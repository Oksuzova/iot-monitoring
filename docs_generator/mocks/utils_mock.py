# mocks/utils_mock.py
from unittest.mock import MagicMock

def process_data_batch(*args, **kwargs):
    pass

def calculate_statistics(*args, **kwargs):
    return {
        'mean': 0.0,
        'median': 0.0,
        'std': 0.0
    }

def check_thresholds(*args, **kwargs):
    return []

def format_message(*args, **kwargs):
    return ""

def send_alert(*args, **kwargs):
    pass