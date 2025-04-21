from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AggregatedStats(Base):
    """SQLAlchemy model for storing aggregated statistical data from sensor readings.

    This class represents a database table that stores comprehensive statistical metrics
    calculated from sensor data over a specific time window.

    Attributes:
        id (int): Primary key for the record.
        sensor_id (int): Identifier of the sensor.
        sensor_type (str): Type/category of the sensor.
        timestamp (datetime): When the statistics were calculated.
        window_size (int): Number of data points in the aggregation window.
        message_count (int): Total number of messages processed.
        avg_value (float): Average of the sensor values.
        min_value (float): Minimum sensor value in the window.
        max_value (float): Maximum sensor value in the window.
        median (float): Median of the sensor values.
        std_dev (float): Standard deviation of the values.
        q25 (float): First quartile (25th percentile).
        q75 (float): Third quartile (75th percentile).
        variance (float): Statistical variance of the values.
        data_points (json): Raw data points used in calculations.
    """
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
    """SQLAlchemy model for storing time-based window statistics from sensor data.

    This class represents a database table that stores statistical metrics
    calculated over specific time windows (e.g., 1-minute, 5-minute intervals).

    Attributes:
        id (int): Primary key for the record.
        sensor_id (int): Identifier of the sensor.
        window_type (str): Type of time window (e.g., 'minute', '5min').
        window_start (datetime): Start time of the aggregation window.
        window_end (datetime): End time of the aggregation window.
        message_count (int): Number of messages in the time window.
        avg_value (float): Average sensor value in the window.
        min_value (float): Minimum sensor value in the window.
        max_value (float): Maximum sensor value in the window.
        trend (float): Calculated trend value (difference between last and first averages).
    """
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