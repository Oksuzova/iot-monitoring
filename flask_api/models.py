from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=False)
    sensor_type = Column(String, nullable=False)
    parameter = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class SensorData(Base):
    __tablename__ = 'sensor_data'

    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, nullable=False)
    sensor_type = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)


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
