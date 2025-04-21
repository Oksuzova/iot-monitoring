"""IoT Sensor Alerts Service.

This module implements a service that monitors IoT sensor data from Kafka
and triggers alerts when measurements exceed predefined thresholds.
Alerts are sent via Telegram and stored in a PostgreSQL database.

Environment Variables:
    BOT_TOKEN: Telegram bot authentication token
    CHAT_ID: Telegram chat ID where alerts will be sent

Dependencies:
    - kafka-python: For consuming sensor data from Kafka
    - sqlalchemy: For database operations
    - python-dotenv: For loading environment variables
    - requests: For sending Telegram API requests
"""

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

# Configure logging with timestamp and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Service configuration constants
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "iot.sensor.data"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATABASE_URL = 'postgresql://user:password@postgres_db:5432/sensors'

# Alert thresholds for different sensor parameters
ALERT_THRESHOLDS = {
    "temperature": 30,  # Temperature threshold in Celsius
    "humidity": 80,    # Humidity threshold in percent
}

# Initialize Kafka consumer with JSON deserialization
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='alerts-service-group'
)

# Initialize SQLAlchemy
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Alert(Base):
    """SQLAlchemy model representing an alert record in the database.

    This model stores information about sensor alerts that are triggered when
    readings exceed predefined thresholds.

    Attributes:
        id (int): Primary key for the alert record.
        sensor_id (int): Identifier of the sensor that triggered the alert.
        sensor_type (str): Type of the sensor (e.g., 'DHT22', 'BME280').
        parameter (str): The measured parameter that triggered the alert (e.g., 'temperature', 'humidity').
        value (float): The actual value that triggered the alert.
        threshold (float): The threshold value that was exceeded.
        timestamp (datetime): When the alert was generated (defaults to UTC now).

    Note:
        The timestamp field automatically defaults to the current UTC time when
        a new record is created if no timestamp is provided.
    """
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
    """Send an alert message to a Telegram chat using the Telegram Bot API.

    Args:
        message (str): The message to send to the Telegram chat.
            The message can contain Markdown formatting.

    Note:
        This function uses the BOT_TOKEN and CHAT_ID environment variables
        for authentication and message routing.

    Raises:
        requests.exceptions.RequestException: If the HTTP request to Telegram fails.
    """
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
    """Process sensor data and generate alerts when thresholds are exceeded.

    Args:
        data (dict): A dictionary containing sensor data with the following structure:
            {
                "sensor_id": int,      # Unique identifier of the sensor
                "sensor_type": str,     # Type of the sensor (e.g., "DHT22")
                "timestamp": float,     # Unix timestamp of the reading
                "data": {              # Dictionary of sensor readings
                    "temperature": float,
                    "humidity": float,
                    ...
                }
            }

    Note:
        The function uses the global ALERT_THRESHOLDS dictionary to determine
        when to trigger alerts. The thresholds are compared against the values
        in the data["data"] dictionary.

    Side Effects:
        - Sends alerts via Telegram if thresholds are exceeded
        - Creates alert records in the database
        - Logs alert information
    """
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
    """Process incoming messages from the Kafka consumer.

    This function runs an infinite loop that consumes messages from a Kafka topic
    and processes each message through the alert checking system. Each message
    is expected to contain sensor data that will be validated against defined
    thresholds.

    The function will continue running until the program is terminated or an
    unhandled exception occurs.

    Note:
        This is the main service loop and should be run as the primary entry point
        of the application.
    """
    logger.info("Alert service started. Listening for messages...")
    for message in consumer:
        check_alerts(message.value)


if __name__ == '__main__':
    process_messages()