from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
import boto3
import logging
import sys

# Fix import path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# -----------------------
# Load JSON
# -----------------------
def load_json(file):
    try:
        path = os.path.join(DATA_DIR, file)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading {file}: {e}")
        return {}

# -----------------------
# EC2 Running Count
# -----------------------
def get_running_ec2_count():
    ec2 = boto3.client("ec2", region_name="ap-south-1")
    response = ec2.describe_instances()

    count = 0
    for r in response["Reservations"]:
        for i in r["Instances"]:
            if i["State"]["Name"] == "running":
                count += 1
    return count

# -----------------------
# Dashboard (NO DATA INITIALLY)
# -----------------------
@app.route("/")
def dashboard():
    return render_template("index.html", result=None)

# -----------------------
# Minimal API (no fake cost)
# -----------------------
@app.route("/api/dashboard-data")
def dashboard_data():
    try:
        return jsonify({
            "total_cost": 0,
            "running_instances": get_running_ec2_count(),
            "data_source": "idle"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------
# Analyze Resource
# -----------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        cost_data = load_json("enhanced_cost_metrics.json")

        resource = request.form.get("resource", "").lower()
        resources = cost_data.get("resources", [])

        # Filter selected resource
        filtered = [
            r for r in resources
            if resource in r.get("service", "").lower()
        ]

        # Calculate cost
        total_cost = 0
        for r in filtered:
            weekly = r.get("cost", {}).get("last_7_days", 0)
            total_cost += weekly * 4.33

        # Running EC2 instances
        running_count = 0
        if resource == "ec2":
            running_count = get_running_ec2_count()

        # -----------------------
        # 🔥 RECOMMENDATION LOGIC
        # -----------------------
        recommendations = []
        high = medium = low = 0
        total_savings = 0

        for r in filtered:
            cost = r.get("cost", {}).get("last_7_days", 0)

            if cost > 0.05:
                priority = "HIGH"
                action = "🔴 Stop or terminate instance immediately (high unnecessary cost)"
                reason = "High cost detected with no optimization"
                savings = cost * 4.33 * 0.4
                high += 1

            elif cost > 0.01:
                priority = "MEDIUM"
                action = "🟡 Resize instance (reduce instance type to save cost)"
                reason = "Moderate usage, can optimize"
                savings = cost * 4.33 * 0.25
                medium += 1

            else:
                priority = "LOW"
                action = "🟢 Keep running (efficient usage)"
                reason = "Low cost, already optimized"
                savings = 0
                low += 1

            total_savings += savings

            recommendations.append({
                "service": resource.upper(),
                "priority": priority,
                "recommendation": action,
                "reason": reason,
                "analysis": {
                    "estimated_monthly_savings": round(savings, 4)
                }
            })

        result = {
            "resource": resource.upper(),
            "total_cost": round(total_cost, 4),
            "resource_count": running_count,
            "recommendations": recommendations,
            "summary": {
                "high_priority": high,
                "medium_priority": medium,
                "low_priority": low,
                "total_savings": round(total_savings, 4)
            }
        }

        return render_template("index.html", result=result)

    except Exception as e:
        logger.error(f"Error: {e}")
        return render_template("index.html", error=str(e))

# -----------------------
# Health
# -----------------------
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "time": datetime.now().isoformat()
    })

# -----------------------
# Run
# -----------------------
if __name__ == "__main__":
    print("🚀 Starting Dashboard...")
    app.run(host="0.0.0.0", port=5000, debug=True)
