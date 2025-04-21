import json
import logging
import os
import requests
from kafka import KafkaConsumer
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "iot.sensor.data"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATABASE_URL = 'postgresql://user:password@postgres_db:5432/sensors'

ALERT_THRESHOLDS = {
    "temperature": 30,
    "humidity": 80,
}

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='alerts-service-group'
)

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=False)
    sensor_type = Column(String, nullable=False)
    parameter = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logger.warning(f"Failed to send alert to Telegram: {response.text}")
    except Exception as e:
        logger.error(f"Error sending Telegram alert: {e}")


def check_alerts(data: dict):
    sensor_id = data.get("sensor_id")
    sensor_type = data.get("sensor_type")
    timestamp_raw = data.get("timestamp")
    timestamp = datetime.fromtimestamp(timestamp_raw) if timestamp_raw else datetime.utcnow()
    readings = data.get("data", {})

    for key, threshold in ALERT_THRESHOLDS.items():
        if key in readings and readings[key] > threshold:
            value = readings[key]
            message = (
                f"🚨 *ALERT*\n"
                f"Sensor #{sensor_id} ({sensor_type})\n"
                f"{key.capitalize()}: {value} > {threshold}\n"
                f"Time: {timestamp.isoformat()}"
            )
            logger.info(message)
            send_telegram_alert(message)

            session = SessionLocal()
            alert = Alert(
                sensor_id=sensor_id,
                sensor_type=sensor_type,
                parameter=key,
                value=value,
                threshold=threshold,
                timestamp=timestamp
            )
            session.add(alert)
            session.commit()
            session.close()


def process_messages():
    logger.info("Alert service started. Listening for messages...")
    for message in consumer:
        check_alerts(message.value)


if __name__ == '__main__':
    process_messages()
