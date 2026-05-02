from datetime import datetime, timedelta, timezone
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from flask import Flask, render_template, request

REGION = os.getenv("AWS_REGION", "ap-south-1")
COST_EXPLORER_REGION = "us-east-1"
ALLOWED_DAYS = {1, 7, 30}

SERVICE_MAP = {
    "ec2": "Amazon Elastic Compute Cloud - Compute",
    "s3": "Amazon Simple Storage Service",
    "rds": "Amazon Relational Database Service",
    "ebs": "Amazon Elastic Block Store",
    "efs": "Amazon Elastic File System",
}

# Efficiency thresholds
THRESHOLDS = {
    "cpu_idle": 5.0,
    "cpu_under": 20.0,
    "cpu_over": 80.0,
    "ebs_ops_under_per_day": 100.0,
    "ebs_ops_over_per_day": 50000.0,
    "efs_io_idle_bytes_per_day": 1 * 1024 * 1024,
    "efs_io_under_bytes_per_day": 100 * 1024 * 1024,
    "efs_io_over_bytes_per_day": 100 * 1024 * 1024 * 1024,
}

# Savings factors by efficiency state (not by cost alone)
SAVINGS_FACTOR = {
    "IDLE": 0.90,
    "UNDERUTILIZED": 0.50,
    "OPTIMIZED": 0.00,
    "OVERUTILIZED": 0.00,
}

app = Flask(__name__)

session = boto3.Session(region_name=REGION)
ec2 = session.client("ec2")
cw = session.client("cloudwatch")
rds = session.client("rds")
efs = session.client("efs")
s3 = session.client("s3")
ce = boto3.client("ce", region_name=COST_EXPLORER_REGION)


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def now_utc():
    return datetime.now(timezone.utc)


def make_recommendation(priority, status_type, resource_id, status, action):
    return {
        "priority": priority,
        "status_type": status_type,
        "resource_id": resource_id,
        "analysis": {"status": status, "action": action},
    }


def get_cost(service, days):
    service_name = SERVICE_MAP.get(service)
    if not service_name:
        return 0.0

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    response = ce.get_cost_and_usage(
        TimePeriod={"Start": str(start_date), "End": str(end_date)},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        Filter={"Dimensions": {"Key": "SERVICE", "Values": [service_name]}},
    )

    total_cost = 0.0
    for item in response.get("ResultsByTime", []):
        total_cost += safe_float(item.get("Total", {}).get("UnblendedCost", {}).get("Amount"))
    return round(total_cost, 4)


def get_resource_cost_map(service, days):
    service_name = SERVICE_MAP.get(service)
    if not service_name:
        return {}

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    token = None
    cost_map = {}

    try:
        while True:
            kwargs = {
                "TimePeriod": {"Start": str(start_date), "End": str(end_date)},
                "Granularity": "DAILY",
                "Metrics": ["UnblendedCost"],
                "Filter": {"Dimensions": {"Key": "SERVICE", "Values": [service_name]}},
                "GroupBy": [{"Type": "DIMENSION", "Key": "RESOURCE_ID"}],
            }
            if token:
                kwargs["NextPageToken"] = token

            response = ce.get_cost_and_usage(**kwargs)
            for day in response.get("ResultsByTime", []):
                for group in day.get("Groups", []):
                    keys = group.get("Keys", [])
                    resource_key = keys[0] if keys else None
                    amount = safe_float(group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount"))
                    if resource_key:
                        cost_map[resource_key] = cost_map.get(resource_key, 0.0) + amount

            token = response.get("NextPageToken")
            if not token:
                break
    except (ClientError, BotoCoreError):
        return {}

    return {key: round(value, 4) for key, value in cost_map.items()}


def get_average_metric(namespace, metric_name, dimensions, days, period=3600, stat="Average"):
    end_time = now_utc()
    start_time = end_time - timedelta(days=days)

    data = cw.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=[stat],
    )

    datapoints = data.get("Datapoints", [])
    values = [safe_float(point.get(stat)) for point in datapoints if stat in point]
    return (sum(values) / len(values)) if values else 0.0


