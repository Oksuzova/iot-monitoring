"""Kafka consumer module for IoT sensor data processing.

This module implements a Kafka consumer that reads sensor data messages and
stores them in a PostgreSQL database. It handles connection retries and
prevents duplicate entries based on sensor ID and timestamp.

Dependencies:
    - kafka-python: For Kafka consumer functionality
    - models: For database model definitions
    - db: For database session management
"""

import logging
import os
import json
import time
from kafka import KafkaConsumer
from models import SensorData
from db import SessionLocal

# Configure logging with timestamp and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Kafka connection settings with environment variable fallbacks
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "iot.sensor.data")


def consume_kafka():
    """Consume and process messages from Kafka topic.

    This function establishes a connection to Kafka broker with retry mechanism,
    reads messages from the configured topic, and stores them in the database.
    It implements deduplication based on sensor ID and timestamp.

    The consumer is configured to:
        - Read from the latest offset
        - Deserialize JSON messages
        - Use a specific consumer group for the Flask API

    Note:
        This function runs indefinitely and should be executed in a separate thread.
    """
    logger.info("[Kafka] Starting consumer...")
    consumer = None
    while not consumer:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                group_id="flask-api-consumer",
                auto_offset_reset="latest"
            )
            logger.info("[Kafka] Connected.")
        except Exception as e:
            logger.error(f"[Kafka] Retry in 5s: {e}")
            time.sleep(5)

    session = SessionLocal()
    for msg in consumer:
        payload = msg.value
        try:
            existing = session.query(SensorData).filter_by(
                sensor_id=payload["sensor_id"],
                timestamp=payload["timestamp"]
            ).first()

            if not existing:
                entry = SensorData(
                    sensor_id=payload["sensor_id"],
                    sensor_type=payload["sensor_type"],
                    timestamp=payload["timestamp"],
                    data=payload["data"]
                )
                session.add(entry)
                session.commit()
                logger.info(f"[Kafka] Saved: {payload}")
            else:
                logger.warning(f"[Kafka] Duplicate skipped: {payload['sensor_id']}, ts={payload['timestamp']}")
        except Exception as e:
            logger.error(f"[Kafka] Error: {e}")
    session.close()