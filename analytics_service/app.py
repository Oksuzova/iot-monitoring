import json
import logging
from kafka import KafkaConsumer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from utils import process_data_batch

"""Analytics service for processing IoT sensor data.

This module implements a Kafka consumer that reads sensor data messages,
buffers them, and processes them in batches. The processed statistics
are stored in a PostgreSQL database.
"""

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Service configuration constants
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'iot.sensor.data'
BUFFER_SIZE = 200
WINDOW_SIZE = 20
DATABASE_URL = 'postgresql://user:password@postgres_db:5432/sensors'

# Initialize database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(engine)
logger.info("Database tables created.")


def main():
    """Main service loop.

    Creates a Kafka consumer to read sensor data messages, processes them in batches,
    and stores statistical results in the database. The service continues running
    until interrupted or an error occurs.

    The function implements:
    - Message buffering for batch processing
    - Database session management
    - Error handling and cleanup
    """
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='stats-aggregator'
    )
    logger.info("Kafka consumer started.")

    message_buffer = []
    db = SessionLocal()

    try:
        for message in consumer:
            message_buffer.append(message.value)

            if len(message_buffer) >= WINDOW_SIZE:
                process_data_batch(db, message_buffer, logger)
                db.commit()
                message_buffer = []

    except Exception as e:
        logger.error(f"Processing error: {e}")
        db.rollback()
    finally:
        consumer.close()
        db.close()
        logger.info("Service stopped.")


if __name__ == "__main__":
    main()