def get_sum_metric(namespace, metric_name, dimensions, days, period=3600):
    end_time = now_utc()
    start_time = end_time - timedelta(days=days)

    data = cw.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=["Sum"],
    )
    return sum(safe_float(point.get("Sum")) for point in data.get("Datapoints", []))


def match_resource_cost(resource_cost_map, resource_id):
    if not resource_cost_map:
        return 0.0

    candidates = (
        resource_id,
        resource_id.lower(),
        resource_id.upper(),
        f"i-{resource_id}" if not resource_id.startswith("i-") else resource_id,
    )
    for key in candidates:
        if key in resource_cost_map:
            return safe_float(resource_cost_map[key])

    for key, value in resource_cost_map.items():
        if resource_id in key:
            return safe_float(value)
    return 0.0


def classify_cpu(avg_cpu):
    if avg_cpu < THRESHOLDS["cpu_idle"]:
        return ("HIGH", "IDLE", f"Idle (avg CPU {avg_cpu:.2f}%)", "Stop/schedule running resource if not required")
    if avg_cpu < THRESHOLDS["cpu_under"]:
        return ("MEDIUM", "UNDERUTILIZED", f"Underutilized (avg CPU {avg_cpu:.2f}%)", "Right-size to smaller instance class")
    if avg_cpu <= THRESHOLDS["cpu_over"]:
        return ("LOW", "OPTIMIZED", f"Optimized (avg CPU {avg_cpu:.2f}%)", "No action needed")
    return ("MEDIUM", "OVERUTILIZED", f"Overutilized (avg CPU {avg_cpu:.2f}%)", "Scale up or tune workload")


def analyze_ec2(days):
    paginator = ec2.get_paginator("describe_instances")
    running_instance_ids = []
    recommendations = []

    for page in paginator.paginate(Filters=[{"Name": "instance-state-name", "Values": ["running"]}]):
        for reservation in page.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                instance_id = inst["InstanceId"]
                running_instance_ids.append(instance_id)

                avg_cpu = get_average_metric(
                    namespace="AWS/EC2",
                    metric_name="CPUUtilization",
                    dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                    days=days,
                )
                priority, status_type, status_text, action = classify_cpu(avg_cpu)
                recommendations.append(make_recommendation(priority, status_type, instance_id, status_text, action))
    return running_instance_ids, recommendations


def analyze_s3(days):
    buckets = s3.list_buckets().get("Buckets", [])
    discovered_buckets = []
    recommendations = []

    for bucket in buckets:
        bucket_name = bucket["Name"]
        discovered_buckets.append(bucket_name)

        try:
            object_probe = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            object_count = safe_float(object_probe.get("KeyCount", 0))
        except (ClientError, BotoCoreError):
            object_count = 0.0

        avg_objects = get_average_metric(
            namespace="AWS/S3",
            metric_name="NumberOfObjects",
            dimensions=[
                {"Name": "BucketName", "Value": bucket_name},
                {"Name": "StorageType", "Value": "AllStorageTypes"},
            ],
            days=days,
            period=86400,
        )

        if object_count <= 0 and avg_objects <= 0:
            rec = ("HIGH", "IDLE", "Idle (no objects found)", "Delete/archive bucket if unused")
        elif avg_objects < 100:
            rec = ("MEDIUM", "UNDERUTILIZED", f"Low usage (~{avg_objects:.0f} objects)", "Enable lifecycle and storage class transitions")
        else:
            rec = ("LOW", "OPTIMIZED", f"Active (~{avg_objects:.0f} objects)", "No action needed")

        recommendations.append(make_recommendation(rec[0], rec[1], bucket_name, rec[2], rec[3]))
    return discovered_buckets, recommendations


