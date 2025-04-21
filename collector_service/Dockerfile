FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV MQTT_BROKER=mosquitto
ENV MQTT_PORT=1883
ENV MQTT_TOPIC=sensor/data
ENV KAFKA_BROKER=kafka:9092
ENV KAFKA_TOPIC=iot.sensor.data

CMD ["python", "bridge.py"]
