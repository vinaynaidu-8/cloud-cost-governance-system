import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cost estimation constants
EBS_COST_PER_GB_MONTH = {
    'gp2': 0.10,      # General Purpose SSD
    'gp3': 0.08,      # General Purpose SSD v3
    'io1': 0.125,     # Provisioned IOPS SSD
    'st1': 0.045,     # Throughput Optimized HDD
    'sc1': 0.025,     # Cold HDD
    'standard': 0.05    # Magnetic
}

EBS_IOPS_COST_PER_MONTH = 0.005  # Per provisioned IOPS

LAMBDA_COST_PER_MS = {
    'us-east-1': 0.0000166667,  # $0.0000166667 per 100ms
    'us-west-2': 0.0000166667,
    'eu-west-1': 0.0000166667,
    # Add more regions as needed
}

LAMBDA_REQUEST_COST_PER_MILLION = 0.20

NAT_GATEWAY_COST_PER_HOUR = 0.045
DATA_TRANSFER_COST_PER_GB = 0.09  # Outbound data transfer

def collect_ebs_costs() -> List[Dict[str, Any]]:
    """Collect EBS volume costs"""
    costs = []
    
    try:
        # Load EBS volumes from inventory
        with open("data/inventory.json", "r") as f:
            inventory = json.load(f)
        
        ebs_volumes = [r for r in inventory['resources'] if r['service'] == 'ebs']
        
        for volume in ebs_volumes:
            # Calculate monthly storage cost
            size_gb = volume['size_gb']
            volume_type = volume['volume_type'].split('(')[0].strip()
            
            storage_cost = size_gb * EBS_COST_PER_GB_MONTH.get(volume_type, 0.10)
            
            # Calculate IOPS cost for provisioned IOPS volumes
            iops_cost = 0
            if volume['iops'] != 'N/A' and volume_type in ['io1', 'gp3']:
                iops_cost = volume['iops'] * EBS_IOPS_COST_PER_MONTH
            
            total_monthly_cost = storage_cost + iops_cost
            
            costs.append({
                "service": "ebs",
                "resource_id": volume['resource_id'],
                "resource_type": volume['resource_type'],
                "cost": {
                    "storage_monthly": round(storage_cost, 4),
                    "iops_monthly": round(iops_cost, 4),
                    "total_monthly": round(total_monthly_cost, 4),
                    "last_7_days": round(total_monthly_cost * 7 / 30, 4)
                },
                "usage_metrics": {
                    "size_gb": size_gb,
                    "volume_type": volume_type,
                    "iops": volume['iops'],
                    "attached": len(volume['attached_to']) > 0
                }
            })
        
        logger.info(f"Calculated costs for {len(costs)} EBS volumes")
        
    except Exception as e:
        logger.error(f"Error collecting EBS costs: {str(e)}")
    
    return costs

def collect_lambda_costs() -> List[Dict[str, Any]]:
    """Collect Lambda function costs"""
    costs = []
    
    try:
        # Load Lambda functions from inventory
        with open("data/inventory.json", "r") as f:
            inventory = json.load(f)
        
        lambda_functions = [r for r in inventory['resources'] if r['service'] == 'lambda']
        
        for func in lambda_functions:
            # Estimate monthly costs based on typical usage patterns
            memory_mb = func['memory_size']
            region = func['region']
            
            # Base compute cost (assuming 1 hour of usage per day)
            compute_cost_per_second = (memory_mb / 1024) * LAMBDA_COST_PER_MS.get(region, 0.0000166667) * 10
            monthly_compute_cost = compute_cost_per_second * 3600 * 30 * 1  # 1 hour per day for 30 days
            
            # Request cost (assuming 1 million requests per month)
            monthly_request_cost = LAMBDA_REQUEST_COST_PER_MILLION
            
            total_monthly_cost = monthly_compute_cost + monthly_request_cost
            
            costs.append({
                "service": "lambda",
                "resource_id": func['resource_id'],
                "resource_type": func['resource_type'],
                "cost": {
                    "compute_monthly": round(monthly_compute_cost, 4),
                    "requests_monthly": round(monthly_request_cost, 4),
                    "total_monthly": round(total_monthly_cost, 4),
                    "last_7_days": round(total_monthly_cost * 7 / 30, 4)
                },
                "usage_metrics": {
                    "memory_mb": memory_mb,
                    "runtime": func['runtime'],
                    "timeout": func['timeout'],
                    "estimated_invocations_monthly": 1000000
                }
            })
        
        logger.info(f"Calculated costs for {len(costs)} Lambda functions")
        
    except Exception as e:
        logger.error(f"Error collecting Lambda costs: {str(e)}")
    
    return costs

def collect_vpc_costs() -> List[Dict[str, Any]]:
    """Collect VPC-related costs (NAT Gateways, Data Transfer)"""
    costs = []
    
    try:
        # Load VPC resources from inventory
        with open("data/inventory.json", "r") as f:
            inventory = json.load(f)
        
        vpc_resources = [r for r in inventory['resources'] if r['service'] == 'vpc']
        
        for resource in vpc_resources:
            if resource['resource_type'] == 'NAT Gateway':
                # NAT Gateway hourly cost
                monthly_cost = NAT_GATEWAY_COST_PER_HOUR * 24 * 30
                
                costs.append({
                    "service": "vpc",
                    "resource_id": resource['resource_id'],
                    "resource_type": resource['resource_type'],
                    "cost": {
                        "total_monthly": round(monthly_cost, 4),
                        "last_7_days": round(monthly_cost * 7 / 30, 4)
                    },
                    "usage_metrics": {
                        "gateway_type": "NAT Gateway",
                        "state": resource['state']
                    }
                })
        
        # Add estimated data transfer costs
        data_transfer_cost = 50 * DATA_TRANSFER_COST_PER_GB  # Assume 50GB/month
        
        costs.append({
            "service": "vpc",
            "resource_id": "data-transfer",
            "resource_type": "Data Transfer",
            "cost": {
                "total_monthly": round(data_transfer_cost, 4),
                "last_7_days": round(data_transfer_cost * 7 / 30, 4)
            },
            "usage_metrics": {
                "estimated_gb_monthly": 50
            }
        })
        
        logger.info(f"Calculated costs for {len(costs)} VPC resources")
        
    except Exception as e:
        logger.error(f"Error collecting VPC costs: {str(e)}")
    
    return costs

def collect_all_costs():
    """Main function to collect costs for all resources"""
    try:
        # Collect costs from all resource types
        ebs_costs = collect_ebs_costs()
        lambda_costs = collect_lambda_costs()
        vpc_costs = collect_vpc_costs()
        
        # Combine all costs
        all_costs = ebs_costs + lambda_costs + vpc_costs
        
        # Create cost data structure
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "resources": all_costs,
            "summary": {
                "total_monthly_cost": sum(cost['cost']['total_monthly'] for cost in all_costs),
                "total_7_day_cost": sum(cost['cost']['last_7_days'] for cost in all_costs),
                "costs_by_service": {
                    service: len([c for c in all_costs if c['service'] == service])
                    for service in ['ebs', 'lambda', 'vpc']
                }
            }
        }
        
        # Save to file
        with open("data/cost_metrics_inventory.json", "w") as f:
            json.dump(data, f, indent=4, default=str)
        
        logger.info(f"Successfully collected costs for {len(all_costs)} resources")
        logger.info(f"Total monthly cost: ${data['summary']['total_monthly_cost']:.2f}")
        
        return data
        
    except Exception as e:
        logger.error(f"Error in cost collection: {str(e)}")
        return None

if __name__ == "__main__":
    collect_all_costs()
