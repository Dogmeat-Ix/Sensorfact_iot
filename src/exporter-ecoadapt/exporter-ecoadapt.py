#!/usr/bin/env python3
"""
A minimal EcoAdapt modbus reader.
Reads voltage and frequency periodically and sends them via WebSocket.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone

from sensor_factory import create_sensor
from ws_client import create_ws_factory

# configure the client logging
FORMAT = (
    "%(asctime)-15s %(threadName)-15s "
    "%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

INTERVAL = 5  # seconds between reads
WS_URL = "ws://127.0.0.1:9000"


def setup_sensor():
    """Create and connect a sensor, falling back to mock if unavailable."""
    sensor = create_sensor()
    try:
        sensor.connect()
    except Exception as e:
        log.warning("Sensor unavailable (%s), falling back to mock" % e)
        sensor = create_sensor("mock")
        sensor.connect()
    return sensor


async def read_loop(sensor, ws_factory, interval):
    """Periodically read sensor data and send via WebSocket."""
    log.info("Starting periodic reads (interval=%ds)" % interval)
    # Yield once to let the event loop complete the WebSocket handshake
    await asyncio.sleep(0.1)
    try:
        while True:
            reading = sensor.read()
            payload = json.dumps({
                "timestamp": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                "voltage": reading["voltage"],
                "frequency": reading["frequency"],
            })
            log.info("Sending: %s" % payload)
            protocol = ws_factory.ws_protocol if ws_factory else None
            if protocol and protocol.state == protocol.STATE_OPEN:
                protocol.sendMessage(payload.encode("utf-8"))
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    finally:
        log.info("Shutting down")
        sensor.close()


def run_sync_client():
    sensor = setup_sensor()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Connect WebSocket
    ws_factory = create_ws_factory(WS_URL)
    try:
        coro = loop.create_connection(ws_factory, "127.0.0.1", 9000)
        loop.run_until_complete(coro)
        log.info("WebSocket TCP connected to %s" % WS_URL)
    except Exception as e:
        log.warning("WebSocket unavailable (%s), will only log readings" % e)
        ws_factory = None

    try:
        loop.run_until_complete(read_loop(sensor, ws_factory, INTERVAL))
    except KeyboardInterrupt:
        log.info("Stopped by user")


if __name__ == "__main__":
    run_sync_client()