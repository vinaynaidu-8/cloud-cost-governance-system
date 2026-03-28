import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_ebs_volumes() -> List[Dict[str, Any]]:
    """Analyze EBS volumes for optimization opportunities"""
    recommendations = []
    
    try:
        # Load inventory and cost data
        with open("data/inventory.json", "r") as f:
            inventory = json.load(f)
        with open("data/cost_metrics_inventory.json", "r") as f:
            cost_data = json.load(f)
        
        ebs_volumes = [r for r in inventory['resources'] if r['service'] == 'ebs']
        ebs_costs = {c['resource_id']: c for c in cost_data['resources'] if c['service'] == 'ebs'}
        
        for volume in ebs_volumes:
            volume_id = volume['resource_id']
            cost_info = ebs_costs.get(volume_id, {})
            
            # Check for unattached volumes
            if not volume['attached_to']:
                monthly_cost = cost_info.get('cost', {}).get('total_monthly', 0)
                recommendations.append({
                    "service": "ebs",
                    "resource_id": volume_id,
                    "resource_type": volume['resource_type'],
                    "priority": "HIGH",
                    "analysis": {
                        "status": "UNATTACHED",
                        "recommendation": "Delete unattached volume",
                        "reason": "Volume is not attached to any instance",
                        "size_gb": volume['size_gb'],
                        "monthly_cost": monthly_cost,
                        "estimated_monthly_savings": monthly_cost,
                        "confidence": "HIGH"
                    }
                })
                continue
            
            # Check for over-provisioned IOPS
            if volume['iops'] != 'N/A' and volume['volume_type'].startswith(('io1', 'gp3')):
                # Check if IOPS seem excessive for volume size
                size_gb = volume['size_gb']
                current_iops = volume['iops']
                
                # Baseline IOPS (3 per GB for gp3, 50 per GB for io1)
                baseline_iops = size_gb * 3 if volume['volume_type'].startswith('gp3') else size_gb * 50
                
                if current_iops > baseline_iops * 1.5:
                    monthly_cost = cost_info.get('cost', {}).get('total_monthly', 0)
                    recommended_iops = int(baseline_iops)
                    savings_percentage = (current_iops - recommended_iops) / current_iops
                    
                    recommendations.append({
                        "service": "ebs",
                        "resource_id": volume_id,
                        "resource_type": volume['resource_type'],
                        "priority": "MEDIUM",
                        "analysis": {
                            "status": "OVER_PROVISIONED_IOPS",
                            "recommendation": f"Reduce IOPS from {current_iops} to {recommended_iops}",
                            "reason": "IOPS provisioned significantly higher than baseline for volume size",
                            "current_iops": current_iops,
                            "recommended_iops": recommended_iops,
                            "monthly_cost": monthly_cost,
                            "estimated_monthly_savings": round(monthly_cost * savings_percentage, 2),
                            "confidence": "MEDIUM"
                        }
                    })
        
        logger.info(f"Generated {len(recommendations)} EBS recommendations")
        
    except Exception as e:
        logger.error(f"Error analyzing EBS volumes: {str(e)}")
    
    return recommendations

def analyze_lambda_functions() -> List[Dict[str, Any]]:
    """Analyze Lambda functions for optimization opportunities"""
    recommendations = []
    
    try:
        # Load inventory and cost data
        with open("data/inventory.json", "r") as f:
            inventory = json.load(f)
        with open("data/cost_metrics_inventory.json", "r") as f:
            cost_data = json.load(f)
        
        lambda_functions = [r for r in inventory['resources'] if r['service'] == 'lambda']
        lambda_costs = {c['resource_id']: c for c in cost_data['resources'] if c['service'] == 'lambda'}
        
        for func in lambda_functions:
            func_id = func['resource_id']
            cost_info = lambda_costs.get(func_id, {})
            
            # Check for over-provisioned memory
            memory_mb = func['memory_size']
            monthly_cost = cost_info.get('cost', {}).get('total_monthly', 0)
            
            # If memory > 512MB and runtime is Node.js/Python, might be over-provisioned
            if memory_mb > 512 and func['runtime'] in ['nodejs', 'python']:
                recommended_memory = 512
                savings_percentage = (memory_mb - recommended_memory) / memory_mb
                
                recommendations.append({
                    "service": "lambda",
                    "resource_id": func_id,
                    "resource_type": func['resource_type'],
                    "priority": "MEDIUM",
                    "analysis": {
                        "status": "OVER_PROVISIONED_MEMORY",
                        "recommendation": f"Reduce memory from {memory_mb}MB to {recommended_memory}MB",
                        "reason": "Memory allocation may be excessive for typical workloads",
                        "current_memory_mb": memory_mb,
                        "recommended_memory_mb": recommended_memory,
                        "monthly_cost": monthly_cost,
                        "estimated_monthly_savings": round(monthly_cost * savings_percentage, 2),
                        "confidence": "MEDIUM"
                    }
                })
            
            # Check for functions with high timeout (might indicate inefficient code)
            if func['timeout'] > 300:  # 5 minutes
                recommendations.append({
                    "service": "lambda",
                    "resource_id": func_id,
                    "resource_type": func['resource_type'],
                    "priority": "LOW",
                    "analysis": {
                        "status": "HIGH_TIMEOUT",
                        "recommendation": "Review function logic to reduce execution time",
                        "reason": "High timeout may indicate inefficient code or resource contention",
                        "current_timeout": func['timeout'],
                        "recommended_timeout": 300,
                        "monthly_cost": monthly_cost,
                        "estimated_monthly_savings": round(monthly_cost * 0.1, 2),  # 10% estimated savings
                        "confidence": "LOW"
                    }
                })
        
        logger.info(f"Generated {len(recommendations)} Lambda recommendations")
        
    except Exception as e:
        logger.error(f"Error analyzing Lambda functions: {str(e)}")
    
    return recommendations

