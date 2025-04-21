# mocks/__init__.py
import sys
from unittest.mock import MagicMock
from .kafka_mock import MockKafka
from .mqtt_mock import mock_mqtt
from .sqlalchemy_mock import MockSQLAlchemy
from .models_mock import MockBase, MockSensorData, MockAlert
from .utils_mock import (
    process_data_batch,
    calculate_statistics,
    check_thresholds,
    format_message,
    send_alert
)

def setup_mocks():
    # Setup utils mock
    utils_mock = MagicMock()
    utils_mock.process_data_batch = process_data_batch
    utils_mock.calculate_statistics = calculate_statistics
    utils_mock.check_thresholds = check_thresholds
    utils_mock.format_message = format_message
    utils_mock.send_alert = send_alert
    sys.modules["utils"] = utils_mock

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