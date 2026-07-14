#!/usr/bin/env python3
"""
A minimal EcoAdapt modbus reader
"""

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


def run_sync_client():
    sensor = create_sensor()
    try:
        sensor.connect()
    except Exception as e:
        log.warning("Sensor unavailable (%s), falling back to mock" % e)
        sensor = create_sensor("mock")
        sensor.connect()

    reading = sensor.read()
    log.info("Voltage: %.2f V" % reading["voltage"])
    log.info("Frequency: %.2f Hz" % reading["frequency"])
    sensor.close()


if __name__ == "__main__":
    run_sync_client()
