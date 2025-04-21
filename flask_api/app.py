"""IoT Sensor Data API Service.

This module implements a Flask-based REST API for accessing IoT sensor data,
alerts, and statistical aggregations. It also serves web-based dashboards
for data visualization.

The API provides endpoints for:
- Raw sensor data retrieval
- Alert history and filtering
- Aggregated statistics
- Time-window based statistics
"""

from flask import Flask, jsonify, request
from db import init_db, SessionLocal
from kafka_consumer import consume_kafka
from models import SensorData, AggregatedStats, TimeWindowStats, Alert
import threading
from datetime import datetime
from flask import render_template

app = Flask(__name__)
init_db()

@app.route("/")
def dashboard():
    """Render the main dashboard page.

    Returns:
        str: Rendered HTML template for the main dashboard.
    """
    return render_template("dashboard.html")


@app.route("/alerts-ui")
def alerts_ui():
    """Render the alerts dashboard page.

    Returns:
        str: Rendered HTML template for the alerts dashboard.
    """
    return render_template("alerts.html")


@app.route("/temperature-ui")
def temperature_ui():
    """Render the temperature data dashboard page.

    Returns:
        str: Rendered HTML template for temperature visualization.
    """
    return render_template("temperature_data.html")


@app.route("/humidity-ui")
def humidity_ui():
    """Render the humidity data dashboard page.

    Returns:
        str: Rendered HTML template for humidity visualization.
    """
    return render_template("humidity_data.html")


@app.route("/co2-ui")
def co2_ui():
    """Render the CO2 data dashboard page.

    Returns:
        str: Rendered HTML template for CO2 visualization.
    """
    return render_template("air_co2_data.html")


@app.route("/pm25-ui")
def pm25_ui():
    """Render the PM2.5 data dashboard page.

    Returns:
        str: Rendered HTML template for PM2.5 visualization.
    """
    return render_template("pm25_data.html")


@app.route("/api/alerts")
def get_alerts():
    """Retrieve alert history with optional filtering.

    Query Parameters:
        limit (int): Maximum number of alerts to return (default: 50)
        sensor_id (str): Filter by sensor ID
        sensor_type (str): Filter by sensor type
        parameter (str): Filter by measured parameter
        from (str): ISO format timestamp for start of time range
        to (str): ISO format timestamp for end of time range

    Returns:
        flask.Response: JSON array of alert records
    """
    session = SessionLocal()
    limit = int(request.args.get("limit", 50))
    sensor_id = request.args.get("sensor_id")
    sensor_type = request.args.get("sensor_type")
    parameter = request.args.get("parameter")
    from_ts = request.args.get("from")
    to_ts = request.args.get("to")

    query = session.query(Alert)

    if sensor_type:
        query = query.filter(Alert.sensor_type == sensor_type)

    if parameter:
        query = query.filter(Alert.parameter == parameter)

    if sensor_id:
        query = query.filter(Alert.sensor_id == sensor_id)

    if from_ts:
        from_dt = datetime.fromisoformat(from_ts)
        query = query.filter(Alert.timestamp >= from_dt)

    if to_ts:
        to_dt = datetime.fromisoformat(to_ts)
        query = query.filter(Alert.timestamp <= to_dt)

    rows = query.order_by(Alert.timestamp.desc()).limit(limit).all()

    result = [{
        "sensor_id": r.sensor_id,
        "sensor_type": r.sensor_type,
        "parameter": r.parameter,
        "value": r.value,
        "threshold": r.threshold,
        "timestamp": r.timestamp,
    } for r in rows]

    session.close()
    return jsonify(result)


@app.route("/api/data")
def get_data():
    """Retrieve recent raw sensor data.

    Returns:
        flask.Response: JSON array of the 100 most recent sensor readings
    """
    session = SessionLocal()
    rows = session.query(SensorData).order_by(SensorData.timestamp.desc()).limit(100).all()
    session.close()
    return jsonify([{
        "sensor_id": r.sensor_id,
        "sensor_type": r.sensor_type,
        "timestamp": r.timestamp,
        "data": r.data
    } for r in rows])


@app.route("/api/aggregated")
def get_aggregated():
    """Retrieve aggregated sensor statistics with optional filtering.

    Query Parameters:
        limit (int): Maximum number of records to return (default: 50)
        sensor_id (str): Filter by sensor ID
        from (str): ISO format timestamp for start of time range
        to (str): ISO format timestamp for end of time range

    Returns:
        flask.Response: JSON array of aggregated statistics
    """
    session = SessionLocal()
    limit = int(request.args.get("limit", 50))
    sensor_id = request.args.get("sensor_id")
    from_ts = request.args.get("from")
    to_ts = request.args.get("to")

    query = session.query(AggregatedStats)

    if sensor_id:
        query = query.filter(AggregatedStats.sensor_id == int(sensor_id))

    if from_ts:
        from_dt = datetime.fromisoformat(from_ts)
        query = query.filter(AggregatedStats.timestamp >= from_dt)

    if to_ts:
        to_dt = datetime.fromisoformat(to_ts)
        query = query.filter(AggregatedStats.timestamp <= to_dt)

    rows = query.order_by(AggregatedStats.timestamp.desc()).limit(limit).all()

    result = [{
        "sensor_id": r.sensor_id,
        "sensor_type": r.sensor_type,
        "timestamp": r.timestamp,
        "window_size": r.window_size,
        "message_count": r.message_count,
        "avg_value": r.avg_value,
        "min_value": r.min_value,
        "max_value": r.max_value,
        "median": r.median,
        "std_dev": r.std_dev,
        "q25": r.q25,
        "q75": r.q75,
        "variance": r.variance,
    } for r in rows]

    session.close()
    return jsonify(result)


@app.route("/api/windows/<window_type>")
def get_window_stats(window_type):
    """Retrieve time-window based statistics for a specific window type.

    Args:
        window_type (str): The type of time window (e.g., 'hourly', 'daily')

    Query Parameters:
        limit (int): Maximum number of records to return (default: 100)
        sensor_id (str): Filter by sensor ID
        from (str): ISO format timestamp for start of time range
        to (str): ISO format timestamp for end of time range

    Returns:
        flask.Response: JSON array of time window statistics
    """
    session = SessionLocal()
    limit = int(request.args.get("limit", 100))
    sensor_id = request.args.get("sensor_id")
    from_ts = request.args.get("from")
    to_ts = request.args.get("to")

    query = session.query(TimeWindowStats).filter(TimeWindowStats.window_type == window_type)

    if sensor_id:
        query = query.filter(TimeWindowStats.sensor_id == int(sensor_id))

    if from_ts:
        from_dt = datetime.fromisoformat(from_ts)
        query = query.filter(TimeWindowStats.window_start >= from_dt)

    if to_ts:
        to_dt = datetime.fromisoformat(to_ts)
        query = query.filter(TimeWindowStats.window_start <= to_dt)

    rows = query.order_by(TimeWindowStats.window_start.desc()).limit(limit).all()

    result = [{
        "sensor_id": r.sensor_id,
        "window_type": r.window_type,
        "window_start": r.window_start,
        "window_end": r.window_end,
        "message_count": r.message_count,
        "avg_value": r.avg_value,
        "min_value": r.min_value,
        "max_value": r.max_value,
        "trend": r.trend
    } for r in rows]

    session.close()
    return jsonify(result)


if __name__ == "__main__":
    threading.Thread(target=consume_kafka, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)