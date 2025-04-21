from unittest.mock import MagicMock


class MockKafka:
    Consumer = MagicMock()
    KafkaConsumer = MagicMock()
    errors = MagicMock()
