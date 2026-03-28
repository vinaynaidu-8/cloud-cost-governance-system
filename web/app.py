from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
import logging
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import configuration
try:
    from config import DATA_DIR, FLASK_DEBUG, FLASK_HOST, FLASK_PORT
except ImportError:
    # Fallback to default configuration
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    FLASK_DEBUG = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def load_json(file):
    """Load JSON file with error handling, prioritizing enhanced data over sample data"""
    try:
        # Try enhanced data first
        enhanced_path = os.path.join(DATA_DIR, f"enhanced_{file}")
        if os.path.exists(enhanced_path):
            with open(enhanced_path) as f:
                data = json.load(f)
                logger.info(f"Loaded enhanced data from {enhanced_path}")
                return data
        
        # Fallback to regular data
        live_path = os.path.join(DATA_DIR, file)
        if os.path.exists(live_path):
            with open(live_path) as f:
                data = json.load(f)
                logger.info(f"Loaded live data from {live_path}")
                return data
        
        # Fallback to sample data
        sample_path = os.path.join(os.path.dirname(DATA_DIR), 'sample_data', f"enhanced_{file}")
        if os.path.exists(sample_path):
            with open(sample_path) as f:
                data = json.load(f)
                logger.warning(f"Using enhanced sample data from {sample_path}")
                return data
        
        logger.error(f"Data file not found: {file}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing {file}: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error loading {file}: {str(e)}")
        return {}

def check_data_freshness():
    """Check if data is fresh (updated within last hour)"""
    try:
        inventory_file = os.path.join(DATA_DIR, 'inventory.json')
        if os.path.exists(inventory_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(inventory_file))
            age = datetime.now() - file_time
            return age.total_seconds() < 3600  # Fresh if less than 1 hour old
        return False
    except Exception:
        return False

@app.route("/")
def dashboard():
    """Main dashboard page"""
    return render_template("index.html", timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route("/api/dashboard-data")
def get_dashboard_data():
    """API endpoint to get dashboard summary data"""
    try:
        inventory = load_json("enhanced_inventory.json")
        cost_data = load_json("enhanced_cost_metrics.json")
        optimization = load_json("enhanced_optimization_report.json")
        
        # Calculate summary metrics
        total_resources = len(inventory.get("resources", []))
        
        # Get optimization summary
        opt_summary = optimization.get("summary", {})
        total_savings = opt_summary.get("total_estimated_monthly_savings", 0)
        high_priority = opt_summary.get("high_priority", 0)
        
        # Calculate total cost
        total_cost = 0
        for resource in cost_data.get("resources", []):
            cost = resource.get("cost", {})
            weekly_cost = cost.get("last_7_days", 0)
            total_cost += weekly_cost * 4.33  # Convert to monthly
        
        return jsonify({
            "total_cost": round(total_cost, 2),
            "total_savings": round(total_savings, 2),
            "total_resources": total_resources,
            "high_priority": high_priority,
            "last_updated": datetime.now().isoformat(),
            "data_fresh": check_data_freshness(),
            "data_source": "live" if os.path.exists(os.path.join(DATA_DIR, "inventory.json")) else "sample"
        })
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze_resources():
    """Analyze specific resource type"""
    try:
        resource = request.form.get("resource")
        days = request.form.get("days", "7")
        
        if not resource:
            return jsonify({"error": "Resource type is required"}), 400
        
        inventory = load_json("enhanced_inventory.json")
        cost_data = load_json("enhanced_cost_metrics.json")
        optimization = load_json("enhanced_optimization_report.json")
        
        # Filter resources by type
        filtered_resources = [r for r in inventory.get("resources", []) if r.get("service") == resource]
        
        # Calculate total cost for the resource type
        total_cost = 0.0
        for r in cost_data.get("resources", []):
            if r.get("service") == resource:
                weekly_cost = r.get("cost", {}).get("last_7_days", 0)
                total_cost += weekly_cost * 4.33  # Convert to monthly
        
        # Get recommendations for this resource type
        recommendations = []
        for r in optimization.get("recommendations", []):
            if r.get("service") == resource:
                recommendations.append(r)
        
        result = {
            "resource": resource.upper(),
            "days": days,
            "total_cost": round(total_cost, 2),
            "resource_count": len(filtered_resources),
            "recommendations": recommendations[:10],  # Limit to top 10 recommendations
            "summary": {
                "high_priority": len([r for r in recommendations if r.get("priority") == "HIGH"]),
                "medium_priority": len([r for r in recommendations if r.get("priority") == "MEDIUM"]),
                "low_priority": len([r for r in recommendations if r.get("priority") == "LOW"]),
                "total_savings": sum(r.get("analysis", {}).get("estimated_monthly_savings", 0) for r in recommendations)
            }
        }
        
        return render_template("index.html", result=result, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
    except Exception as e:
        logger.error(f"Error analyzing resources: {str(e)}")
        return render_template("index.html", error=str(e), timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    })

if __name__ == "__main__":
    logger.info("Starting Intelligent Cloud Cost Governance Dashboard...")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Debug mode: {FLASK_DEBUG}")
    logger.info(f"Server running on: http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
