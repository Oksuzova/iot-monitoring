import logging
import time
import random
import paho.mqtt.client as mqtt
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

BROKER = "localhost"
PORT = 1883
TOPIC = "sensor/data"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)


def generate_temp_hum(sensor):
    return {
        "sensor_id": sensor,
        "sensor_type": "temperature_humidity",
        "data": {
            "temperature": round(random.uniform(20.0, 30.0), 2),
            "humidity": round(random.uniform(40.0, 60.0), 2)
        },
        "timestamp": int(time.time())
    }


def generate_air_quality(sensor):
    return {
        "sensor_id": sensor,
        "sensor_type": "air_quality",
        "data": {
            "co2": round(random.uniform(300.0, 800.0), 2),
            "pm25": round(random.uniform(0.0, 50.0), 2)
        },
        "timestamp": int(time.time())
    }


def generate_trigger_alert(sensor):
    return {
        "sensor_id": sensor,
        "sensor_type": "temperature_humidity",
        "data": {
            "temperature": 35.0,
            "humidity": 50.0
        },
        "timestamp": int(time.time())
    }


sensor_ids = [1, 2, 3]
air_quality_sensors = [4, 5]

last_alert_time = 0

while True:
    for sid in sensor_ids:
        payload = json.dumps(generate_temp_hum(sid))
        client.publish(TOPIC, payload)
        logger.info(f"Published temp/hum sensor {sid}: {payload}")
        time.sleep(1)

    for sid in air_quality_sensors:
        payload = json.dumps(generate_air_quality(sid))
        client.publish(TOPIC, payload)
        logger.info(f"Published air quality sensor {sid}: {payload}")
        time.sleep(1)

    now = time.time()
    if now - last_alert_time > 10:
        alert_sensor_id = random.choice(sensor_ids)
        alert_payload = json.dumps(generate_trigger_alert(alert_sensor_id))
        client.publish(TOPIC, alert_payload)
        logger.info(f"Published ALERT TRIGGER from sensor {alert_sensor_id}: {alert_payload}")
        last_alert_time = now

    time.sleep(3)
