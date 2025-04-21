from unittest.mock import MagicMock


class MockBase:
    metadata = MagicMock()
    __table__ = MagicMock()
    query = MagicMock()

    @staticmethod
    def create_all(*args, **kwargs):
        pass


# Mock model classes
class MockSensorData(MockBase):
    id = MagicMock()
    timestamp = MagicMock()
    sensor_id = MagicMock()
    temperature = MagicMock()
    humidity = MagicMock()
    pressure = MagicMock()


class MockAlert(MockBase):
    id = MagicMock()
    timestamp = MagicMock()
    sensor_id = MagicMock()
    alert_type = MagicMock()
    message = MagicMock()
