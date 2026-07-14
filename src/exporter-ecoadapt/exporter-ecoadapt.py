#!/usr/bin/env python3
"""
A minimal EcoAdapt modbus reader.
Reads voltage and frequency periodically and logs them.
"""

import asyncio
import logging

from sensor_factory import create_sensor

# configure the client logging
FORMAT = (
    "%(asctime)-15s %(threadName)-15s "
    "%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

INTERVAL = 5  # seconds between reads


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


async def read_loop(sensor, interval):
    """Periodically read sensor data until cancelled."""
    log.info("Starting periodic reads (interval=%ds)" % interval)
    try:
        while True:
            reading = sensor.read()
            log.info("Voltage: %.2f V | Frequency: %.2f Hz" % (
                reading["voltage"], reading["frequency"]
            ))
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    finally:
        log.info("Shutting down")
        sensor.close()


def run_sync_client():
    sensor = setup_sensor()
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(read_loop(sensor, INTERVAL))
    except KeyboardInterrupt:
        log.info("Stopped by user")


if __name__ == "__main__":
    run_sync_client()