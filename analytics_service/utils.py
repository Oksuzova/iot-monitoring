import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from models import TimeWindowStats, AggregatedStats


def convert_numpy_types(value):
    """Convert numpy data types to native Python types.

    Args:
        value: Value to convert, can be numpy integer, float, or ndarray.

    Returns:
        Converted value in native Python type (int, float, or list).
    """
    if isinstance(value, np.integer):
        return int(value)
    elif isinstance(value, np.floating):
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    return value


def calculate_advanced_stats(values):
    """Calculate statistical metrics for a set of numerical values.

    Args:
        values: List of numerical values to analyze.

    Returns:
        dict: Statistical metrics including count, average, min, max, median,
              standard deviation, quartiles, variance, and original values.
        None: If input list is empty.
    """
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
    """Save statistical data for different time windows (1-minute and 5-minute).

    Args:
        db: Database session object.
        sensor_id: ID of the sensor.
        current_stats: Dictionary containing current statistical data.
    """
    now = datetime.utcnow()
    sensor_id = int(sensor_id)
    stats = {k: convert_numpy_types(v) for k, v in current_stats.items()}

    minute_start = now.replace(second=0, microsecond=0)
    minute_stats = TimeWindowStats(
        sensor_id=sensor_id,
        window_type='minute',
        window_start=minute_start,
        window_end=minute_start + timedelta(minutes=1),
        message_count=stats['count'],
        avg_value=stats['avg'],
        min_value=stats['min'],
        max_value=stats['max'],
        trend=0.0
    )
    db.add(minute_stats)

    five_min_start = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0)
    minute_records = db.query(TimeWindowStats).filter(
        TimeWindowStats.sensor_id == sensor_id,
        TimeWindowStats.window_type == 'minute',
        TimeWindowStats.window_start >= five_min_start
    ).all()

    if minute_records:
        counts = [int(s.message_count) for s in minute_records]
        avgs = [float(s.avg_value) for s in minute_records]
        mins = [float(s.min_value) for s in minute_records]
        maxs = [float(s.max_value) for s in minute_records]

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


def process_data_batch(db, message_buffer, logger):
    """Process a batch of sensor messages and calculate statistics.

    Args:
        db: Database session object.
        message_buffer: List of sensor messages to process.
        logger: Logger object for recording processing information.
    """
    df = pd.DataFrame(message_buffer)
    data_expanded = df['data'].apply(pd.Series)
    df_expanded = pd.concat([df[['sensor_id', 'sensor_type']], data_expanded], axis=1)

    for (sensor_id, sensor_type), group in df_expanded.groupby(['sensor_id', 'sensor_type']):
        numeric_cols = group.select_dtypes(include='number').columns
        for field in numeric_cols:
            process_sensor_data(db, sensor_id, sensor_type, group[field].dropna().values, logger)


def process_sensor_data(db, sensor_id, sensor_type, values, logger):
    """Process numerical data for a specific sensor and save statistics.

    Args:
        db: Database session object.
        sensor_id: ID of the sensor.
        sensor_type: Type of the sensor.
        values: Numerical values to process.
        logger: Logger object for recording processing information.
    """
    native_values = [float(v) for v in values if pd.notnull(v)]
    if not native_values:
        return

    stats = calculate_advanced_stats(native_values)
    if not stats:
        return

    converted_stats = {k: convert_numpy_types(v) for k, v in stats.items()}

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