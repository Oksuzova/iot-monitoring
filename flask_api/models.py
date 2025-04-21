"""SQLAlchemy models for IoT sensor data storage.

This module defines the database schema for storing sensor alerts, raw data,
and various statistical aggregations using SQLAlchemy ORM.
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Alert(Base):
    """Model for storing sensor alert events.

    Represents threshold violation events from sensors with associated
    metadata and measured values.

    Attributes:
        id (int): Primary key
        sensor_id (int): ID of the sensor that generated the alert
        sensor_type (str): Type/model of the sensor
        parameter (str): Measured parameter that triggered the alert
        value (float): Actual measured value
        threshold (float): Threshold value that was exceeded
        timestamp (datetime): When the alert was generated (UTC)
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=False)
    sensor_type = Column(String, nullable=False)
    parameter = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class SensorData(Base):
    """Model for storing raw sensor measurements.

    Stores individual sensor readings with their associated metadata
    and measurement data.

    Attributes:
        id (int): Primary key
        sensor_id (int): ID of the sensor
        sensor_type (str): Type/model of the sensor
        timestamp (int): Unix timestamp of the measurement
        data (dict): JSON object containing the actual measurements
    """
    __tablename__ = 'sensor_data'

    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, nullable=False)
    sensor_type = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)


class AggregatedStats(Base):
    """Model for storing statistical aggregations of sensor data.

    Stores various statistical metrics calculated over specified time windows
    for each sensor.

    Attributes:
        id (int): Primary key
        sensor_id (int): ID of the sensor
        sensor_type (str): Type/model of the sensor
        timestamp (datetime): When the aggregation was computed
        window_size (int): Size of the aggregation window in seconds
        message_count (int): Number of measurements in the window
        avg_value (float): Mean value
        min_value (float): Minimum value
        max_value (float): Maximum value
        median (float): Median value
        std_dev (float): Standard deviation
        q25 (float): First quartile (25th percentile)
        q75 (float): Third quartile (75th percentile)
        variance (float): Statistical variance
        data_points (dict): JSON array of raw data points used
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
    """Model for storing time-based window statistics.

    Stores basic statistical metrics for fixed time windows (hourly, daily, etc.)
    along with trend analysis.

    Attributes:
        id (int): Primary key
        sensor_id (int): ID of the sensor
        window_type (str): Type of time window (e.g., 'hourly', 'daily')
        window_start (datetime): Start time of the window
        window_end (datetime): End time of the window
        message_count (int): Number of measurements in the window
        avg_value (float): Mean value
        min_value (float): Minimum value
        max_value (float): Maximum value
        trend (float): Calculated trend coefficient
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