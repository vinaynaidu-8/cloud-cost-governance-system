"""
Configuration file for Cloud Cost Governance System
"""

import os
from datetime import datetime, timedelta

# AWS Configuration
AWS_REGION = 'us-east-1'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Cost Thresholds for Optimization
CPU_UTILIZATION_THRESHOLD = 20.0  # % below which is considered idle
MEMORY_UTILIZATION_THRESHOLD = 30.0
STORAGE_UTILIZATION_THRESHOLD = 50.0
IDLE_INSTANCE_THRESHOLD_HOURS = 24  # Hours of inactivity before recommendation

# Data Collection Configuration
TIME_RANGES = {
    '1_day': 1,
    '7_days': 7,
    '30_days': 30
}

DEFAULT_TIME_RANGE = 7  # days

# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = True
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000

# Data Directory Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SAMPLE_DATA_DIR = os.path.join(BASE_DIR, 'sample_data')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(BASE_DIR, 'pipeline.log')

# Dashboard Configuration
DASHBOARD_REFRESH_INTERVAL = 300  # seconds (5 minutes)
MAX_RECOMMENDATIONS_DISPLAY = 20

# AWS Services Configuration
SERVICES_TO_MONITOR = ['ec2', 's3', 'rds']
COST_EXPLORER_ENABLED = True
CLOUDWATCH_ENABLED = True

# Time Configuration
METRICS_PERIOD = 3600  # seconds (1 hour)

# Optimization Thresholds
OPTIMIZATION_THRESHOLDS = {
    'ec2': {
        'idle_cpu_threshold': CPU_UTILIZATION_THRESHOLD,      # CPU % below which instance is considered idle
        'low_cpu_threshold': CPU_UTILIZATION_THRESHOLD,      # CPU % below which instance is underutilized
        'idle_cpu_threshold': 5.0,      # CPU % below which instance is considered idle
        'low_cpu_threshold': 20.0,      # CPU % below which instance is underutilized
        'idle_network_threshold': 100.0, # Network MB below which instance is considered idle
        'min_running_hours': 24.0        # Minimum hours before considering optimization
    },
    's3': {
        'large_bucket_threshold': 100.0,  # GB above which to suggest lifecycle policies
        'infrequent_access_threshold': 30.0  # Days after which to move to IA storage
    },
    'rds': {
        'low_cpu_threshold': 15.0,      # CPU % below which instance is underutilized
        'low_storage_threshold': 20.0,  # Storage % below which instance is underutilized
        'min_running_hours': 24.0       # Minimum hours before considering optimization
    }
}

# Priority Scoring
PRIORITY_WEIGHTS = {
    'cost_savings': 0.4,      # Higher weight for cost savings
    'resource_waste': 0.3,    # High waste increases priority
    'confidence': 0.2,        # Higher confidence increases priority
    'resource_type': 0.1      # EC2 gets slightly higher priority
}

# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

# Data Directory Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SAMPLE_DATA_DIR = os.path.join(BASE_DIR, 'sample_data')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(BASE_DIR, 'pipeline.log')

# Dashboard Configuration
DASHBOARD_REFRESH_INTERVAL = 300  # seconds (5 minutes)
MAX_RECOMMENDATIONS_DISPLAY = 20

# Cost Explorer Configuration
COST_EXPLORER_GRANULARITY = 'DAILY'
COST_EXPLORER_METRICS = ['BlendedCost', 'UnblendedCost', 'UsageQuantity']
COST_EXPLORER_GROUP_BY = [
    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
    {'Type': 'DIMENSION', 'Key': 'OPERATION'}
]

# CloudWatch Configuration
CLOUDWATCH_PERIOD = 3600  # 1 hour in seconds
CLOUDWATCH_STATISTICS = ['Average', 'Sum', 'Maximum', 'Minimum']

# Anomaly Detection Configuration
ANOMALY_DETECTION = {
    'cost_spike_threshold': 50.0,      # % increase to flag as anomaly
    'storage_growth_threshold': 20.0,   # % growth to flag as anomaly
    'cpu_deviation_threshold': 30.0,    # % deviation from baseline to flag as anomaly
    'min_data_points': 7               # Minimum data points for anomaly detection
}

# Date/Time Configuration
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'

def get_time_range_days(range_name):
    """Get number of days for a time range"""
    return TIME_RANGES.get(range_name, TIME_RANGES[DEFAULT_TIME_RANGE])

def get_date_range(days):
    """Get start and end dates for given number of days"""
    end_date = datetime.now()
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

# Validate configuration
def validate_config():
    """Validate required configuration"""
    errors = []
    
    # Check AWS credentials
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        errors.append("AWS credentials not configured")
    
    # Check data directory
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR)
        except Exception as e:
            errors.append(f"Cannot create data directory: {e}")
    
    return errors

# Print configuration summary
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
