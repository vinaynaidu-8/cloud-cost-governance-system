# Cloud Cost Governance System

<p align="center">
  <img src="https://github.com/user-attachments/assets/713eec09-1764-47d9-833c-060499fd1a38" alt="Cloud Cost Governance System Banner" width="100%">

<p align="center">
  <strong>AWS • Flask • Python • Cloud Cost Optimization</strong>
</p>


A rule-based cloud cost optimization system that analyzes AWS resource utilization and provides actionable recommendations to help reduce unnecessary cloud costs. The application integrates with AWS services, evaluates resource usage, and presents optimization insights through a web-based dashboard.

---

## Project Overview

Cloud Cost Governance System is a web-based application developed to help optimize AWS cloud costs by analyzing resource utilization and identifying optimization opportunities. The application integrates with Amazon CloudWatch and AWS Cost Explorer to collect utilization and cost metrics, applies predefined governance rules, and generates actionable recommendations.

Built using Python, Flask, and Boto3, the system presents cloud usage insights through an interactive dashboard, enabling users to identify idle or underutilized resources and make informed cost optimization decisions.

## Key Features

### AWS Monitoring

- Monitor Amazon EC2 resource utilization.
- Retrieve cloud cost data using AWS Cost Explorer.
- Collect utilization metrics from Amazon CloudWatch.

### Cost Optimization

- Analyze resource utilization using predefined governance rules.
- Identify idle and underutilized resources.
- Generate optimization recommendations such as **Stop**, **Resize**, or **Keep Running**.

### Dashboard & Reporting

- Interactive web dashboard built with Flask.
- Visual representation of utilization metrics and cost insights.
- Simple and user-friendly interface for monitoring cloud resources.
---

## Technology Stack

| Category | Technologies |
|----------|--------------|
| **Programming Language** | Python |
| **Backend Framework** | Flask |
| **Cloud Platform** | Amazon Web Services (AWS) |
| **AWS Services** | Amazon EC2, Amazon CloudWatch, AWS Cost Explorer |
| **AWS SDK** | Boto3 |
| **Frontend** | HTML, CSS, Bootstrap, JavaScript |
| **Development Tools** | Git, GitHub, VS Code |
---

# System Architecture

<p align="center">
  <img src="https://github.com/user-attachments/assets/0bc3f0fa-03b0-45c8-9f4c-7f0bc917b93f" alt="Cloud Cost Governance System Banner" width="100%">

  ### Architecture Components

| Component | Description |
|-----------|-------------|
| **Flask Application** | Serves as the backend and coordinates data processing and dashboard rendering. |
| **Amazon EC2** | Provides information about compute resources. |
| **Amazon CloudWatch** | Supplies utilization metrics used for resource evaluation. |
| **AWS Cost Explorer** | Retrieves cloud cost and usage information. |
| **Governance Rule Engine** | Applies predefined rules to classify resources and generate optimization recommendations. |
| **Dashboard** | Displays utilization metrics, cloud cost insights, and optimization recommendations through a web interface. |

---

## How It Works

The application follows the following execution flow:

1. Establishes a connection with AWS services using Boto3.
2. Retrieves EC2 resource information, CloudWatch utilization metrics, and Cost Explorer data.
3. Processes the collected information using predefined governance rules.
4. Classifies resources based on their utilization levels.
5. Generates optimization recommendations such as **Stop**, **Resize**, or **Keep Running**.
6. Displays the analyzed results through the Flask dashboard.

---

## Project Structure

