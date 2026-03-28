"""
Real AWS Optimization Engine Module
Generates optimization recommendations based on real AWS data
"""

import boto3
import json
import logging
from datetime import datetime, timedelta
from config import AWS_REGION, CPU_UTILIZATION_THRESHOLD, MEMORY_UTILIZATION_THRESHOLD, STORAGE_UTILIZATION_THRESHOLD

logger = logging.getLogger(__name__)

def calculate_priority(savings_amount, confidence_level):
    """Calculate recommendation priority based on savings and confidence"""
    if savings_amount > 50 and confidence_level > 0.8:
        return 'HIGH'
    elif savings_amount > 20 and confidence_level > 0.6:
        return 'MEDIUM'
    else:
        return 'LOW'

def analyze_ec2_optimization(resource_data, metrics_data, cost_data):
    """Generate EC2 optimization recommendations"""
    recommendations = []
    
    resource_id = resource_data['resource_id']
    instance_type = resource_data['resource_type']
    state = resource_data['state']
    
    # Get metrics
    cpu_avg = metrics_data.get('metrics', {}).get('cpu_utilization', {}).get('average', 0)
    cpu_max = metrics_data.get('metrics', {}).get('cpu_utilization', {}).get('maximum', 0)
    network_in = metrics_data.get('metrics', {}).get('network', {}).get('in_mb_per_hour', 0)
    network_out = metrics_data.get('metrics', {}).get('network', {}).get('out_mb_per_hour', 0)
    
    # Get cost data
    hourly_rate = cost_data.get('hourly_rate', 0)
    total_cost = cost_data.get('total_cost', 0)
    
    # Check if instance is idle
    if state == 'running' and cpu_avg < CPU_UTILIZATION_THRESHOLD and network_in < 1 and network_out < 1:
        savings_per_month = hourly_rate * 24 * 30
        recommendation = {
            'service': 'ec2',
            'resource_id': resource_id,
            'resource_type': instance_type,
            'priority': calculate_priority(savings_per_month, 0.9),
            'analysis': {
                'status': 'IDLE',
                'recommendation': 'Stop or terminate idle instance',
                'reason': f'Instance has low CPU utilization ({cpu_avg:.1f}%) and minimal network activity',
                'current_cpu_utilization': cpu_avg,
                'current_network_in': network_in,
                'current_network_out': network_out,
                'estimated_monthly_savings': round(savings_per_month, 2),
                'confidence': 'HIGH'
            }
        }
        recommendations.append(recommendation)
    
    # Check if instance is underutilized
    elif state == 'running' and cpu_avg < 30 and cpu_max < 50:
        # Recommend right-sizing
        smaller_instances = {
            't3.xlarge': 't3.large',
            't3.large': 't3.medium',
            't3.medium': 't3.small',
            't3.small': 't3.micro'
        }
        
        if instance_type in smaller_instances:
            # Get pricing for smaller instance
            from cost_collection import get_real_ec2_pricing
            smaller_rate = get_real_ec2_pricing(smaller_instances[instance_type])
            savings_per_month = (hourly_rate - smaller_rate) * 24 * 30
            
            if savings_per_month > 10:
                recommendation = {
                    'service': 'ec2',
                    'resource_id': resource_id,
                    'resource_type': instance_type,
                    'priority': calculate_priority(savings_per_month, 0.7),
                    'analysis': {
                        'status': 'UNDERUTILIZED',
                        'recommendation': f'Downsize to {smaller_instances[instance_type]}',
                        'reason': f'Instance has low CPU utilization ({cpu_avg:.1f}%) and can be right-sized',
                        'current_cpu_utilization': cpu_avg,
                        'recommended_instance': smaller_instances[instance_type],
                        'current_hourly_rate': hourly_rate,
                        'recommended_hourly_rate': smaller_rate,
                        'estimated_monthly_savings': round(savings_per_month, 2),
                        'confidence': 'MEDIUM'
                    }
                }
                recommendations.append(recommendation)
    
    # Check if instance is stopped but still incurring costs (EBS volumes)
    elif state == 'stopped':
        recommendation = {
            'service': 'ec2',
            'resource_id': resource_id,
            'resource_type': instance_type,
            'priority': 'LOW',
            'analysis': {
                'status': 'STOPPED',
                'recommendation': 'Terminate if no longer needed',
                'reason': 'Instance is stopped but may still incur EBS costs',
                'estimated_monthly_savings': 0,
                'confidence': 'LOW'
            }
        }
        recommendations.append(recommendation)
    
    return recommendations

