# Cloud Cost Governance System

An intelligent cloud cost optimization system that analyzes AWS resource utilization and provides actionable recommendations to reduce unnecessary cloud expenditure. The application collects AWS resource information, evaluates utilization using predefined governance rules, and presents optimization recommendations through a web-based dashboard.

---

## Overview

Cloud environments often contain underutilized or idle resources that continue to generate unnecessary costs. This project helps identify such resources by analyzing their utilization metrics and classifying them into actionable categories such as **Stop**, **Resize**, or **Keep Running**.

The system is designed with a modular architecture, making it easy to extend with additional cloud services, optimization rules, and automation features.

---

## Features

- Analyze AWS EC2 resource utilization
- Monitor cloud resource status
- Rule-based resource optimization
- Identify idle and underutilized instances
- Estimate potential cost savings
- Interactive web dashboard
- Modular pipeline architecture
- Easy deployment on AWS EC2

---

## System Architecture

```
                +---------------------+
                |     AWS Services    |
                | EC2 | Cost Explorer |
                +----------+----------+
                           |
                           |
                    Data Collection
                           |
                           |
                +----------v----------+
                |    Processing &     |
                | Optimization Rules  |
                +----------+----------+
                           |
                           |
                  Recommendation Engine
                           |
                           |
                +----------v----------+
                |   Flask Dashboard   |
                +----------+----------+
                           |
                           |
                        End User
```

---

## Project Structure

```
cloud-cost-governance-system/
│
├── pipeline/                  # Core processing and optimization logic
├── web/                       # Flask web application
│   ├── app.py                 # Application entry point
│   ├── templates/
│   └── static/
│
├── data/                      # Input and processed data
├── config.py                  # Configuration settings
├── aws_setup.py               # AWS service initialization
├── run_system.py              # Pipeline execution script
├── requirements.txt           # Project dependencies
├── README.md
├── PROJECT_DOCUMENTATION.md
└── SYSTEM_VERIFICATION.md
```

---

## Technology Stack

### Programming Language

- Python

### Web Framework

- Flask

### Cloud Platform

- Amazon Web Services (AWS)

### AWS Services

- Amazon EC2
- AWS Cost Explorer
- Amazon CloudWatch

### Libraries

- Boto3
- Pandas
- NumPy

### Frontend

- HTML
- CSS
- Bootstrap
- JavaScript

---

## Workflow

1. Connect to AWS services.
2. Collect resource utilization information.
3. Process and validate the collected data.
4. Apply governance rules to identify optimization opportunities.
5. Classify resources based on utilization.
6. Estimate potential savings.
7. Display recommendations on the dashboard.

---

## Optimization Categories

| Category | Action | Description |
|----------|--------|-------------|
| High Priority | Stop | Resource is idle and can be stopped to reduce cost. |
| Medium Priority | Resize | Resource is underutilized and can be resized. |
| Low Priority | Keep Running | Resource utilization is within the expected range. |

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/vinaynaidu-8/cloud-cost-governance-system.git

cd cloud-cost-governance-system
```

### Create Virtual Environment

```bash
python3 -m venv venv
```

### Activate Virtual Environment

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

Navigate to the web directory.

```bash
cd web
```

Start the Flask application.

```bash
python app.py
```

The application will start on the configured local server.

---

## AWS Configuration

Before running the application, ensure that AWS credentials are configured with the required permissions.

Required AWS services include:

- Amazon EC2
- Amazon CloudWatch
- AWS Cost Explorer

Configure credentials using:

```bash
aws configure
```

---

## Sample Analysis

The system evaluates resource utilization and generates recommendations such as:

| Resource | Status | Recommendation |
|----------|--------|----------------|
| EC2 Instance A | Idle | Stop |
| EC2 Instance B | Underutilized | Resize |
| EC2 Instance C | Optimally Utilized | Keep Running |

---

## Future Enhancements

- Machine Learning based utilization prediction
- Automatic remediation actions
- Multi-cloud support
- Email notifications
- Scheduled optimization reports
- Historical trend analysis
- Resource tagging support
- Cost forecasting
- Automated governance policies

---

## Author

**Vinay Naidu**

Master of Computer Applications (MCA)

Cloud Computing | Python | AWS | DevOps

GitHub: https://github.com/vinaynaidu-8

---

## License

This project is intended for educational and research purposes.
