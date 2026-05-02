import json
from datetime import datetime

def main():
    try:
        with open("data/enhanced_cost_metrics.json") as f:
            cost_data = json.load(f)

        recommendations = []

        for r in cost_data.get("resources", []):
            service = r.get("service")
            cost = r.get("cost", {}).get("last_7_days", 0)

            priority = "LOW"
            action = "No action needed"

            if cost > 0.05:
                priority = "HIGH"
                action = "Consider optimization or cost reduction"
            elif cost > 0.01:
                priority = "MEDIUM"
                action = "Monitor usage and optimize if needed"

            recommendations.append({
                "service": service,
                "priority": priority,
                "recommendation": action,
                "analysis": {
                    "estimated_monthly_savings": round(cost * 4.33 * 0.3, 4)
                }
            })

        output = {
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": recommendations,
            "summary": {
                "total_estimated_monthly_savings": sum(
                    r["analysis"]["estimated_monthly_savings"] for r in recommendations
                ),
                "high_priority": len([r for r in recommendations if r["priority"] == "HIGH"]),
                "medium_priority": len([r for r in recommendations if r["priority"] == "MEDIUM"]),
                "low_priority": len([r for r in recommendations if r["priority"] == "LOW"])
            }
        }

        with open("data/enhanced_optimization_report.json", "w") as f:
            json.dump(output, f, indent=4)

        print("✅ Optimization completed!")

    except Exception as e:
        print(f"❌ Optimization error: {e}")
