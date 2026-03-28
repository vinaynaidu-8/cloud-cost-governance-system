# Intelligent Cloud Cost Governance System - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- AWS Account with appropriate permissions
- Git for cloning the repository

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-repo/intelligent-cloud-cost-governance.git
cd intelligent-cloud-cost-governance
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure AWS Credentials
```bash
# Option 1: AWS CLI Configuration
aws configure

# Option 2: Environment Variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Option 3: IAM Role (Recommended for EC2 deployment)
# Attach IAM role with required permissions to EC2 instance
```

### Step 4: Required AWS IAM Permissions
Ensure your AWS credentials have the following permissions:
- `cloudwatch:GetMetricStatistics`
- `cloudwatch:ListMetrics`
- `ec2:DescribeInstances`
- `ec2:DescribeInstanceTypes`
- `s3:ListAllMyBuckets`
- `s3:GetBucketLocation`
- `rds:DescribeDBInstances`
- `ce:GetCostAndUsage`
- `sts:GetCallerIdentity`

### Step 5: Run the Data Collection Pipeline
```bash
# Navigate to pipeline directory
cd pipeline

# Run resource discovery
python resource_discovery.py

# Collect metrics
python metrics_collection.py

# Collect cost data
python cost_collection.py

# Generate optimization recommendations
python optimization_engine.py
```

### Step 6: Start the Web Dashboard
```bash
# Navigate to web directory
cd ../web

# Start Flask application
python app.py
```

### Step 7: Access the Dashboard
Open your web browser and navigate to:
```
http://localhost:5000
```

## 🏗️ AWS Deployment Instructions

### Option 1: EC2 Instance Deployment

#### 1. Launch EC2 Instance
```bash
# Using AWS CLI
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx \
    --iam-instance-profile Name=CloudCostGovernanceRole \
    --user-data file://user-data-script.sh
```

#### 2. User Data Script (user-data-script.sh)
```bash
#!/bin/bash
yum update -y
yum install python3 python3-pip git -y
cd /home/ec2-user
git clone https://github.com/your-repo/intelligent-cloud-cost-governance.git
cd intelligent-cloud-cost-governance
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/cost-governance.service << EOF
[Unit]
Description=Cloud Cost Governance Dashboard
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/intelligent-cloud-cost-governance/web
Environment=PATH=/home/ec2-user/intelligent-cloud-cost-governance/venv/bin
ExecStart=/home/ec2-user/intelligent-cloud-cost-governance/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable cost-governance.service
systemctl start cost-governance.service
```

#### 3. Security Group Configuration
Ensure your security group allows:
- Port 22 (SSH) - Your IP only
- Port 5000 (HTTP) - 0.0.0.0/0

### Option 2: Docker Deployment

#### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "web/app.py"]
```

#### 2. Build and Run Docker Container
```bash
# Build image
docker build -t cloud-cost-governance .

# Run container
docker run -d \
    --name cost-governance \
    -p 5000:5000 \
    -v ~/.aws:/root/.aws \
    cloud-cost-governance
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
FLASK_ENV=production
FLASK_DEBUG=False
```

### Custom Configuration
Edit `config.py` (if exists) or modify the following in pipeline scripts:
- Cost thresholds
- Instance type mappings
- Regional settings
- Data retention periods

## 📊 Data Directory Structure
```
data/
├── inventory.json           # Discovered AWS resources
├── metrics_inventory.json   # Collected CloudWatch metrics
├── cost_metrics_inventory.json  # Cost analysis data
├── optimization_report.json # Optimization recommendations
└── anomaly_report.json     # Anomaly detection results
```

## 🔄 Automation Setup

### Cron Job for Automated Data Collection
```bash
# Edit crontab
crontab -e

# Add entries for automated execution
0 */6 * * * cd /path/to/intelligent-cloud-cost-governance/pipeline && python resource_discovery.py
15 */6 * * * cd /path/to/intelligent-cloud-cost-governance/pipeline && python metrics_collection.py
30 */6 * * * cd /path/to/intelligent-cloud-cost-governance/pipeline && python cost_collection.py
45 */6 * * * cd /path/to/intelligent-cloud-cost-governance/pipeline && python optimization_engine.py
```

### AWS EventBridge (CloudWatch Events)
```json
{
  "Source": ["aws.events"],
  "DetailType": ["Scheduled Event"],
  "Detail": {
    "event": ["CostGovernancePipeline"]
  }
}
```

## 🧪 Testing

### Run Unit Tests
```bash
# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run tests
pytest tests/ -v --cov=.

# Run specific test file
pytest tests/test_optimization_engine.py -v
```

### Manual Testing
```bash
# Test individual pipeline components
python pipeline/resource_discovery.py
python pipeline/metrics_collection.py
python pipeline/cost_collection.py
python pipeline/optimization_engine.py

# Test web application
cd web && python app.py
```

## 🚨 Troubleshooting

### Common Issues

#### 1. AWS Credentials Error
```
Solution: Verify AWS credentials are properly configured
Run: aws sts get-caller-identity
```

#### 2. Permission Denied
```
Solution: Check IAM permissions for required AWS services
Ensure least privilege principle is followed
```

#### 3. No Data in Dashboard
```
Solution: 
1. Check if pipeline scripts ran successfully
2. Verify data files exist in data/ directory
3. Check CloudWatch metrics availability
```

#### 4. Cost Explorer Access Denied
```
Solution: 
1. Enable Cost Explorer in AWS Console
2. Add ce:GetCostAndUsage permission
3. Wait 24 hours for data to be available
```

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG
```

## 📈 Monitoring and Maintenance

### Application Health Check
```bash
curl http://localhost:5000/health
```

### Log Files
- Application logs: Check Flask console output
- AWS API logs: Enable CloudTrail for API auditing
- System logs: `/var/log/messages` (Linux) or Event Viewer (Windows)

### Performance Optimization
- Use pagination for large resource sets
- Implement caching for frequently accessed data
- Schedule data collection during off-peak hours
- Monitor AWS API rate limits

## 🔒 Security Considerations

1. **IAM Permissions**: Use least privilege principle
2. **Credentials**: Never hardcode AWS credentials
3. **Network**: Use security groups to restrict access
4. **Data**: Encrypt sensitive data at rest and in transit
5. **Monitoring**: Enable AWS CloudTrail for audit logging

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review AWS service limits and permissions
3. Consult the project documentation
4. Create an issue in the GitHub repository

---

**Note**: This system is designed for educational and demonstration purposes. For production use, consider additional security, monitoring, and scalability enhancements.
