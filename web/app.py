from flask import Flask, render_template, request
import boto3
from datetime import datetime, timedelta

app = Flask(__name__)

REGION = "ap-south-1"

ec2 = boto3.client("ec2", region_name=REGION)
cw = boto3.client("cloudwatch", region_name=REGION)
rds = boto3.client("rds", region_name=REGION)
efs = boto3.client("efs", region_name=REGION)
s3 = boto3.client("s3")
ce = boto3.client("ce", region_name="us-east-1")


# ---------- COST ----------
def get_cost(service, days):
    try:
        end = datetime.utcnow().date()
        start = end - timedelta(days=days)

        service_map = {
            "ec2": "Amazon Elastic Compute Cloud - Compute",
            "s3": "Amazon Simple Storage Service",
            "rds": "Amazon Relational Database Service",
            "ebs": "Amazon Elastic Block Store",
            "efs": "Amazon Elastic File System"
        }

        response = ce.get_cost_and_usage(
            TimePeriod={"Start": str(start), "End": str(end)},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            Filter={
                "Dimensions": {
                    "Key": "SERVICE",
                    "Values": [service_map.get(service)]
                }
            }
        )

        return float(response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"])
    except:
        return 0.0


# ---------- EC2 ----------
def analyze_ec2(instances, days):
    recommendations = []

    for inst in instances:
        metrics = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": inst}],
            StartTime=datetime.utcnow() - timedelta(days=days),
            EndTime=datetime.utcnow(),
            Period=3600,
            Statistics=["Average"]
        )

        datapoints = metrics.get("Datapoints", [])
        avg_cpu = (
            sum(d["Average"] for d in datapoints) / len(datapoints)
            if datapoints else 0
        )

        if avg_cpu < 5:
            recommendations.append({
                "priority": "HIGH",
                "resource_id": inst,
                "analysis": {
                    "status": "Idle",
                    "action": "Stop Instance"
                }
            })

        elif avg_cpu < 20:
            recommendations.append({
                "priority": "MEDIUM",
                "resource_id": inst,
                "analysis": {
                    "status": "Underutilized",
                    "action": "Resize Instance"
                }
            })

        elif avg_cpu > 80:
            recommendations.append({
                "priority": "MEDIUM",
                "resource_id": inst,
                "analysis": {
                    "status": "Overutilized",
                    "action": "Scale Up"
                }
            })

    return recommendations


# ---------- ROUTE ----------
@app.route("/")
def home():
    return render_template("index.html", result=None)


@app.route("/analyze", methods=["POST"])
def analyze():
    resource = request.form.get("resource")
    days = int(request.form.get("days"))

    cost = get_cost(resource, days)

    recommendations = []
    count = 0

    # ---------- EC2 ----------
    if resource == "ec2":
        instances = [
            i["InstanceId"]
            for r in ec2.describe_instances()["Reservations"]
            for i in r["Instances"]
            if i["State"]["Name"] == "running"
        ]

        count = len(instances)
        if count > 0:
            recommendations = analyze_ec2(instances, days)

    # ---------- S3 ----------
    elif resource == "s3":
        buckets = s3.list_buckets()["Buckets"]
        count = len(buckets)

        if count > 5:
            recommendations.append({
                "priority": "MEDIUM",
                "resource_id": "S3 Buckets",
                "analysis": {
                    "status": "Underutilized",
                    "action": "Enable Lifecycle"
                }
            })

    # ---------- RDS ----------
    elif resource == "rds":
        dbs = rds.describe_db_instances()["DBInstances"]
        count = len(dbs)

        for db in dbs:
            recommendations.append({
                "priority": "MEDIUM",
                "resource_id": db["DBInstanceIdentifier"],
                "analysis": {
                    "status": "Underutilized",
                    "action": "Review DB Usage"
                }
            })

    # ---------- EBS ----------
    elif resource == "ebs":
        volumes = ec2.describe_volumes()["Volumes"]
        count = len(volumes)

        unused = [v for v in volumes if v["State"] == "available"]

        for v in unused:
            recommendations.append({
                "priority": "HIGH",
                "resource_id": v["VolumeId"],
                "analysis": {
                    "status": "Idle",
                    "action": "Delete Volume"
                }
            })

    # ---------- EFS ----------
    elif resource == "efs":
        fs = efs.describe_file_systems()["FileSystems"]
        count = len(fs)

        if count > 0:
            recommendations.append({
                "priority": "MEDIUM",
                "resource_id": "EFS",
                "analysis": {
                    "status": "Underutilized",
                    "action": "Optimize Storage"
                }
            })

    # ---------- NO ACTION ----------
    if not recommendations:
        recommendations = [{
            "priority": "LOW",
            "resource_id": resource.upper(),
            "analysis": {
                "status": "Optimized",
                "action": "No Action Needed"
            }
        }]

    result = {
        "resource": resource.upper(),
        "resource_count": count,
        "total_cost": round(cost, 4),
        "summary": {
            "total_savings": round(cost * 0.3, 4)
        },
        "recommendations": recommendations
    }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
