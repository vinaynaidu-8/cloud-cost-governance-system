# Live AWS Data Implementation Guide

## 🎯 Overview

This guide explains how to implement live AWS data ingestion for the Cloud Cost Governance System, replacing the static sample data with real-time data from AWS services.

## 🔄 Data Flow Architecture

```
AWS Services → Pipeline Scripts → Data Files → Flask Dashboard
     ↓              ↓              ↓           ↓
CloudWatch → metrics_collection.py → metrics_inventory.json → Real-time metrics
Cost Explorer → cost_collection.py → cost_metrics_inventory.json → Live cost data
EC2/S3/RDS → resource_discovery.py → inventory.json → Current resources
```

## 🚀 Quick Start for Live Data

### Step 1: Configure AWS Credentials

```bash
# Option 1: AWS CLI (Recommended)
aws configure

# Option 2: Environment Variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Step 2: Test AWS Configuration

```bash
# Test AWS permissions and connectivity
python aws_setup.py
```

### Step 3: Run Live Data Pipeline

```bash
# Run complete data collection pipeline
python pipeline/run_pipeline.py
```

### Step 4: Start Dashboard with Live Data

```bash
# Start dashboard (automatically uses live data)
python web/app.py
```

## 📊 Pipeline Components

### 1. Resource Discovery (`pipeline/resource_discovery.py`)

**Purpose**: Discover all AWS resources (EC2, S3, RDS)

**AWS APIs Used**:
- `ec2:DescribeInstances`
- `s3:ListAllMyBuckets`
- `rds:DescribeDBInstances`

**Data Output**: `data/inventory.json`

**Key Features**:
- Collects detailed resource metadata
- Tracks resource state and running hours
- Captures tags for categorization

### 2. Metrics Collection (`pipeline/metrics_collection.py`)

**Purpose**: Collect CloudWatch metrics for discovered resources

**AWS APIs Used**:
- `cloudwatch:GetMetricStatistics`
- `cloudwatch:ListMetrics`

**Data Output**: `data/metrics_inventory.json`

**Key Features**:
- CPU utilization for EC2 instances
- Network I/O metrics
- Storage utilization for RDS
- S3 bucket size metrics

### 3. Cost Collection (`pipeline/cost_collection.py`)

**Purpose**: Retrieve cost data from AWS Cost Explorer

**AWS APIs Used**:
- `ce:GetCostAndUsage`
- `ce:GetDimensionValues`

**Data Output**: `data/cost_metrics_inventory.json`

**Key Features**:
- 7-day, 30-day cost data
- Service-level cost breakdown
- Forecast future costs

### 4. Optimization Engine (`pipeline/optimization_engine.py`)

**Purpose**: Analyze metrics and generate optimization recommendations

**Data Input**: All collected data files

**Data Output**: `data/optimization_report.json`

**Key Features**:
- Rule-based optimization logic
- Priority scoring system
- Estimated savings calculations
- Confidence levels

## 🔧 Configuration

### Time Range Configuration

The system supports multiple time ranges for analysis:

```python
# In config.py
TIME_RANGES = {
    '1_day': 1,
    '7_days': 7,
    '30_days': 30
}
```

### Optimization Thresholds

Customize optimization thresholds in `config.py`:

```python
OPTIMIZATION_THRESHOLDS = {
    'ec2': {
        'idle_cpu_threshold': 5.0,      # CPU % for idle detection
        'low_cpu_threshold': 20.0,      # CPU % for underutilization
        'idle_network_threshold': 100.0, # Network MB for idle
        'min_running_hours': 24.0        # Minimum hours before optimization
    }
}
```

### Cost Estimation

Instance hourly rates are configurable:

```python
EC2_COST_PER_HOUR = {
    't3.micro': 0.0104,
    't3.small': 0.0208,
    't3.medium': 0.0416,
    # ... more instances
}
```

## 🌐 Dashboard Integration

### Live vs Sample Data

The Flask app automatically prioritizes live data:

1. **First Priority**: Check `data/` directory for live data
2. **Fallback**: Use `sample_data/` if live data unavailable
3. **Indicator**: Dashboard shows data source and freshness

### API Endpoints

- `GET /api/dashboard-data` - Returns summary with data source info
- `POST /analyze` - Analyze specific resource type
- `GET /health` - System health check

### Data Freshness

The system checks if data is fresh (updated within last hour):

```python
def check_data_freshness():
    """Check if data is fresh (updated within last hour)"""
    inventory_file = os.path.join(DATA_DIR, 'inventory.json')
    if os.path.exists(inventory_file):
        file_time = datetime.fromtimestamp(os.path.getmtime(inventory_file))
        age = datetime.now() - file_time
        return age.total_seconds() < 3600
    return False
