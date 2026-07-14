import logging
import struct

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

from .base_sensor import BaseSensor

log = logging.getLogger(__name__)


def decode_float(low_word, high_word):
    """Decode IEEE 754 float from two 16-bit registers (swapped word order)."""
    return struct.unpack(">f", struct.pack(">HH", high_word, low_word))[0]


class EcoAdaptSensor(BaseSensor):
    """Reads voltage and frequency from an EcoAdapt PE6 via ModBus TCP."""

    DEFAULT_ADDRESS = "169.254.20.1"
    DEFAULT_PORT = 502
    DEFAULT_UNIT_ID = 0x1

    def __init__(self, address=DEFAULT_ADDRESS, port=DEFAULT_PORT, unit_id=DEFAULT_UNIT_ID):
        self._address = address
        self._port = port
        self._unit_id = unit_id
        self._client = None

    def connect(self):
        self._client = ModbusClient(self._address, port=self._port)
        if not self._client.connect():
            raise ConnectionError(
                "Failed to connect to %s:%d" % (self._address, self._port)
            )
        log.info("Connected to sensor at %s" % self._address)

    def read(self):
        voltage_resp = self._client.read_input_registers(352, 2, unit=self._unit_id)
        frequency_resp = self._client.read_input_registers(424, 2, unit=self._unit_id)
        return {
            "voltage": decode_float(voltage_resp.registers[0], voltage_resp.registers[1]),
            "frequency": decode_float(frequency_resp.registers[0], frequency_resp.registers[1]),
        }

    def close(self):
        if self._client:
            self._client.close()
            log.info("Disconnected from sensor")


# Raw register output from real device (2021-03-19) for reference:
# (0, 1):   [514]
# (1, 1):   [2]
# (2, 3):   [30, 44285, 17639]
# (244, 12): [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# (352, 12): [49709, 17262, 20887, 15905, 45177, 15748, 0, 0, 0, 0, 0, 0]
# (388, 12): [34030, 17262, 13400, 15907, 22707, 15748, 0, 0, 0, 0, 0, 0]
# (424, 12): [54339, 16973, 54339, 16973, 43051, 16949, 0, 0, 0, 0, 0, 0]
#
# Decoded (swapped word order: high_word=reg[1], low_word=reg[0]):
#   Register 352 -> 238.76 V  (Phase 1 voltage)
#   Register 388 -> 238.52 V  (Phase 2 voltage)
#   Register 424 ->  51.46 Hz (Phase 1 frequency)
