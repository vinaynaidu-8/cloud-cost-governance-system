from flask import Flask, render_template, request
import json
import boto3

app = Flask(__name__)
REGION = "ap-south-1"


# ---------- RESOURCE COUNTS ----------

def get_ec2():
    ec2 = boto3.client("ec2", region_name=REGION)
    res = ec2.describe_instances()
    return sum(
        1 for r in res["Reservations"]
        for i in r["Instances"]
        if i["State"]["Name"] == "running"
    )


def get_s3():
    s3 = boto3.client("s3")
    return len(s3.list_buckets()["Buckets"])


def get_rds():
    rds = boto3.client("rds", region_name=REGION)
    return len(rds.describe_db_instances()["DBInstances"])


def get_ebs():
    ec2 = boto3.client("ec2", region_name=REGION)
    return sum(1 for v in ec2.describe_volumes()["Volumes"] if v["State"] == "in-use")


def get_efs():
    try:
        efs = boto3.client("efs", region_name=REGION)
        return len(efs.describe_file_systems()["FileSystems"])
    except Exception:
        return 0


# ---------- LOAD COST ----------

def get_cost(resource, days):
    with open("../data/enhanced_cost_metrics.json") as f:
        data = json.load(f)

    for r in data["resources"]:
        if r["service"] == resource:
            return r["cost"]["last_7_days"] if days == "7" else r["cost"]["last_30_days"]

    return 0


# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("index.html", result=None)


@app.route("/analyze", methods=["POST"])
def analyze():
    resource = request.form["resource"]
    days = request.form["days"]

    cost = get_cost(resource, days)

    # ---------- COUNT ----------
    if resource == "ec2":
        count = get_ec2()
    elif resource == "s3":
        count = get_s3()
    elif resource == "rds":
        count = get_rds()
    elif resource == "ebs":
        count = get_ebs()
    elif resource == "efs":
        count = get_efs()
    else:
        count = 0

    # ---------- MONTHLY COST ----------
    monthly_cost = cost * 4.33

    # ---------- LOGIC ----------
    if monthly_cost > 1:
        priority = "HIGH"
        action = f"🔴 Optimize {resource.upper()} immediately"
        reason = "High monthly cost detected"
        savings = monthly_cost * 0.4

    elif monthly_cost > 0.1:
        priority = "MEDIUM"
        action = f"🟡 Optimize {resource.upper()} usage"
        reason = "Moderate cost detected"
        savings = monthly_cost * 0.25

    else:
        priority = "LOW"
        action = f"🟢 {resource.upper()} usage is efficient"
        reason = "Low cost usage"
        savings = 0

    result = {
        "resource": resource.upper(),
        "resource_count": count,
        "total_cost": round(monthly_cost, 4),
        "summary": {
            "high_priority": 1 if priority == "HIGH" else 0,
            "medium_priority": 1 if priority == "MEDIUM" else 0,
            "low_priority": 1 if priority == "LOW" else 0,
            "total_savings": round(savings, 4)
        },
        "recommendations": [{
            "priority": priority,
            "recommendation": action,
            "reason": reason,
            "analysis": {
                "estimated_monthly_savings": round(savings, 4)
            }
        }]
    }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
