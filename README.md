# Cloud Cost Governance System

## Overview

Cloud Cost Governance System is a web-based application developed to analyze AWS resource utilization and provide rule-based recommendations for optimizing cloud costs. The system collects resource information from AWS services, evaluates utilization using predefined governance rules, and presents optimization insights through an interactive dashboard.

The primary objective of this project is to help identify idle and underutilized cloud resources so that organizations can make informed decisions to reduce unnecessary cloud expenditure.

---

## Problem Statement

Cloud resources that remain underutilized or idle continue to generate costs even when they are not effectively used. Manually identifying such resources becomes difficult as cloud environments grow.

This project provides a simple governance solution that monitors AWS resource utilization and recommends appropriate optimization actions based on predefined rules.

---

## Objectives

* Analyze AWS cloud resource utilization.
* Identify idle and underutilized EC2 instances.
* Generate rule-based optimization recommendations.
* Display utilization insights through a web dashboard.
* Support better cloud cost management.

---

## Features

* AWS EC2 resource monitoring
* Rule-based resource classification
* Resource utilization analysis
* Cost optimization recommendations
* Interactive Flask dashboard
* Modular backend architecture
* Easy deployment on AWS EC2

---

# System Architecture

> **Placeholder:** Insert the overall architecture diagram here.

Example filename:

```
docs/images/system-architecture.png
```

---

# Application Workflow

> **Placeholder:** Insert the workflow diagram here.

Example filename:

```
docs/images/application-workflow.png
```

---

## Project Structure

```text
cloud-cost-governance-system/
│
├── web/
│   ├── app.py                 # Main Flask application
│   ├── templates/
│   │     └── index.html       # Dashboard UI
│   └── static/
│
├── pipeline/                  # Data processing and optimization logic
├── data/                      # Sample/processed data (if applicable)
├── config.py                  # Configuration settings
├── aws_setup.py               # AWS service initialization
├── requirements.txt           # Python dependencies
├── README.md
└── .gitignore
```

---

## Technology Stack

### Programming Language

* Python

### Backend Framework

* Flask

### Cloud Platform

* Amazon Web Services (AWS)

### AWS Services

* Amazon EC2
* Amazon CloudWatch
* AWS Cost Explorer

### Libraries

* Boto3
* Pandas
* NumPy

### Frontend

* HTML
* CSS
* Bootstrap
* JavaScript

### Development Tools

* VS Code
* Git
* GitHub

---

## System Workflow

1. Connect to AWS services.
2. Retrieve resource utilization information.
3. Process collected metrics.
4. Apply governance rules.
5. Classify resources based on utilization.
6. Generate optimization recommendations.
7. Display results through the dashboard.

---

## Optimization Logic

| Resource Status    | Recommendation |
| ------------------ | -------------- |
| Idle               | Stop           |
| Underutilized      | Resize         |
| Optimally Utilized | Keep Running   |

---

# Dashboard

> **Placeholder:** Insert dashboard screenshot here.

Example filename:

```
docs/images/dashboard.png
```

---

# Sample Output

> **Placeholder:** Insert sample recommendation screenshot here.

Example filename:

```
docs/images/sample-output.png
```

---

## Installation

Clone the repository.

```bash
git clone https://github.com/vinaynaidu-8/cloud-cost-governance-system.git
```

Move into the project directory.

```bash
cd cloud-cost-governance-system
```

Create a virtual environment.

```bash
python3 -m venv venv
```

Activate the virtual environment.

Linux/macOS

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install project dependencies.

```bash
pip install -r requirements.txt
```

---

## Running the Application

Navigate to the application directory.

```bash
cd web
```

Start the Flask server.

```bash
python app.py
```

Open your browser and access the application using the local address displayed in the terminal.

---

## AWS Configuration

Before running the project, configure AWS credentials.

```bash
aws configure
```

The application requires access to:

* Amazon EC2
* Amazon CloudWatch
* AWS Cost Explorer

---

## Future Enhancements

* Automated optimization actions
* Multi-cloud support
* Historical trend analysis
* Email notifications
* Scheduled governance reports
* Resource tagging support
* Cost forecasting
* Machine learning based recommendation engine

---

## Project Outcome

The project successfully demonstrates how AWS resource utilization can be analyzed using rule-based governance to identify optimization opportunities. It provides a functional dashboard that helps visualize utilization metrics and supports cost optimization decisions.

---

## Author

**Vinay Naidu**

Master of Computer Applications

Cloud Computing | Python | AWS

GitHub: https://github.com/vinaynaidu-8

---

## License

This project is developed for educational and academic purposes.
