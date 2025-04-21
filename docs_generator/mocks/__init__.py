import sys
from .kafka_mock import MockKafka
from .mqtt_mock import mock_mqtt
from .sqlalchemy_mock import MockSQLAlchemy

def setup_mocks():
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
    sys.modules["sqlalchemy"] = MockSQLAlchemy()
    sys.modules["sqlalchemy.orm"] = MagicMock()
    sys.modules["sqlalchemy.ext"] = MagicMock()
    sys.modules["sqlalchemy.ext.declarative"] = MagicMock()