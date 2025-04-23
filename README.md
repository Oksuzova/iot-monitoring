# IoT Sensor Data Processing System

This project is a distributed system for real-time ingestion, storage, analysis, and visualization of IoT sensor data. It uses MQTT, Kafka, PostgreSQL, and Flask, all orchestrated with Docker Compose.

## 🔍 Overview

**Key Features:**
- Real-time sensor data flow: MQTT → Kafka → PostgreSQL
- Microservices architecture
- REST API for querying data
- Analytics and alerting services
- Fully containerized setup

📘 **Documentation:**  
[https://oksuzova.github.io/iot-monitoring/](https://oksuzova.github.io/iot-monitoring/)

## 🛍 Architecture

```mermaid
flowchart TD
    A0["Sensor Data Generator"]
    A1["Docker Compose Orchestration"]
    A2["MQTT-to-Kafka Bridge"]
    A3["Flask Database Setup"]
    A4["Flask API Endpoints"]
    A5["Kafka Consumer for Data Ingestion"]
    A6["Alerts Service"]
    A7["Analytics Service"]
    A1 -- "Spins up" --> A0
    A0 -- "Publishes sensor data" --> A2
    A2 -- "Publishes to Kafka" --> A5
    A5 -- "Stores raw data" --> A3
    A4 -- "Queries data" --> A3
    A6 -- "Saves alerts" --> A3
    A7 -- "Saves analytics" --> A3
```

## 📦 Services

| Service            | Description                              |
|--------------------|------------------------------------------|
| `mosquitto`        | MQTT broker for publishing sensor data   |
| `kafka`            | Message broker for streaming data        |
| `collector_service`| Transfers MQTT messages to Kafka         |
| `postgres_db`      | Stores raw data, analytics and alerts    |
| `flask_api`        | Exposes REST endpoints to query data     |
| `analytics_service`| Performs statistical analysis            |
| `alerts_service`   | Generates alerts based on incoming data  |

## 🚀 How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/oksuzova/iot-monitoring.git
cd iot-monitoring
```

### 2. Start the System

```bash
docker-compose up --build
```

This will:
- Launch MQTT, Kafka, PostgreSQL
- Build all services (API, Analytics, Alerts, Collector)
- Automatically connect and orchestrate the data flow

### 3. Access the System

- **API & UI**: [http://localhost:5001/](http://localhost:5001/)

![img.png](img.png)

- **Database**: PostgreSQL running on `localhost:5432`  
  Credentials:
  ```text
  DB name: sensors  
  User: user  
  Password: password
  ```

### 4. Generate Sensor Data

You can simulate sensor data by publishing to Mosquitto manually:

```bash
mosquitto_pub -h localhost -p 1883 -t sensor/data -m '{"sensor_id": "123", "temperature": 22.5, "humidity": 40}'
```
or 

```bash
python3 sensor_script.py
```

### 5. Run the unit tests

```bash
docker exec -it iot-monitoring-flask_api-1 python -m unittest test_app.py -v
```

![img_1.png](img_1.png)

### 6. Sending Alerts to Telegram
You can set up alerts to be sent to your Telegram bot. 
Make sure to set the `BOT_TOKEN` and `CHAT_ID` environment variables in your `.env` file.

Alerts will be sent when sensor readings exceed predefined thresholds.

![img_2.png](img_2.png)