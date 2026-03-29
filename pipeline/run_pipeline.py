import sys
import os
import logging

# Fix imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pipeline():
    try:
        logger.info("🚀 Starting Pipeline...")

        from pipeline.resource_discovery import main as discover
        from pipeline.metrics_collection import main as metrics
        from pipeline.cost_collection import main as cost
        from pipeline.optimization_engine import main as optimize

        discover()
        metrics()
        cost()
        optimize()

        logger.info("🎉 Pipeline completed successfully!")

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_pipeline()
