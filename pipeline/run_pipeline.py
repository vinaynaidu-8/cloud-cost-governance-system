#!/usr/bin/env python3
"""
Main Pipeline Runner
Orchestrates the complete data collection and analysis pipeline
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add pipeline directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from resource_discovery import main as discover_resources
from metrics_collection import main as collect_metrics
from cost_collection import main as collect_costs
from optimization_engine import main as analyze_optimization

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def ensure_data_directory():
    """Ensure data directory exists"""
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    return data_dir

def run_pipeline():
    """Run the complete data collection and analysis pipeline"""
    logger.info("Starting Cloud Cost Governance Pipeline...")
    start_time = datetime.now()
    
    try:
        # Ensure data directory exists
        data_dir = ensure_data_directory()
        logger.info(f"Data directory: {data_dir}")
        
        # Step 1: Discover AWS Resources
        logger.info("Step 1: Discovering AWS Resources...")
        try:
            discover_resources()
            logger.info("✅ Resource discovery completed")
        except Exception as e:
            logger.error(f"❌ Resource discovery failed: {str(e)}")
            return False
        
        # Step 2: Collect CloudWatch Metrics
        logger.info("Step 2: Collecting CloudWatch Metrics...")
        try:
            collect_metrics()
            logger.info("✅ Metrics collection completed")
        except Exception as e:
            logger.error(f"❌ Metrics collection failed: {str(e)}")
            return False
        
        # Step 3: Collect Cost Data
        logger.info("Step 3: Collecting Cost Data from Cost Explorer...")
        try:
            collect_costs()
            logger.info("✅ Cost collection completed")
        except Exception as e:
            logger.error(f"❌ Cost collection failed: {str(e)}")
            return False
        
        # Step 4: Run Optimization Analysis
        logger.info("Step 4: Running Optimization Analysis...")
        try:
            analyze_optimization()
            logger.info("✅ Optimization analysis completed")
        except Exception as e:
            logger.error(f"❌ Optimization analysis failed: {str(e)}")
            return False
        
        # Generate pipeline summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            "pipeline_run": {
                "timestamp": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "SUCCESS",
                "steps_completed": 4
            }
        }
        
        # Save pipeline summary
        summary_file = data_dir / "pipeline_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"🎉 Pipeline completed successfully in {duration:.2f} seconds")
        logger.info(f"📊 Results saved to: {data_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}")
        return False

def validate_data_files():
    """Validate that all required data files exist and are valid JSON"""
    data_dir = Path(__file__).parent.parent / 'data'
    required_files = [
        'inventory.json',
        'metrics_inventory.json', 
        'cost_metrics_inventory.json',
        'optimization_report.json'
    ]
    
    missing_files = []
    invalid_files = []
    
    for file_name in required_files:
        file_path = data_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
        else:
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                invalid_files.append(file_name)
    
    if missing_files or invalid_files:
        logger.error(f"Data validation failed:")
        if missing_files:
            logger.error(f"  Missing files: {missing_files}")
        if invalid_files:
            logger.error(f"  Invalid JSON files: {invalid_files}")
        return False
    
    logger.info("✅ All data files validated successfully")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Intelligent Cloud Cost Governance Pipeline")
    print("=" * 60)
    
    # Run the pipeline
    success = run_pipeline()
    
    if success:
        print("\n✅ Pipeline completed successfully!")
        print("📊 Dashboard is ready with fresh AWS data")
        print("🌐 Start the dashboard: python web/app.py")
    else:
        print("\n❌ Pipeline failed!")
        print("📋 Check pipeline.log for detailed error information")
        sys.exit(1)
