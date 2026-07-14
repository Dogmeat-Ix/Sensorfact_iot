#!/usr/bin/env python3
import asyncio
import json
import logging
from datetime import datetime, timezone

from sensor_factory import create_sensor
from ws_client import create_ws_factory

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
FORMAT = (
    "%(asctime)-15s %(threadName)-15s "
    "%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

INTERVAL = 5  # seconds between reads
WS_URL = "ws://127.0.0.1:9000"


# ---------------------------------------------------------------------------
# Sensor setup
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Async pipeline (producer / consumer)
# ---------------------------------------------------------------------------
async def get_sensor_data(sensor, sensor_data_queue, interval):
    """Read sensor data periodically and enqueue readings."""
    log.info("get_sensor_data started (interval=%ds)" % interval)
    try:
        while True:
            reading = sensor.read()
            reading["timestamp"] = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            sensor_data_queue.put_nowait(reading)
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    finally:
        sensor.close()


async def send_sensor_data(sensor_data_queue, ws_factory):
    """Dequeue readings and send them over WebSocket."""
    log.info("send_sensor_data started")
    try:
        while True:
            reading = await sensor_data_queue.get()
            payload = json.dumps(reading)
            log.info("Sending: %s" % payload)
            protocol = ws_factory.ws_protocol if ws_factory else None
            if protocol and protocol.state == protocol.STATE_OPEN:
                protocol.sendMessage(payload.encode("utf-8"))
    except asyncio.CancelledError:
        pass


async def run_exporter(sensor, ws_factory):
    """Run producer and consumer concurrently."""
    sensor_data_queue = asyncio.Queue()
    # Let the WebSocket handshake complete before consuming
    await asyncio.sleep(0.1)
    getter = asyncio.ensure_future(get_sensor_data(sensor, sensor_data_queue, INTERVAL))
    sender = asyncio.ensure_future(send_sensor_data(sensor_data_queue, ws_factory))
    try:
        await asyncio.gather(getter, sender)
    except asyncio.CancelledError:
        getter.cancel()
        sender.cancel()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
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
        loop.run_until_complete(run_exporter(sensor, ws_factory))
    except KeyboardInterrupt:
        log.info("Stopped by user")


if __name__ == "__main__":
    run_sync_client()