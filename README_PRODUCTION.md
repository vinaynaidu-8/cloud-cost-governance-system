# AWS Cloud Cost Governance System - Production Ready

## 🎯 Overview
Real-time AWS cost optimization dashboard that discovers, analyzes, and provides recommendations for AWS resources (EC2, S3, RDS) using actual AWS APIs.

## 🚀 Quick Start

### **Prerequisites**
- AWS Account with IAM role permissions
- Python 3.7+
- Git

### **Deployment on EC2**
```bash
# Clone repository
git clone <repository-url>
cd intelligent-cloud-cost-governance-phase-2

# Install dependencies
pip install -r requirements.txt

# Run data collection
python run_system.py

# Start dashboard
python web/app.py
```

### **Access Dashboard**
```
http://your-ec2-ip:5000
```

## 📊 Features
- ✅ Real AWS resource discovery (EC2, S3, RDS)
- ✅ Live CloudWatch metrics collection
- ✅ Actual AWS pricing via Cost Explorer
- ✅ Dynamic optimization recommendations
- ✅ Professional dashboard interface

## 🔐 AWS IAM Permissions Required
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes",
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation",
                "s3:GetBucketTagging",
                "rds:DescribeDBInstances",
                "cloudwatch:GetMetricStatistics",
                "pricing:GetProducts",
                "ce:GetCostAndUsage"
            ],
            "Resource": "*"
        }
    ]
}
```

## 📁 Project Structure
```
intelligent-cloud-cost-governance-phase-2/
├── config.py                 # Configuration settings
├── run_system.py            # Main pipeline orchestrator
├── requirements.txt          # Python dependencies
├── pipeline/
│   ├── resource_discovery.py    # Real AWS resource discovery
│   ├── metrics_collection.py    # Real CloudWatch metrics
│   ├── cost_collection.py      # Real AWS pricing
│   └── optimization_engine.py   # Real optimization logic
├── web/
│   ├── app.py               # Flask web server
│   └── templates/
│       └── index.html       # Dashboard interface
└── data/                   # Data storage
```

## 🎓 Real AWS Integration
- **Resource Discovery**: Uses boto3 clients for EC2, S3, RDS
- **Metrics Collection**: Real CloudWatch get_metric_statistics()
- **Cost Analysis**: AWS Pricing API + Cost Explorer
- **Optimization**: Rule-based analysis with actual usage patterns

## 🌐 Dashboard Features
- Real-time cost metrics
- Resource-specific analysis
- Priority-based recommendations
- Professional UI/UX design
- Mobile responsive interface

## 📈 Business Value
- **Cost Reduction**: Identify idle/underutilized resources
- **Optimization**: Right-sizing and lifecycle policies
- **Visibility**: Real-time cost monitoring
- **Automation**: Scheduled analysis and reporting

## 🏆 Project Highlights
- **Production Ready**: Deployed on AWS EC2
- **Real Data**: No sample/hardcoded values
- **Professional**: Enterprise-grade architecture
- **Scalable**: Modular pipeline design
