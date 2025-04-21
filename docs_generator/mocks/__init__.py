# mocks/__init__.py
import sys
from unittest.mock import MagicMock
from .kafka_mock import MockKafka
from .mqtt_mock import mock_mqtt
from .sqlalchemy_mock import MockSQLAlchemy
from .models_mock import MockBase, MockSensorData, MockAlert


def setup_mocks():
    # Setup models mock
    models_mock = MagicMock()
    models_mock.Base = MockBase
    models_mock.SensorData = MockSensorData
    models_mock.Alert = MockAlert
    sys.modules["models"] = models_mock

    # Setup Kafka mocks
    sys.modules["kafka"] = MockKafka()
    sys.modules["kafka.consumer"] = MagicMock()
    sys.modules["kafka.consumer.group"] = MagicMock()
    sys.modules["kafka.errors"] = MagicMock()

    # Setup MQTT mocks
    sys.modules["paho"] = mock_mqtt
    sys.modules["paho.mqtt"] = mock_mqtt
    sys.modules["paho.mqtt.client"] = mock_mqtt

    # Setup SQLAlchemy mocks
    mock_sqlalchemy = MockSQLAlchemy()
    sys.modules["sqlalchemy"] = mock_sqlalchemy
    sys.modules["sqlalchemy.orm"] = MagicMock()
    sys.modules["sqlalchemy.ext"] = MagicMock()
    sys.modules["sqlalchemy.ext.declarative"] = MagicMock()
