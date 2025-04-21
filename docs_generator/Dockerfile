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

# Create a mock implementation script
RUN echo 'import sys\nfrom unittest.mock import MagicMock\n\nsys.modules["kafka"] = MagicMock()\nsys.modules["kafka.consumer"] = MagicMock()\nsys.modules["kafka.consumer.group"] = MagicMock()\nsys.modules["kafka.errors"] = MagicMock()' > /src/mock_kafka.py

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

# Use a wrapper script to load mocks before running pdoc
RUN echo '#!/bin/python3\nimport mock_kafka\nimport pdoc.__main__\npdoc.__main__.main()' > /src/run_pdoc.py && \
    chmod +x /src/run_pdoc.py

CMD ["python", "/src/run_pdoc.py", "-o", "/output", \
     "alerts_service", \
     "analytics_service", \
     "collector_service", \
     "flask_api", \
     "sensor_script.py"]