```text
cloud-cost-governance-system/
│
├── docs/
│   └── images/                # README assets and screenshots
│
├── web/
│   ├── app.py                 # Main Flask application
│   ├── templates/
│   │   └── index.html         # Dashboard user interface
│   └── static/                # Static assets (CSS, JS, Images)
│
├── aws_setup.py               # AWS authentication and service initialization
├── config.py                  # Application configuration and constants
├── requirements.txt           # Project dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

### Directory Overview

| File / Folder | Description |
|---------------|-------------|
| **web/** | Contains the Flask application and user interface. |
| **app.py** | Entry point of the application that handles AWS integration, business logic, and dashboard rendering. |
| **templates/** | HTML templates used by the Flask application. |
| **static/** | Static resources such as CSS, JavaScript, and images. |
| **aws_setup.py** | Initializes AWS services and validates AWS connectivity. |
| **config.py** | Stores configurable values and application settings. |
| **requirements.txt** | Lists all Python packages required to run the project. |
| **docs/images/** | Stores images used in the GitHub README. |


---

# Dashboard

The dashboard provides a consolidated view of AWS resource utilization, cloud cost analysis, and rule-based optimization recommendations. It enables users to monitor cloud resources and quickly identify opportunities for cost optimization.

<p align="center">
  <img src="https://github.com/user-attachments/assets/dbc72762-7382-4de3-b10e-a9c77b4c01e8" alt="Cloud Cost Governance System Banner" width="100%">

---

# Sample Output

<p align="center">
  <img src="https://github.com/user-attachments/assets/18e33c7f-3fa3-4910-a52a-7c07ab2dcaaf" alt="Cloud Cost Governance System Banner" width="100%">


---

## Getting Started

Follow the steps below to set up and run the application on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/vinaynaidu-8/cloud-cost-governance-system.git
cd cloud-cost-governance-system
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure AWS Credentials

Configure AWS credentials before running the application.

```bash
aws configure
```

The application requires access to:

- Amazon EC2
- Amazon CloudWatch
- AWS Cost Explorer

> **Note:** If the application is deployed on an Amazon EC2 instance with an IAM Role attached, `aws configure` is not required.

### 6. Run the Application

```bash
cd web
python app.py
```

Once the server starts successfully, open the application in your browser using the local URL displayed in the terminal.
---

## AWS Configuration

Before running the project, configure AWS credentials.

```bash
aws configure
```

The application requires access to the following AWS services:

* Amazon EC2
* Amazon CloudWatch
* AWS Cost Explorer

---

## Current Scope

The current implementation focuses on AWS EC2 resource monitoring and rule-based cloud cost governance. The application integrates with Amazon CloudWatch and AWS Cost Explorer to analyze resource utilization and cost metrics, applies predefined governance rules, and presents optimization recommendations through a Flask-based dashboard.

---

## Future Enhancements

The current implementation serves as a foundation for extending cloud governance capabilities. Future improvements may include:

- Automated optimization actions for supported AWS resources.
- Historical utilization and cost trend analysis.
- Cost forecasting using historical usage patterns.
- Email notifications for optimization recommendations.
- Resource tagging and governance policy support.
- Multi-cloud support for Azure and Google Cloud Platform.
- Machine learning-based recommendation engine for intelligent cost optimization.
- Scheduled cloud governance reports and analytics.

---

## Project Outcome

This project demonstrates the practical application of cloud computing concepts by integrating AWS services with a Python-based web application to support cloud cost governance. It provides a centralized dashboard for monitoring resource utilization, analyzing cloud costs, and generating rule-based optimization recommendations that assist in improving cloud resource efficiency.

---

## Learning Outcomes

Through the development of this project, the following concepts were explored and implemented:

- AWS service integration using Boto3
- Cloud resource monitoring with Amazon CloudWatch
- Cloud cost analysis using AWS Cost Explorer
- Rule-based decision making for resource optimization
- Flask web application development
- Dashboard design and data visualization
- Git and GitHub for version control

---

## Repository Information

**Repository Name**

`cloud-cost-governance-system`

**Primary Technologies**

Python • Flask • AWS • Boto3 • HTML • CSS • Bootstrap

**Project Type**

Academic Cloud Computing Project

---

## Author

**Vinay Naidu**

Master of Computer Applications (MCA)

Cloud Computing | Python | AWS | Flask | DevOps

GitHub: https://github.com/vinaynaidu-8

LinkedIn: *(Add your LinkedIn profile URL here if you want recruiters to connect with you.)*

---

## Acknowledgements

This project was developed as part of an academic cloud computing initiative to explore AWS-based resource monitoring, cloud cost governance, and web application development. It reflects practical implementation of cloud governance concepts using publicly available AWS services and Python-based technologies.

---

## License

This project is intended for educational and learning purposes. The source code may be referenced for academic study and personal learning.

