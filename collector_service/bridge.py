import json
import paho.mqtt.client as mqtt
from kafka import KafkaProducer

MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"

KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "iot.sensor.data"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    print("[Bridge] Received from MQTT:", payload)
    producer.send(KAFKA_TOPIC, payload)


client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)
print("[Bridge] Listening MQTT and forwarding to Kafka...")
client.loop_forever()
