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
    DB_PASSWORD=password

# Create a mock directory structure
RUN mkdir -p /src/alerts_service \
    /src/analytics_service \
    /src/collector_service \
    /src/flask_api

# Copy only the necessary Python files for documentation
COPY alerts_service/*.py /src/alerts_service/
COPY analytics_service/*.py /src/analytics_service/
COPY collector_service/*.py /src/collector_service/
COPY flask_api/*.py /src/flask_api/
COPY sensor_script.py /src/

# Create mock __init__.py files
RUN touch /src/alerts_service/__init__.py \
    /src/analytics_service/__init__.py \
    /src/collector_service/__init__.py \
    /src/flask_api/__init__.py

# Generate documentation
CMD ["pdoc", "-o", "/output", \
     "alerts_service", \
     "analytics_service", \
     "collector_service", \
     "flask_api", \
     "sensor_script.py"]