def analyze_rds(days):
    paginator = rds.get_paginator("describe_db_instances")
    db_instances = []
    for page in paginator.paginate():
        db_instances.extend(page.get("DBInstances", []))

    discovered = []
    recommendations = []

    for db in db_instances:
        db_id = db["DBInstanceIdentifier"]
        discovered.append(db_id)
        db_status = db.get("DBInstanceStatus", "")
        if db_status not in {"available", "backing-up", "storage-optimization"}:
            recommendations.append(
                make_recommendation(
                    "LOW",
                    "OPTIMIZED",
                    db_id,
                    f"Not active for compute analysis (status: {db_status})",
                    "No action needed",
                )
            )
            continue

        avg_cpu = get_average_metric(
            namespace="AWS/RDS",
            metric_name="CPUUtilization",
            dimensions=[{"Name": "DBInstanceIdentifier", "Value": db_id}],
            days=days,
        )

        priority, status_type, status_text, action = classify_cpu(avg_cpu)
        recommendations.append(make_recommendation(priority, status_type, db_id, status_text, action))
    return discovered, recommendations


def analyze_ebs(days):
    paginator = ec2.get_paginator("describe_volumes")
    discovered = []
    recommendations = []

    for page in paginator.paginate():
        for volume in page.get("Volumes", []):
            volume_id = volume["VolumeId"]
            state = volume.get("State", "")
            discovered.append(volume_id)

            if state == "available":
                recommendations.append(make_recommendation("HIGH", "IDLE", volume_id, "Idle (unattached volume)", "Delete volume if not required"))
                continue

            total_io = get_sum_metric(
                namespace="AWS/EBS",
                metric_name="VolumeReadOps",
                dimensions=[{"Name": "VolumeId", "Value": volume_id}],
                days=days,
            ) + get_sum_metric(
                namespace="AWS/EBS",
                metric_name="VolumeWriteOps",
                dimensions=[{"Name": "VolumeId", "Value": volume_id}],
                days=days,
            )

            ops_per_day = total_io / max(days, 1)

            if ops_per_day == 0:
                rec = ("HIGH", "IDLE", "Idle (0 read/write ops)", "Snapshot then delete if safe")
            elif ops_per_day < THRESHOLDS["ebs_ops_under_per_day"]:
                rec = ("MEDIUM", "UNDERUTILIZED", f"Underutilized (~{ops_per_day:.1f} ops/day)", "Move to cheaper/smaller volume profile")
            elif ops_per_day <= THRESHOLDS["ebs_ops_over_per_day"]:
                rec = ("LOW", "OPTIMIZED", f"Optimized (~{ops_per_day:.1f} ops/day)", "No action needed")
            else:
                rec = ("MEDIUM", "OVERUTILIZED", f"Overutilized (~{ops_per_day:.1f} ops/day)", "Use higher IOPS/throughput volume type")
            recommendations.append(make_recommendation(rec[0], rec[1], volume_id, rec[2], rec[3]))
    return discovered, recommendations


def analyze_efs(days):
    file_systems = efs.describe_file_systems().get("FileSystems", [])
    discovered = []
    recommendations = []

    for fs in file_systems:
        fs_id = fs["FileSystemId"]
        discovered.append(fs_id)
        fs_state = fs.get("LifeCycleState")
        if fs_state != "available":
            recommendations.append(
                make_recommendation(
                    "LOW",
                    "OPTIMIZED",
                    fs_id,
                    f"Not active for IO analysis (state: {fs_state})",
                    "No action needed",
                )
            )
            continue

        total_io_bytes = get_sum_metric(
            namespace="AWS/EFS",
            metric_name="TotalIOBytes",
            dimensions=[{"Name": "FileSystemId", "Value": fs_id}],
            days=days,
        )

        io_per_day = total_io_bytes / max(days, 1)

        if io_per_day <= THRESHOLDS["efs_io_idle_bytes_per_day"]:
            rec = ("HIGH", "IDLE", f"Idle (~{io_per_day:.0f} bytes/day IO)", "Remove unused EFS or archive data")
        elif io_per_day < THRESHOLDS["efs_io_under_bytes_per_day"]:
            rec = ("MEDIUM", "UNDERUTILIZED", f"Underutilized (~{io_per_day:.0f} bytes/day IO)", "Enable lifecycle/IA policy")
        elif io_per_day <= THRESHOLDS["efs_io_over_bytes_per_day"]:
            rec = ("LOW", "OPTIMIZED", f"Optimized (~{io_per_day:.0f} bytes/day IO)", "No action needed")
        else:
            rec = ("MEDIUM", "OVERUTILIZED", f"Overutilized (~{io_per_day:.0f} bytes/day IO)", "Scale throughput/performance mode")

        recommendations.append(make_recommendation(rec[0], rec[1], fs_id, rec[2], rec[3]))
    return discovered, recommendations


