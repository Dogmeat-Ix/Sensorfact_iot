import logging

from .base_sensor import BaseSensor
from .ecoadapt_sensor import decode_float

log = logging.getLogger(__name__)


class MockSensor(BaseSensor):
    """Returns hardcoded values from a real PE6 capture."""

    def connect(self):
        log.info("MockSensor connected (no hardware)")

    def read(self):
        return {
            "voltage": decode_float(49709, 17262),    # 238.76 V
            "frequency": decode_float(54339, 16973),  # 51.46 Hz
        }

    def close(self):
        log.info("MockSensor disconnected")
