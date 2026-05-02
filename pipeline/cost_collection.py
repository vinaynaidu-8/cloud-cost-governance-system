import boto3
from datetime import datetime, timedelta
import json

REGION = "ap-south-1"


def normalize(service):
    s = service.lower()

    if "elastic compute cloud" in s:
        return "ec2"
    elif "simple storage service" in s:
        return "s3"
    elif "relational database" in s:
        return "rds"
    elif "ec2 - other" in s:
        return "ebs"
    elif "elastic file system" in s:
        return "efs"
    else:
        return None


def get_cost(days):
    ce = boto3.client("ce")

    end = datetime.utcnow()
    start = end - timedelta(days=days)

    response = ce.get_cost_and_usage(
        TimePeriod={
            "Start": start.strftime("%Y-%m-%d"),
            "End": end.strftime("%Y-%m-%d")
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
    )

    costs = {}

    for day in response["ResultsByTime"]:
        for g in day["Groups"]:
            service = g["Keys"][0]
            amount = float(g["Metrics"]["UnblendedCost"]["Amount"])

            key = normalize(service)
            if not key:
                continue

            costs[key] = costs.get(key, 0) + amount

    return costs


def run():
    cost7 = get_cost(7)
    cost30 = get_cost(30)

    services = ["ec2", "s3", "rds", "ebs", "efs"]

    result = []

    for s in services:
        result.append({
            "service": s,
            "cost": {
                "last_7_days": round(cost7.get(s, 0), 4),
                "last_30_days": round(cost30.get(s, 0), 4)
            }
        })

    with open("data/enhanced_cost_metrics.json", "w") as f:
        json.dump({"resources": result}, f, indent=4)

    print("✅ Cost updated")


if __name__ == "__main__":
    run()