def estimate_monthly_savings(total_cost, days, resources, recommendations, service):
    if days <= 0 or not resources:
        return 0.0, {}

    resource_cost_map = get_resource_cost_map(service, days)
    estimated_resource_monthly_cost = {}

    total_resource_cost_in_window = 0.0
    for rid in resources:
        matched_cost = match_resource_cost(resource_cost_map, rid)
        total_resource_cost_in_window += matched_cost
        estimated_resource_monthly_cost[rid] = (matched_cost / days) * 30 if matched_cost > 0 else 0.0

    if total_resource_cost_in_window == 0:
        evenly_split = ((total_cost / days) * 30) / len(resources)
        for rid in resources:
            estimated_resource_monthly_cost[rid] = evenly_split

    savings = 0.0
    for rec in recommendations:
        rid = rec.get("resource_id")
        base_cost = estimated_resource_monthly_cost.get(rid, 0.0)
        factor = SAVINGS_FACTOR.get(rec.get("status_type", "OPTIMIZED"), 0.0)
        item_saving = base_cost * factor
        rec["analysis"]["estimated_monthly_cost"] = round(base_cost, 4)
        rec["analysis"]["potential_savings"] = round(item_saving, 4)
        savings += item_saving

    return round(savings, 4), {k: round(v, 4) for k, v in estimated_resource_monthly_cost.items()}


@app.route("/")
def home():
    return render_template("index.html", result=None, error=None)


@app.route("/analyze", methods=["POST"])
def analyze():
    resource = (request.form.get("resource") or "").strip().lower()
    try:
        days = int(request.form.get("days", "7"))
    except ValueError:
        days = 7

    if days not in ALLOWED_DAYS:
        days = 7

    if resource not in SERVICE_MAP:
        return render_template("index.html", result=None, error="Invalid resource selected.")

    try:
        total_cost = get_cost(resource, days)

        if resource == "ec2":
            discovered_resources, recommendations = analyze_ec2(days)
        elif resource == "s3":
            discovered_resources, recommendations = analyze_s3(days)
        elif resource == "rds":
            discovered_resources, recommendations = analyze_rds(days)
        elif resource == "ebs":
            discovered_resources, recommendations = analyze_ebs(days)
        elif resource == "efs":
            discovered_resources, recommendations = analyze_efs(days)

        if not recommendations:
            recommendations = [
                {
                    "priority": "LOW",
                    "status_type": "OPTIMIZED",
                    "resource_id": resource.upper(),
                    "analysis": {"status": "No optimization issues detected", "action": "No action needed"},
                }
            ]

        resource_count = len(discovered_resources)
        estimated_savings, resource_monthly_cost = estimate_monthly_savings(
            total_cost=total_cost,
            days=days,
            resources=discovered_resources,
            recommendations=recommendations,
            service=resource,
        )

        result = {
            "resource": resource.upper(),
            "resource_count": resource_count,
            "total_cost": total_cost,
            "days": days,
            "summary": {"total_savings": estimated_savings, "resource_monthly_cost": resource_monthly_cost},
            "recommendations": recommendations,
        }
        return render_template("index.html", result=result, error=None)

    except NoCredentialsError:
        return render_template(
            "index.html",
            result=None,
            error=(
                "AWS credentials not found. On EC2, attach an IAM role to this instance "
                "with Cost Explorer, CloudWatch, EC2, RDS, EFS, and S3 read permissions."
            ),
        )
    except (ClientError, BotoCoreError) as exc:
        return render_template("index.html", result=None, error=f"AWS API error: {exc}")
    except Exception as exc:
        return render_template("index.html", result=None, error=f"Unexpected error: {exc}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
