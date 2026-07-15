import sys
import unittest

sys.path.insert(0, "src/exporter-ecoadapt")

from sensors.ecoadapt_sensor import decode_float


class TestDecodeFloat(unittest.TestCase):
    """Tests for decode_float utility."""

    def test_decode_voltage(self):
        """Known register pair decodes to ~238.76 V."""
        result = decode_float(49709, 17262)
        self.assertAlmostEqual(result, 238.76, places=1)

    def test_decode_frequency(self):
        """Known register pair decodes to ~51.46 Hz."""
        result = decode_float(54339, 16973)
        self.assertAlmostEqual(result, 51.46, places=1)

    def test_decode_zero(self):
        """Zero registers decode to 0.0."""
        result = decode_float(0, 0)
        self.assertEqual(result, 0.0)

    def test_decode_nan(self):
        """NaN register pattern decodes to NaN."""
        import math
        result = decode_float(0x0000, 0x7FC0)  # quiet NaN
        self.assertTrue(math.isnan(result))


if __name__ == "__main__":
    unittest.main()