def analyze_s3_optimization(resource_data, metrics_data, cost_data):
    """Generate S3 optimization recommendations"""
    recommendations = []
    
    bucket_name = resource_data['resource_id']
    size_gb = resource_data.get('size_gb', 0)
    object_count = resource_data.get('object_count', 0)
    
    # Get metrics
    storage_trend = metrics_data.get('metrics', {}).get('storage', {}).get('trend', 'stable')
    requests_per_hour = metrics_data.get('metrics', {}).get('requests', {}).get('average_per_hour', 0)
    
    # Get cost data
    storage_cost = cost_data.get('storage_cost', 0)
    request_cost = cost_data.get('request_cost', 0)
    total_cost = cost_data.get('total_cost', 0)
    
    # Check for large buckets that could benefit from lifecycle policies
    if size_gb > 100:  # Large bucket
        # Estimate savings from moving old data to Glacier
        glacier_savings = storage_cost * 0.7 * 0.5  # 70% of data to Glacier, 50% savings
        recommendation = {
            'service': 's3',
            'resource_id': bucket_name,
            'resource_type': 'Bucket',
            'priority': calculate_priority(glacier_savings, 0.6),
            'analysis': {
                'status': 'LARGE_BUCKET',
                'recommendation': 'Implement S3 Lifecycle Policy',
                'reason': f'Large bucket ({size_gb:.1f}GB) could benefit from moving old data to Glacier',
                'current_size_gb': size_gb,
                'estimated_monthly_savings': round(glacier_savings, 2),
                'confidence': 'MEDIUM'
            }
        }
        recommendations.append(recommendation)
    
    # Check for buckets with low activity
    elif requests_per_hour < 1 and size_gb > 10:
        recommendation = {
            'service': 's3',
            'resource_id': bucket_name,
            'resource_type': 'Bucket',
            'priority': 'LOW',
            'analysis': {
                'status': 'LOW_ACTIVITY',
                'recommendation': 'Review bucket necessity',
                'reason': f'Bucket has minimal activity ({requests_per_hour:.1f} requests/hour)',
                'current_requests_per_hour': requests_per_hour,
                'estimated_monthly_savings': round(storage_cost, 2),
                'confidence': 'LOW'
            }
        }
        recommendations.append(recommendation)
    
    return recommendations

def analyze_rds_optimization(resource_data, metrics_data, cost_data):
    """Generate RDS optimization recommendations"""
    recommendations = []
    
    db_id = resource_data['resource_id']
    instance_class = resource_data['resource_type']
    engine = resource_data.get('engine', 'mysql')
    state = resource_data['state']
    
    # Get metrics
    cpu_avg = metrics_data.get('metrics', {}).get('cpu_utilization', {}).get('average', 0)
    connections_avg = metrics_data.get('metrics', {}).get('connections', {}).get('average', 0)
    storage_utilization = metrics_data.get('metrics', {}).get('storage', {}).get('utilization_percent', 0)
    
    # Get cost data
    hourly_rate = cost_data.get('hourly_rate', 0)
    storage_cost = cost_data.get('storage_cost', 0)
    total_cost = cost_data.get('total_cost', 0)
    
    # Check if database is underutilized
    if state == 'available' and cpu_avg < 15 and connections_avg < 5:
        # Recommend right-sizing
        smaller_instances = {
            'db.t3.large': 'db.t3.medium',
            'db.t3.medium': 'db.t3.small',
            'db.t3.small': 'db.t3.micro'
        }
        
        if instance_class in smaller_instances:
            # Get pricing for smaller instance
            from cost_collection import get_real_rds_pricing
            smaller_rate = get_real_rds_pricing(smaller_instances[instance_class], engine)
            savings_per_month = (hourly_rate - smaller_rate) * 24 * 30
            
            if savings_per_month > 20:
                recommendation = {
                    'service': 'rds',
                    'resource_id': db_id,
                    'resource_type': instance_class,
                    'priority': calculate_priority(savings_per_month, 0.7),
                    'analysis': {
                        'status': 'UNDERUTILIZED',
                        'recommendation': f'Downsize to {smaller_instances[instance_class]}',
                        'reason': f'Database has low CPU utilization ({cpu_avg:.1f}%) and few connections ({connections_avg:.1f})',
                        'current_cpu_utilization': cpu_avg,
                        'current_connections': connections_avg,
                        'recommended_instance': smaller_instances[instance_class],
                        'estimated_monthly_savings': round(savings_per_month, 2),
                        'confidence': 'MEDIUM'
                    }
                }
                recommendations.append(recommendation)
    
    # Check for storage optimization
    if storage_utilization < 20:  # Less than 20% storage used
        storage_savings = storage_cost * 0.5  # Potential 50% savings
        recommendation = {
            'service': 'rds',
            'resource_id': db_id,
            'resource_type': instance_class,
            'priority': 'LOW',
            'analysis': {
                'status': 'LOW_STORAGE_UTILIZATION',
                'recommendation': 'Reduce allocated storage',
                'reason': f'Database storage is underutilized ({storage_utilization:.1f}%)',
                'current_storage_utilization': storage_utilization,
                'estimated_monthly_savings': round(storage_savings, 2),
                'confidence': 'LOW'
            }
        }
        recommendations.append(recommendation)
    
    return recommendations

