"""IoT Data Bridge Service.

This module implements a bridge between MQTT and Kafka messaging systems.
It subscribes to sensor data from an MQTT broker and forwards the messages
to a Kafka topic for further processing.

Dependencies:
    - paho-mqtt: For MQTT client functionality
    - kafka-python: For Kafka producer operations
"""

import json
import logging

import paho.mqtt.client as mqtt
from kafka import KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# MQTT connection settings
MQTT_BROKER = "mosquitto"  # MQTT broker hostname
MQTT_PORT = 1883          # Default MQTT port
MQTT_TOPIC = "sensor/data"  # Topic to subscribe for sensor data

# Kafka connection settings
KAFKA_BROKER = "kafka:9092"  # Kafka broker address
KAFKA_TOPIC = "iot.sensor.data"  # Target topic for sensor data

# Initialize Kafka producer with JSON serialization
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def on_message(client, userdata, msg):
    """Handle incoming MQTT messages and forward them to Kafka.

    This callback function is triggered whenever a message is received on the
    subscribed MQTT topic. It decodes the JSON payload and forwards it to
    the configured Kafka topic.

    Args:
        client: The MQTT client instance.
        userdata: User data of any type (set on client initialization).
        msg: The MQTTMessage object containing the payload.

    Note:
        The function assumes the MQTT payload is JSON-encoded and can be parsed.
    """
    payload = json.loads(msg.payload.decode())
    logger.info("[Bridge] Received from MQTT:", payload)
    producer.send(KAFKA_TOPIC, payload)


# Initialize and configure MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)  # 60 seconds keepalive
client.subscribe(MQTT_TOPIC)
logger.info("[Bridge] Listening MQTT and forwarding to Kafka...")
client.loop_forever()  # Start the MQTT client loop
