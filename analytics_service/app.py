import json
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from kafka import KafkaConsumer
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'iot.sensor.data'
BUFFER_SIZE = 200
WINDOW_SIZE = 20
DATABASE_URL = 'postgresql://user:password@postgres_db:5432/sensors'

Base = declarative_base()


def convert_numpy_types(value):
    if isinstance(value, np.integer):
        return int(value)
    elif isinstance(value, np.floating):
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    return value


class AggregatedStats(Base):
    __tablename__ = 'aggregated_stats'
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer)
    sensor_type = Column(String)
    timestamp = Column(DateTime)
    window_size = Column(Integer)

    message_count = Column(Integer)
    avg_value = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)

    median = Column(Float)
    std_dev = Column(Float)
    q25 = Column(Float)
    q75 = Column(Float)
    variance = Column(Float)
    data_points = Column(JSON)


class TimeWindowStats(Base):
    __tablename__ = 'time_window_stats'
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer)
    window_type = Column(String)
    window_start = Column(DateTime)
    window_end = Column(DateTime)

    message_count = Column(Integer)
    avg_value = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)
    trend = Column(Float)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(engine)
logger.info("Database tables created.")


def calculate_advanced_stats(values):
    if len(values) == 0:
        return None

    return {
        'count': int(len(values)),
        'avg': float(np.mean(values)),
        'min': float(np.min(values)),
        'max': float(np.max(values)),
        'median': float(np.median(values)),
        'std': float(np.std(values)),
        'q25': float(np.percentile(values, 25)),
        'q75': float(np.percentile(values, 75)),
        'variance': float(np.var(values)),
        'values': [float(v) for v in values]
    }


def save_time_window_stats(db, sensor_id, current_stats):
    now = datetime.utcnow()

    converted_stats = {
        k: convert_numpy_types(v) for k, v in current_stats.items()
    }

    sensor_id = int(sensor_id)
    minute_start = now.replace(second=0, microsecond=0)

    minute_stats = TimeWindowStats(
        sensor_id=sensor_id,
        window_type='minute',
        window_start=minute_start,
        window_end=minute_start + timedelta(minutes=1),
        message_count=converted_stats['count'],
        avg_value=converted_stats['avg'],
        min_value=converted_stats['min'],
        max_value=converted_stats['max'],
        trend=0.0
    )
    db.add(minute_stats)

    five_min_start = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=(now.minute // 5) * 5
    )

    logger.debug(
        f"sensor_id={sensor_id} ({type(sensor_id)}), window_type='minute', five_min_start={five_min_start} ({type(five_min_start)})")

    last_5min = db.query(TimeWindowStats).filter(
        TimeWindowStats.sensor_id == sensor_id,
        TimeWindowStats.window_type == 'minute',
        TimeWindowStats.window_start >= five_min_start
    ).all()

    if last_5min:
        counts = [int(s.message_count) for s in last_5min]
        avgs = [float(s.avg_value) for s in last_5min]
        mins = [float(s.min_value) for s in last_5min]
        maxs = [float(s.max_value) for s in last_5min]

        five_min_stats = TimeWindowStats(
            sensor_id=sensor_id,
            window_type='5min',
            window_start=five_min_start,
            window_end=five_min_start + timedelta(minutes=5),
            message_count=sum(counts),
            avg_value=float(np.mean(avgs)),
            min_value=min(mins) if mins else 0.0,
            max_value=max(maxs) if maxs else 0.0,
            trend=float(avgs[-1] - avgs[0]) if avgs else 0.0
        )
        db.add(five_min_stats)


def process_sensor_data(db, sensor_id, sensor_type, values):
    native_values = [float(v) for v in values if pd.notnull(v)]

    if not native_values:
        return

    stats = calculate_advanced_stats(native_values)
    if not stats:
        return

    converted_stats = {
        k: convert_numpy_types(v) for k, v in stats.items()
    }

    agg_stats = AggregatedStats(
        sensor_id=int(sensor_id),
        sensor_type=str(sensor_type),
        timestamp=datetime.utcnow(),
        window_size=int(len(native_values)),
        message_count=converted_stats['count'],
        avg_value=converted_stats['avg'],
        min_value=converted_stats['min'],
        max_value=converted_stats['max'],
        median=converted_stats['median'],
        std_dev=converted_stats['std'],
        q25=converted_stats['q25'],
        q75=converted_stats['q75'],
        variance=converted_stats['variance'],
        data_points=converted_stats['values']
    )
    db.add(agg_stats)

    save_time_window_stats(db, sensor_id, converted_stats)

    logger.info(f"Processed {converted_stats['count']} values for sensor {sensor_id}. "
                f"Avg: {converted_stats['avg']:.2f}, Std: {converted_stats['std']:.2f}")


def main():
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
            msg = message.value
            message_buffer.append(msg)

            if len(message_buffer) >= WINDOW_SIZE:
                df = pd.DataFrame(message_buffer)

                data_expanded = df['data'].apply(pd.Series)
                df_expanded = pd.concat([df[['sensor_id', 'sensor_type']], data_expanded], axis=1)

                for (sensor_id, sensor_type), group in df_expanded.groupby(['sensor_id', 'sensor_type']):
                    numeric_cols = group.select_dtypes(include='number').columns
                    for field in numeric_cols:
                        process_sensor_data(db, sensor_id, sensor_type, group[field].dropna().values)

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
