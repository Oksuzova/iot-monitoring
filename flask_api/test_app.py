import unittest
from datetime import datetime, timedelta
import os

# Set environment variables for database connection
os.environ['DB_HOST'] = 'postgres_db'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'sensors'
os.environ['DB_USER'] = 'user'
os.environ['DB_PASSWORD'] = 'password'

from app import app
from db import SessionLocal
from models import Alert, SensorData, AggregatedStats, TimeWindowStats


class TestFlaskAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        cls.app = app.test_client()

    def setUp(self):
        self.db = SessionLocal()
        self._create_test_data()

    def tearDown(self):
        self.db.query(Alert).delete()
        self.db.query(SensorData).delete()
        self.db.query(AggregatedStats).delete()
        self.db.query(TimeWindowStats).delete()
        self.db.commit()
        self.db.close()

    def _create_test_data(self):
        sensor_data = SensorData(
            sensor_id=1,
            sensor_type="DHT22",
            timestamp=int(datetime.utcnow().timestamp()),
            data={"temperature": 25.5, "humidity": 60}
        )
        self.db.add(sensor_data)

        alert = Alert(
            sensor_id=1,
            sensor_type="DHT22",
            parameter="temperature",
            value=31.0,
            threshold=30.0,
            timestamp=datetime.utcnow()
        )
        self.db.add(alert)

        agg_stats = AggregatedStats(
            sensor_id=1,
            sensor_type="DHT22",
            timestamp=datetime.utcnow(),
            window_size=3600,
            message_count=10,
            avg_value=25.5,
            min_value=24.0,
            max_value=27.0,
            median=25.5,
            std_dev=0.5,
            q25=24.75,
            q75=26.25,
            variance=0.25
        )
        self.db.add(agg_stats)

        window_stats = TimeWindowStats(
            sensor_id=1,
            window_type="hourly",
            window_start=datetime.utcnow() - timedelta(hours=1),
            window_end=datetime.utcnow(),
            message_count=60,
            avg_value=25.5,
            min_value=24.0,
            max_value=27.0,
            trend=1.0
        )
        self.db.add(window_stats)

        self.db.commit()

    def test_dashboard_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_alerts_ui_route(self):
        response = self.app.get('/alerts-ui')
        self.assertEqual(response.status_code, 200)

    def test_temperature_ui_route(self):
        response = self.app.get('/temperature-ui')
        self.assertEqual(response.status_code, 200)

    def test_humidity_ui_route(self):
        response = self.app.get('/humidity-ui')
        self.assertEqual(response.status_code, 200)

    def test_co2_ui_route(self):
        response = self.app.get('/co2-ui')
        self.assertEqual(response.status_code, 200)

    def test_pm25_ui_route(self):
        response = self.app.get('/pm25-ui')
        self.assertEqual(response.status_code, 200)

    def test_get_alerts_with_filters(self):
        response = self.app.get('/api/alerts')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json, list))

        params = {
            'limit': 10,
            'sensor_id': 1,
            'sensor_type': 'DHT22',
            'parameter': 'temperature',
            'from': (datetime.utcnow() - timedelta(hours=24)).isoformat(),
            'to': datetime.utcnow().isoformat()
        }
        response = self.app.get('/api/alerts', query_string=params)
        self.assertEqual(response.status_code, 200)
        data = response.json
        if data:
            alert = data[0]
            self.assertEqual(alert['sensor_id'], 1)
            self.assertEqual(alert['sensor_type'], 'DHT22')
            self.assertEqual(alert['parameter'], 'temperature')

    def test_get_data_with_pagination(self):
        response = self.app.get('/api/data')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(isinstance(data, list))
        if data:
            sensor_data = data[0]
            self.assertIn('sensor_id', sensor_data)
            self.assertIn('sensor_type', sensor_data)
            self.assertIn('timestamp', sensor_data)
            self.assertIn('data', sensor_data)

    def test_get_aggregated_with_filters(self):
        params = {
            'limit': 10,
            'sensor_id': 1,
            'from': (datetime.utcnow() - timedelta(hours=24)).isoformat(),
            'to': datetime.utcnow().isoformat()
        }
        response = self.app.get('/api/aggregated', query_string=params)
        self.assertEqual(response.status_code, 200)
        data = response.json
        if data:
            stats = data[0]
            self.assertEqual(stats['sensor_id'], 1)
            self.assertIn('avg_value', stats)
            self.assertIn('min_value', stats)
            self.assertIn('max_value', stats)

    def test_get_window_stats_types(self):
        window_types = ['hourly', 'daily', 'weekly']
        for window_type in window_types:
            response = self.app.get(f'/api/windows/{window_type}')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(isinstance(response.json, list))

    def test_get_window_stats_with_filters(self):
        params = {
            'limit': 10,
            'sensor_id': 1,
            'from': (datetime.utcnow() - timedelta(hours=24)).isoformat(),
            'to': datetime.utcnow().isoformat()
        }
        response = self.app.get('/api/windows/hourly', query_string=params)
        self.assertEqual(response.status_code, 200)
        data = response.json
        if data:
            stats = data[0]
            self.assertEqual(stats['window_type'], 'hourly')
            self.assertEqual(stats['sensor_id'], 1)
            self.assertIn('message_count', stats)
            self.assertIn('avg_value', stats)
            self.assertIn('trend', stats)


if __name__ == '__main__':
    unittest.main()