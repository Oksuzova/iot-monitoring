FROM python:3.11-slim

WORKDIR /src

# Install required packages
RUN pip install --no-cache-dir \
    pdoc \
    requests \
    kafka-python \
    pandas \
    SQLAlchemy \
    psycopg2-binary \
    python-dotenv

# Create comprehensive mock modules script
RUN echo 'import sys\nfrom unittest.mock import MagicMock\n\n\
# Mock Kafka\n\
class MockKafka:\n\
    Consumer = MagicMock()\n\
    KafkaConsumer = MagicMock()\n\
    errors = MagicMock()\n\
\n\
sys.modules["kafka"] = MockKafka()\n\
sys.modules["kafka.consumer"] = MagicMock()\n\
sys.modules["kafka.consumer.group"] = MagicMock()\n\
sys.modules["kafka.errors"] = MagicMock()\n\
\n\
# Mock MQTT\n\
sys.modules["paho"] = MagicMock()\n\
sys.modules["paho.mqtt"] = MagicMock()\n\
sys.modules["paho.mqtt.client"] = MagicMock()\n\
\n\
# Mock SQLAlchemy\n\
class MockEngine:\n\
    def connect(self):\n\
        return MagicMock()\n\
    def begin(self):\n\
        return MagicMock()\n\
    def raw_connection(self):\n\
        return MagicMock()\n\
\n\
class MockSQLAlchemy:\n\
    def create_engine(self, *args, **kwargs):\n\
        return MockEngine()\n\
    Column = MagicMock()\n\
    Integer = MagicMock()\n\
    Float = MagicMock()\n\
    String = MagicMock()\n\
    DateTime = MagicMock()\n\
    ForeignKey = MagicMock()\n\
    create_engine = MagicMock(return_value=MockEngine())\n\
\n\
sys.modules["sqlalchemy"] = MockSQLAlchemy()\n\
sys.modules["sqlalchemy.orm"] = MagicMock()\n\
sys.modules["sqlalchemy.ext"] = MagicMock()\n\
sys.modules["sqlalchemy.ext.declarative"] = MagicMock()' > /src/mock_modules.py

# Create mock environment variables
ENV KAFKA_BROKER=localhost:9092 \
    MQTT_BROKER=localhost \
    MQTT_PORT=1883 \
    MQTT_TOPIC=sensor/data \
    KAFKA_TOPIC=iot.sensor.data \
    DB_HOST=localhost \
    DB_PORT=5432 \
    DB_NAME=sensors \
    DB_USER=user \
    DB_PASSWORD=password \
    PYTHONPATH=/src

# Create directory structure and copy files
RUN mkdir -p /src/alerts_service \
    /src/analytics_service \
    /src/collector_service \
    /src/flask_api

COPY alerts_service/*.py /src/alerts_service/
COPY analytics_service/*.py /src/analytics_service/
COPY collector_service/*.py /src/collector_service/
COPY flask_api/*.py /src/flask_api/
COPY sensor_script.py /src/

RUN touch /src/alerts_service/__init__.py \
    /src/analytics_service/__init__.py \
    /src/collector_service/__init__.py \
    /src/flask_api/__init__.py

# Create wrapper script
RUN echo '#!/bin/python3\n\
import mock_modules\n\
import os\n\
import sys\n\
import pdoc\n\
\n\
modules = [\n\
    "alerts_service",\n\
    "analytics_service",\n\
    "collector_service",\n\
    "flask_api",\n\
    "sensor_script"\n\
]\n\
\n\
for module in modules:\n\
    pdoc.render.configure(docformat="google")\n\
    doc = pdoc.pdoc(module)\n\
    output_file = os.path.join("/output", f"{module}.html")\n\
    with open(output_file, "w", encoding="utf-8") as f:\n\
        f.write(doc)' > /src/run_pdoc.py && \
    chmod +x /src/run_pdoc.py

CMD ["python", "/src/run_pdoc.py"]