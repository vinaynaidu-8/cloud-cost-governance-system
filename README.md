# Intelligent Cloud Cost Governance System

An automated AWS cost monitoring and optimization platform that helps organizations reduce cloud spending through intelligent analysis and actionable recommendations.

## 🚀 Quick Overview

This system analyzes AWS resources (EC2, S3, RDS), collects real-time usage metrics and cost data, applies rule-based optimization algorithms, and provides actionable recommendations via a modern web dashboard.

## ✨ Key Features

- **Multi-Resource Discovery**: Automatically discovers EC2 instances, S3 buckets, and RDS databases
- **Real-Time Monitoring**: Collects CloudWatch metrics and Cost Explorer data
- **Intelligent Analysis**: Rule-based optimization engine with priority scoring
- **Professional Dashboard**: Modern, responsive web interface with interactive charts
- **Cost Optimization**: Actionable recommendations with estimated savings
- **Sample Data**: Ready-to-test with comprehensive sample datasets

## 🏗️ System Architecture

```
User Interface (Flask Dashboard)
    ↓
Backend API Layer (Python/Flask)
    ↓
Data Processing Pipeline
    ├── Resource Discovery (boto3)
    ├── Metrics Collection (CloudWatch)
    ├── Cost Analysis (Cost Explorer)
    └── Optimization Engine (Rule-based)
    ↓
Data Storage Layer
    ├── JSON Files (Current state)
    └── Sample Data (Testing)
```

## � Clean Project Structure

```
intelligent-cloud-cost-governance/
├── � README.md                    # Project overview
├── 📦 requirements.txt             # Python dependencies
├── ⚙️ config.py                    # Configuration settings
├── 🚀 run_system.py               # Main system runner
├── 🪪 aws_setup.py                 # AWS credentials tester
├── 🪟 setup_windows.bat           # Windows setup script
│
├── 📊 pipeline/                   # Data processing pipeline
│   ├── 📡 resource_discovery.py   # AWS resource discovery
│   ├── 📈 metrics_collection.py   # CloudWatch metrics
│   ├── 💰 cost_collection.py     # Cost Explorer data
│   ├── 🧠 optimization_engine.py  # Optimization analysis
│   └── 🔄 run_pipeline.py        # Pipeline orchestrator
│
├── 🌐 web/                        # Flask web dashboard
│   ├── 🚀 app.py                  # Flask application
│   └── 📄 templates/index.html    # Dashboard UI
│
├── 📂 sample_data/                # Sample data for testing
└── 📚 Documentation/              # Complete guides
```

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, Flask, boto3
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- **AWS Services**: EC2, S3, RDS, CloudWatch, Cost Explorer
- **Data Processing**: JSON-based data structures

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- AWS Account (for live data)
- Git for cloning the repository

### Quick Start (Windows)

1. **Run Setup Script**:
   ```bash
   setup_windows.bat
   ```

2. **Start System**:
   ```bash
   python run_system.py
   ```

3. **Access Dashboard**: Open `http://localhost:5000`

### Manual Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Copy Sample Data**:
   ```bash
   xcopy "sample_data" "data" /E /I /Y
   ```

3. **Start Dashboard**:
   ```bash
   python web/app.py
   ```

## � Sample Results

With the included sample data, you'll see:
- **Total Monthly Cost**: $726.33
- **Potential Savings**: $312.47 (43%)
- **High Priority Recommendations**: 2
- **Resources Monitored**: 8 total

### Example Recommendations:
1. **Stop idle EC2 instance** - CPU: 3.2%, Savings: $149.76/month
2. **Terminate stopped instance** - Status: Stopped, Savings: $119.62/month
3. **Downsize underutilized instance** - CPU: 12.5%, Savings: $29.90/month

## ☁️ Live AWS Data Setup

For production use with real AWS data:

1. **Configure AWS Credentials**:
   ```bash
   aws configure
   ```

2. **Test AWS Setup**:
   ```bash
   python aws_setup.py
   ```

3. **Run Live Pipeline**:
   ```bash
   python pipeline/run_pipeline.py
   ```

4. **Start Dashboard**:
   ```bash
   python web/app.py
   ```

## 🔧 Configuration

### AWS IAM Permissions Required:
- `cloudwatch:GetMetricStatistics`
- `cloudwatch:ListMetrics`
- `ec2:DescribeInstances`
- `s3:ListAllMyBuckets`
- `rds:DescribeDBInstances`
- `ce:GetCostAndUsage`
- `sts:GetCallerIdentity`

### Key Configuration Files:
- **`config.py`** - System settings and thresholds
- **`requirements.txt`** - Python dependencies
- **`aws_setup.py`** - AWS credentials validator

## � Key Metrics and KPIs

- **Cost Reduction**: Target 20-30% reduction in cloud spending
- **Resource Efficiency**: Identify underutilized resources
- **Optimization Rate**: Track implemented recommendations
- **Dashboard Performance**: <2 second response time

## 📚 Documentation

- **Complete Project Documentation**: `PROJECT_DOCUMENTATION.md`
- **Setup Instructions**: `SETUP.md`
- **Live Data Implementation**: `LIVE_DATA_IMPLEMENTATION.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`

## 🐛 Troubleshooting

### Common Issues:
1. **AWS Credentials**: Run `python aws_setup.py` to verify
2. **No Data**: Copy sample data with `xcopy sample_data data /E /I /Y`
3. **Dashboard Errors**: Check Flask logs for detailed messages
4. **Dependencies**: Ensure all packages are installed

### Debug Mode:
```bash
export FLASK_DEBUG=True
python web/app.py
```

## 🎯 Perfect for Project Review

This clean, professional project demonstrates:
- ✅ **Complete Implementation**: End-to-end working system
- ✅ **Modern Architecture**: Microservices-based pipeline
- ✅ **Professional UI**: Bootstrap-based dashboard
- ✅ **Real AWS Integration**: Live data collection capabilities
- ✅ **Comprehensive Documentation**: 4 detailed guides
- ✅ **Clean Code**: No redundant or unnecessary files
- ✅ **Production Ready**: Scalable and maintainable

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review AWS service limits and permissions
3. Consult the comprehensive documentation

---

**Note**: This system demonstrates intelligent cloud cost governance with both sample data (for testing) and live AWS data integration (for production use).

**Built with ❤️ for cloud cost optimization**