def generate_all_recommendations(inventory_data, metrics_data, cost_data):
    """Generate optimization recommendations for all resources"""
    logger.info("Starting optimization analysis...")
    
    all_recommendations = []
    
    # Create lookup dictionaries
    metrics_lookup = {m['resource_id']: m for m in metrics_data.get('resources', [])}
    cost_lookup = {c['resource_id']: c for c in cost_data.get('resources', [])}
    
    for resource in inventory_data['resources']:
        resource_id = resource['resource_id']
        service = resource['service']
        
        # Get corresponding metrics and cost data
        resource_metrics = metrics_lookup.get(resource_id, {})
        resource_cost = cost_lookup.get(resource_id, {})
        
        if service == 'ec2':
            recommendations = analyze_ec2_optimization(resource, resource_metrics, resource_cost)
            all_recommendations.extend(recommendations)
            
        elif service == 's3':
            recommendations = analyze_s3_optimization(resource, resource_metrics, resource_cost)
            all_recommendations.extend(recommendations)
            
        elif service == 'rds':
            recommendations = analyze_rds_optimization(resource, resource_metrics, resource_cost)
            all_recommendations.extend(recommendations)
    
    # Sort recommendations by priority and savings
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    all_recommendations.sort(key=lambda x: (priority_order.get(x['priority'], 3), -x['analysis'].get('estimated_monthly_savings', 0)))
    
    # Create summary
    summary = {
        'total_recommendations': len(all_recommendations),
        'high_priority': len([r for r in all_recommendations if r['priority'] == 'HIGH']),
        'medium_priority': len([r for r in all_recommendations if r['priority'] == 'MEDIUM']),
        'low_priority': len([r for r in all_recommendations if r['priority'] == 'LOW']),
        'total_estimated_monthly_savings': sum(r['analysis'].get('estimated_monthly_savings', 0) for r in all_recommendations),
        'recommendations_by_service': {
            'ec2': len([r for r in all_recommendations if r['service'] == 'ec2']),
            's3': len([r for r in all_recommendations if r['service'] == 's3']),
            'rds': len([r for r in all_recommendations if r['service'] == 'rds'])
        }
    }
    
    optimization_report = {
        'timestamp': datetime.utcnow().isoformat(),
        'summary': summary,
        'recommendations': all_recommendations
    }
    
    logger.info(f"Optimization analysis complete. Generated {len(all_recommendations)} recommendations with ${summary['total_estimated_monthly_savings']:.2f} potential savings")
    
    return optimization_report

if __name__ == "__main__":
    # Test the optimization engine
    from resource_discovery import discover_all_resources
    from metrics_collection import collect_all_metrics
    from cost_collection import collect_all_costs
    
    inventory = discover_all_resources()
    metrics = collect_all_metrics(inventory)
    costs = collect_all_costs(inventory)
    
    recommendations = generate_all_recommendations(inventory, metrics, costs)
    print(json.dumps(recommendations, indent=2, default=str))
