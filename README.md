# Cloud Cost Governance System

<p align="center">
  <img src="https://github.com/user-attachments/assets/713eec09-1764-47d9-833c-060499fd1a38" alt="Cloud Cost Governance System Banner" width="100%">


A rule-based cloud cost optimization system that analyzes AWS resource utilization and provides actionable recommendations to help reduce unnecessary cloud costs. The application integrates with AWS services, evaluates resource usage, and presents optimization insights through a web-based dashboard.

---

## Project Overview

Cloud resources that remain idle or underutilized continue to incur costs. This project helps identify such resources by analyzing AWS utilization metrics and applying predefined governance rules to recommend appropriate optimization actions.

The application is built using Python and Flask, with AWS integration through Boto3, and provides an interactive dashboard for monitoring cloud resources and cost optimization opportunities.

---

## Key Features

* Analyze AWS EC2 resource utilization
* Retrieve AWS cost information using Cost Explorer
* Monitor resource metrics using Amazon CloudWatch
* Rule-based resource classification
* Optimization recommendations (Stop, Resize, or Keep Running)
* Interactive dashboard for visualization
* Modular and easy-to-maintain architecture

---

## Technology Stack

| Category             | Technologies                     |
| -------------------- | -------------------------------- |
| Programming Language | Python                           |
| Backend              | Flask                            |
| Cloud Platform       | Amazon Web Services (AWS)        |
| AWS Services         | EC2, CloudWatch, Cost Explorer   |
| SDK                  | Boto3                            |
| Frontend             | HTML, CSS, Bootstrap, JavaScript |
| Version Control      | Git, GitHub                      |

---

# System Architecture

<p align="center">
  <img src="https://github.com/user-attachments/assets/0bc3f0fa-03b0-45c8-9f4c-7f0bc917b93f" alt="Cloud Cost Governance System Banner" width="100%">

---

# Application Workflow

<p align="center">
  <img src="https://github.com/user-attachments/assets/b34af952-cdc2-4c0b-87f9-da0bf301adfb" alt="Cloud Cost Governance System Banner" width="100%">


---

## Project Structure

```text
cloud-cost-governance-system/
│
├── web/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│
├── aws_setup.py
├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## How It Works

1. Connects securely to AWS services.
2. Retrieves resource utilization and cost information.
3. Processes the collected metrics.
4. Applies rule-based governance logic.
5. Classifies resources based on utilization.
6. Generates optimization recommendations.
7. Displays the results through the web dashboard.

---

## Optimization Logic

| Resource Status    | Recommendation |
| ------------------ | -------------- |
| Idle               | Stop           |
| Underutilized      | Resize         |
| Optimally Utilized | Keep Running   |

---

# Dashboard

<p align="center">
  <img src="https://github.com/user-attachments/assets/dbc72762-7382-4de3-b10e-a9c77b4c01e8" alt="Cloud Cost Governance System Banner" width="100%">

---

# Sample Output

<p align="center">
  <img src="https://github.com/user-attachments/assets/18e33c7f-3fa3-4910-a52a-7c07ab2dcaaf" alt="Cloud Cost Governance System Banner" width="100%">


---

## Installation

Clone the repository.

```bash
git clone https://github.com/vinaynaidu-8/cloud-cost-governance-system.git
```

Navigate to the project directory.

```bash
cd cloud-cost-governance-system
```

Create a virtual environment.

```bash
python3 -m venv venv
```

Activate the virtual environment.

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

Install the required dependencies.

```bash
pip install -r requirements.txt
```

---

## Running the Application

Navigate to the application directory.

```bash
cd web
```

Start the Flask application.

```bash
python app.py
```

Open the application using the local URL displayed in the terminal.

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

## Future Enhancements

* Automated optimization actions
* Historical utilization reports
* Email notifications
* Cost forecasting
* Multi-cloud support
* Resource tagging support
* Machine learning based recommendation engine

---

## Project Outcome

This project demonstrates a practical approach to cloud cost governance by analyzing AWS resource utilization and generating rule-based optimization recommendations. It provides a simple and effective dashboard that helps users identify opportunities to improve cloud resource efficiency and reduce unnecessary costs.

---

## Author

**Vinay Naidu**

Master of Computer Applications (MCA)

Interests: Cloud Computing, Python, AWS, DevOps

GitHub: https://github.com/vinaynaidu-8

---

## License

This project is intended for educational and learning purposes.
