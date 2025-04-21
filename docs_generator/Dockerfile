FROM python:3.11-slim

RUN pip install --no-cache-dir pdoc

WORKDIR /src
COPY . .

RUN pdoc -o /output \
    alerts_service \
    analytics_service \
    collector_service \
    flask_api \
    sensor_script.py

