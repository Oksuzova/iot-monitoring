from unittest.mock import MagicMock


class MockEngine:
    def connect(self):
        return MagicMock()

    def begin(self):
        return MagicMock()

    def raw_connection(self):
        return MagicMock()


class MockSQLAlchemy:
    def create_engine(self, *args, **kwargs):
        return MockEngine()

    Column = MagicMock()
    Integer = MagicMock()
    Float = MagicMock()
    String = MagicMock()
    DateTime = MagicMock()
    ForeignKey = MagicMock()
    create_engine = MagicMock(return_value=MockEngine())