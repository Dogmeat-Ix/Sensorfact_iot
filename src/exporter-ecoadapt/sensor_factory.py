from sensors.ecoadapt_sensor import EcoAdaptSensor
from sensors.mock_sensor import MockSensor


def create_sensor(sensor_type="ecoadapt", **kwargs):
    if sensor_type == "mock":
        return MockSensor()
    return EcoAdaptSensor(**kwargs)
