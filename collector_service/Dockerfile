# Use Python 3.9 slim base image as the base for the collector service
# The slim variant provides a minimal image while maintaining Python functionality
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
# This step is separated to leverage Docker layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service source code into the container
COPY . /app

# Configure environment variables for service connections
# MQTT broker connection settings
ENV MQTT_BROKER=mosquitto
ENV MQTT_PORT=1883
ENV MQTT_TOPIC=sensor/data

# Kafka connection settings
ENV KAFKA_BROKER=kafka:9092
ENV KAFKA_TOPIC=iot.sensor.data

# Start the bridge service using the Python interpreter
# The bridge.py script implements the MQTT to Kafka message forwarding
CMD ["python", "bridge.py"]