def analyze_vpc_resources() -> List[Dict[str, Any]]:
    """Analyze VPC resources for optimization opportunities"""
    recommendations = []
    
    try:
        # Load inventory and cost data
        with open("data/inventory.json", "r") as f:
            inventory = json.load(f)
        with open("data/cost_metrics_inventory.json", "r") as f:
            cost_data = json.load(f)
        
        vpc_resources = [r for r in inventory['resources'] if r['service'] == 'vpc']
        vpc_costs = {c['resource_id']: c for c in cost_data['resources'] if c['service'] == 'vpc'}
        
        for resource in vpc_resources:
            resource_id = resource['resource_id']
            cost_info = vpc_costs.get(resource_id, {})
            
            if resource['resource_type'] == 'NAT Gateway':
                monthly_cost = cost_info.get('cost', {}).get('total_monthly', 0)
                
                # Check if NAT Gateway is in a development environment
                tags = resource.get('tags', {})
                if tags.get('Environment', '').lower() in ['dev', 'development', 'test']:
                    recommendations.append({
                        "service": "vpc",
                        "resource_id": resource_id,
                        "resource_type": resource['resource_type'],
                        "priority": "HIGH",
                        "analysis": {
                            "status": "DEV_ENVIRONMENT",
                            "recommendation": "Remove NAT Gateway from development environment",
                            "reason": "NAT Gateway in development environment may not be necessary",
                            "environment": tags.get('Environment', 'Unknown'),
                            "monthly_cost": monthly_cost,
                            "estimated_monthly_savings": monthly_cost,
                            "confidence": "HIGH"
                        }
                    })
        
        logger.info(f"Generated {len(recommendations)} VPC recommendations")
        
    except Exception as e:
        logger.error(f"Error analyzing VPC resources: {str(e)}")
    
    return recommendations

def generate_optimization_report():
    """Main function to generate comprehensive optimization report"""
    try:
        # Analyze all resource types
        ebs_recommendations = analyze_ebs_volumes()
        lambda_recommendations = analyze_lambda_functions()
        vpc_recommendations = analyze_vpc_resources()
        
        # Combine all recommendations
        all_recommendations = ebs_recommendations + lambda_recommendations + vpc_recommendations
        
        # Sort by priority and potential savings
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        all_recommendations.sort(key=lambda x: (
            priority_order.get(x['priority'], 3),
            -x['analysis']['estimated_monthly_savings']
        ))
        
        # Create optimization report
        total_savings = sum(rec['analysis']['estimated_monthly_savings'] for rec in all_recommendations)
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_recommendations": len(all_recommendations),
                "high_priority": len([r for r in all_recommendations if r['priority'] == 'HIGH']),
                "medium_priority": len([r for r in all_recommendations if r['priority'] == 'MEDIUM']),
                "low_priority": len([r for r in all_recommendations if r['priority'] == 'LOW']),
                "total_estimated_monthly_savings": round(total_savings, 2),
                "recommendations_by_service": {
                    service: len([r for r in all_recommendations if r['service'] == service])
                    for service in ['ebs', 'lambda', 'vpc']
                }
            },
            "recommendations": all_recommendations[:20]  # Top 20 recommendations
        }
        
        # Save to file
        with open("data/optimization_report.json", "w") as f:
            json.dump(report, f, indent=4, default=str)
        
        logger.info(f"Generated optimization report with {len(all_recommendations)} recommendations")
        logger.info(f"Total estimated savings: ${total_savings:.2f}/month")
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating optimization report: {str(e)}")
        return None

if __name__ == "__main__":
    generate_optimization_report()
