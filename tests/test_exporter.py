import asyncio
import json
import sys
import unittest

sys.path.insert(0, "src/exporter-ecoadapt")

from sensors.mock_sensor import MockSensor


def _get_one_reading():
    """Run the producer once and return the queued reading."""
    from importlib import import_module
    exporter = import_module("exporter-ecoadapt")

    sensor = MockSensor()
    sensor.connect()
    queue = asyncio.Queue()

    async def _run():
        task = asyncio.ensure_future(
            exporter.get_sensor_data(sensor, queue, interval=10)
        )
        reading = await asyncio.wait_for(queue.get(), timeout=2)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        return reading

    return asyncio.run(_run())


class TestSensorReadingShape(unittest.TestCase):
    """The queued message contains the expected fields."""

    def setUp(self):
        self.reading = _get_one_reading()

    def test_has_voltage(self):
        self.assertIsInstance(self.reading["voltage"], float)

    def test_has_frequency(self):
        self.assertIsInstance(self.reading["frequency"], float)

    def test_has_timestamp(self):
        self.assertIsInstance(self.reading["timestamp"], str)
        self.assertIn("T", self.reading["timestamp"])


class TestSensorReadingValues(unittest.TestCase):
    """Given mock sensor values, JSON payload has correct data."""

    def setUp(self):
        self.payload = json.loads(json.dumps(_get_one_reading()))

    def test_voltage_value(self):
        self.assertAlmostEqual(self.payload["voltage"], 238.76, places=1)

    def test_frequency_value(self):
        self.assertAlmostEqual(self.payload["frequency"], 51.46, places=1)


if __name__ == "__main__":
    unittest.main()
