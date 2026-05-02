"""
Configuration file for Cloud Cost Governance System
"""

import os
from datetime import datetime, timedelta

# AWS Configuration - Use IAM role when on EC2, fallback to environment variables
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Rule thresholds from abstract - ONLY these should be hardcoded
CPU_UNDERUTILIZED_THRESHOLD = 10.0  # CPU < 10%
CPU_IDLE_THRESHOLD = 5.0            # CPU ≈ 0-5%
CPU_OVERUTILIZED_THRESHOLD = 70.0   # CPU > 70-80%

# Data Collection Configuration
TIME_RANGES = {
    '1_day': 1,
    '7_days': 7,
    '30_days': 30
}

DEFAULT_TIME_RANGE = 7  # days

# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

# Data Directory Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(BASE_DIR, 'pipeline.log')

# AWS Services Configuration - All enabled for real data
SERVICES_TO_MONITOR = ['ec2', 's3', 'rds']
COST_EXPLORER_ENABLED = True
CLOUDWATCH_ENABLED = True

# Time Configuration
METRICS_PERIOD = 3600  # seconds (1 hour)

# Cost Explorer Configuration
COST_EXPLORER_GRANULARITY = 'DAILY'
COST_EXPLORER_METRICS = ['BlendedCost']
COST_EXPLORER_GROUP_BY = [
    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
    {'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}
]

# Date/Time Configuration
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'

def get_time_range_days(range_name):
    """Get number of days for a time range"""
    return TIME_RANGES.get(range_name, TIME_RANGES['7_days'])

def get_date_range(days):
    """Get start and end dates for given number of days"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return {
        'start': start_date.strftime(DATE_FORMAT),
        'end': end_date.strftime(DATE_FORMAT)
    }

def get_cost_explorer_time_range(days):
    """Get time range for Cost Explorer API"""
    date_range = get_date_range(days)
    return {
        'Start': date_range['start'],
        'End': date_range['end']
    }

def validate_config():
    """Validate required configuration"""
    errors = []
    
    # Check data directory
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR)
        except Exception as e:
            errors.append(f"Cannot create data directory: {e}")
    
    return errors

def print_config_summary():
    """Print configuration summary"""
    print("=" * 60)
    print("🔧 Cloud Cost Governance Configuration")
    print("=" * 60)
    print(f"AWS Region: {AWS_REGION}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Flask Debug: {FLASK_DEBUG}")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Default Time Range: {DEFAULT_TIME_RANGE}")
    print("=" * 60)