```

## 🔄 Automation

### Cron Job Setup (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add entries for automated data collection
0 */6 * * * cd /path/to/project && python pipeline/run_pipeline.py
```

### Windows Task Scheduler

```batch
# Create batch file
@echo off
cd /d "E:\4th sem Project\intelligent-cloud-cost-governance-phase-2"
python pipeline/run_pipeline.py
```

### AWS EventBridge (CloudWatch Events)

```json
{
  "Source": ["aws.events"],
  "DetailType": ["Scheduled Event"],
  "ScheduleExpression": "rate(6 hours)"
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. AWS Credentials Not Found
```
Error: Unable to locate credentials
Solution: Configure AWS credentials with 'aws configure'
```

#### 2. Cost Explorer Not Enabled
```
Error: AccessDeniedException
Solution: Enable Cost Explorer in AWS Management Console
```

#### 3. No CloudWatch Data
```
Error: No metrics available
Solution: Wait 24 hours after launching instances for metrics
```

#### 4. Permission Denied
```
Error: AccessDenied
Solution: Check IAM permissions for required services
```

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python pipeline/run_pipeline.py
```

### Data Validation

Validate collected data:

```python
# In pipeline/run_pipeline.py
def validate_data_files():
    """Validate that all required data files exist and are valid JSON"""
    # ... validation logic
```

## 📊 Sample Live Data Output

### Inventory.json (Live)
```json
{
    "account_id": "123456789012",
    "region": "us-east-1",
    "timestamp": "2026-03-24T10:30:00.000Z",
    "resources": [
        {
            "service": "ec2",
            "resource_id": "i-1234567890abcdef0",
            "resource_type": "t3.large",
            "state": "running",
            "running_hours": 216.5,
            "tags": {"Environment": "production"}
        }
    ]
}
```

### Optimization Report.json (Live)
```json
{
    "timestamp": "2026-03-24T10:30:00.000Z",
    "summary": {
        "total_recommendations": 3,
        "total_estimated_monthly_savings": 156.78
    },
    "recommendations": [
        {
            "service": "ec2",
            "resource_id": "i-1234567890abcdef0",
            "priority": "HIGH",
            "analysis": {
                "status": "IDLE",
                "recommendation": "Stop instance",
                "cpu_utilization": 3.2,
                "estimated_monthly_savings": 149.76
            }
        }
    ]
}
```

## 🔮 Future Enhancements

### Real-Time Updates
- WebSocket integration for live updates
- Push notifications for critical recommendations
- Real-time cost monitoring

### Advanced Analytics
- Machine learning for cost prediction
- Anomaly detection with statistical models
- Trend analysis and forecasting

### Multi-Account Support
- AWS Organizations integration
- Cross-account cost aggregation
- Centralized dashboard for multiple accounts

## 📋 Implementation Checklist

- [ ] Configure AWS credentials
- [ ] Test AWS permissions with `aws_setup.py`
- [ ] Run pipeline with `pipeline/run_pipeline.py`
- [ ] Verify data files in `data/` directory
- [ ] Start dashboard with `web/app.py`
- [ ] Test live data functionality
- [ ] Set up automation (cron/scheduled tasks)
- [ ] Monitor system performance and costs

## 🎯 Success Metrics

- **Data Freshness**: < 1 hour old
- **Pipeline Success Rate**: > 95%
- **Dashboard Response Time**: < 2 seconds
- **Cost Coverage**: All AWS services monitored
- **Recommendation Accuracy**: > 80% confidence

---

**Note**: Live data ingestion requires proper AWS permissions and may incur costs for API calls and data transfer. Monitor your AWS usage and costs when implementing live data collection.
