import boto3
import json
import logging
from datetime import datetime, timedelta
from config import AWS_REGION, DEFAULT_TIME_RANGE, METRICS_PERIOD, CLOUDWATCH_ENABLED

logger = logging.getLogger(__name__)

def get_cloudwatch_metrics(resource_id, namespace, metric_name, dimensions, days=DEFAULT_TIME_RANGE):
    """Get metrics from CloudWatch"""
    if not CLOUDWATCH_ENABLED:
        return []
    
    try:
        cloudwatch = boto3.client('cloudwatch', region_name=AWS_REGION)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=METRICS_PERIOD,
            Statistics=['Average', 'Maximum', 'Minimum']
        )
        
        return response['Datapoints']
        
    except Exception as e:
        logger.error(f"Error getting CloudWatch metrics for {resource_id}: {str(e)}")
        return []

def collect_ec2_metrics(instance_data, days=DEFAULT_TIME_RANGE):
    """Collect real EC2 performance metrics from CloudWatch"""
    try:
        instance_id = instance_data['resource_id']
        
        # Get CPU utilization
        cpu_metrics = get_cloudwatch_metrics(
            instance_id,
            'AWS/EC2',
            'CPUUtilization',
            [{'Name': 'InstanceId', 'Value': instance_id}],
            days
        )
        
        # Get network metrics
        network_in = get_cloudwatch_metrics(
            instance_id,
            'AWS/EC2',
            'NetworkIn',
            [{'Name': 'InstanceId', 'Value': instance_id}],
            days
        )
        
        network_out = get_cloudwatch_metrics(
            instance_id,
            'AWS/EC2',
            'NetworkOut',
            [{'Name': 'InstanceId', 'Value': instance_id}],
            days
        )
        
        # Calculate averages
        avg_cpu = sum([m['Average'] for m in cpu_metrics]) / len(cpu_metrics) if cpu_metrics else 0
        max_cpu = max([m['Maximum'] for m in cpu_metrics]) if cpu_metrics else 0
        avg_network_in = sum([m['Average'] for m in network_in]) / len(network_in) if network_in else 0
        avg_network_out = sum([m['Average'] for m in network_out]) / len(network_out) if network_out else 0
        
        # Determine if instance is idle
        is_idle = avg_cpu < 5.0 and avg_network_in < 1048576 and avg_network_out < 1048576  # <5% CPU and <1MB network
        
        metrics_data = {
            'resource_id': instance_id,
            'service': 'ec2',
            'metrics': {
                'cpu_utilization': {
                    'average': round(avg_cpu, 2),
                    'maximum': round(max_cpu, 2),
                    'datapoints': len(cpu_metrics)
                },
                'network': {
                    'in_mb_per_hour': round(avg_network_in / (1024*1024), 2),
                    'out_mb_per_hour': round(avg_network_out / (1024*1024), 2)
                },
                'status': 'idle' if is_idle else 'active',
                'data_points': len(cpu_metrics),
                'period_days': days
            }
        }
        
        logger.info(f"EC2 {instance_id}: CPU {avg_cpu:.1f}%, Network {avg_network_in/1024/1024:.1f}MB in, Status: {metrics_data['metrics']['status']}")
        
        return metrics_data
        
    except Exception as e:
        logger.error(f"Error collecting EC2 metrics: {str(e)}")
        return {'resource_id': instance_data['resource_id'], 'service': 'ec2', 'metrics': {}}

def collect_s3_metrics(bucket_data, days=DEFAULT_TIME_RANGE):
    """Collect real S3 metrics from CloudWatch"""
    try:
        bucket_name = bucket_data['resource_id']
        
        # Get S3 storage metrics
        size_metrics = get_cloudwatch_metrics(
            bucket_name,
            'AWS/S3',
            'BucketSizeBytes',
            [{'Name': 'BucketName', 'Value': bucket_name}],
            days
        )
        
        # Get object count metrics
        object_metrics = get_cloudwatch_metrics(
            bucket_name,
            'AWS/S3',
            'NumberOfObjects',
            [{'Name': 'BucketName', 'Value': bucket_name}],
            days
        )
        
        # Get request metrics
        get_requests = get_cloudwatch_metrics(
            bucket_name,
            'AWS/S3',
            'AllRequests',
            [{'Name': 'BucketName', 'Value': bucket_name}],
            days
        )
        
        # Calculate averages
        avg_size_gb = sum([m['Average'] for m in size_metrics]) / len(size_metrics) if size_metrics else 0
        avg_object_count = sum([m['Average'] for m in object_metrics]) / len(object_metrics) if object_metrics else 0
        avg_requests = sum([m['Average'] for m in get_requests]) / len(get_requests) if get_requests else 0
        
        metrics_data = {
            'resource_id': bucket_name,
            'service': 's3',
            'metrics': {
                'storage': {
                    'average_size_gb': round(avg_size_gb / (1024**3), 2),
                    'trend': 'growing' if len(size_metrics) > 1 and size_metrics[-1]['Average'] > size_metrics[0]['Average'] else 'stable'
                },
                'objects': {
                    'average_count': int(avg_object_count),
                    'trend': 'growing' if len(object_metrics) > 1 and object_metrics[-1]['Average'] > object_metrics[0]['Average'] else 'stable'
                },
                'requests': {
                    'average_per_hour': round(avg_requests, 2),
                    'total_requests': sum([m['Average'] for m in get_requests])
                },
                'data_points': len(size_metrics),
                'period_days': days
            }
        }
        
        logger.info(f"S3 {bucket_name}: {avg_size_gb/1024**3:.1f}GB, {avg_object_count:.0f} objects, {avg_requests:.0f} requests/hour")
        
        return metrics_data
        
    except Exception as e:
        logger.error(f"Error collecting S3 metrics: {str(e)}")
        return {'resource_id': bucket_data['resource_id'], 'service': 's3', 'metrics': {}}

def collect_rds_metrics(rds_data, days=DEFAULT_TIME_RANGE):
    """Collect real RDS performance metrics from CloudWatch"""
    try:
        db_instance_id = rds_data['resource_id']
        
        # Get CPU utilization
        cpu_metrics = get_cloudwatch_metrics(
            db_instance_id,
            'AWS/RDS',
            'CPUUtilization',
            [{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
            days
        )
        
        # Get memory utilization (if available)
        memory_metrics = get_cloudwatch_metrics(
            db_instance_id,
            'AWS/RDS',
            'FreeableMemory',
            [{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
            days
        )
        
        # Get database connections
        connection_metrics = get_cloudwatch_metrics(
            db_instance_id,
            'AWS/RDS',
            'DatabaseConnections',
            [{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
            days
        )
        
        # Get storage metrics
        storage_metrics = get_cloudwatch_metrics(
            db_instance_id,
            'AWS/RDS',
            'FreeStorageSpace',
            [{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
            days
        )
        
        # Calculate averages
        avg_cpu = sum([m['Average'] for m in cpu_metrics]) / len(cpu_metrics) if cpu_metrics else 0
        max_cpu = max([m['Maximum'] for m in cpu_metrics]) if cpu_metrics else 0
        avg_memory = sum([m['Average'] for m in memory_metrics]) / len(memory_metrics) if memory_metrics else 0
        avg_connections = sum([m['Average'] for m in connection_metrics]) / len(connection_metrics) if connection_metrics else 0
        avg_storage = sum([m['Average'] for m in storage_metrics]) / len(storage_metrics) if storage_metrics else 0
        
        # Determine if database is underutilized
        is_underutilized = avg_cpu < 10.0 and avg_connections < 5
        
        metrics_data = {
            'resource_id': db_instance_id,
            'service': 'rds',
            'metrics': {
                'cpu_utilization': {
                    'average': round(avg_cpu, 2),
                    'maximum': round(max_cpu, 2),
                    'datapoints': len(cpu_metrics)
                },
                'memory': {
                    'freeable_mb': round(avg_memory / (1024*1024), 2),
                    'utilization_percent': round((1 - avg_memory / (rds_data.get('allocated_storage', 100) * 1024**3)) * 100, 2)
                },
                'connections': {
                    'average': round(avg_connections, 2),
                    'maximum': max([m['Maximum'] for m in connection_metrics]) if connection_metrics else 0
                },
                'storage': {
                    'free_gb': round(avg_storage / (1024**3), 2),
                    'utilization_percent': round((1 - avg_storage / (rds_data.get('allocated_storage', 100) * 1024**3)) * 100, 2)
                },
                'status': 'underutilized' if is_underutilized else 'active',
                'data_points': len(cpu_metrics),
                'period_days': days
            }
        }
        
        logger.info(f"RDS {db_instance_id}: CPU {avg_cpu:.1f}%, Connections {avg_connections:.1f}, Status: {metrics_data['metrics']['status']}")
        
        return metrics_data
        
    except Exception as e:
        logger.error(f"Error collecting RDS metrics: {str(e)}")
        return {'resource_id': rds_data['resource_id'], 'service': 'rds', 'metrics': {}}

def collect_all_metrics(inventory_data, days=DEFAULT_TIME_RANGE):
    """Collect metrics for all AWS resources using real CloudWatch data"""
    logger.info(f"Starting metrics collection for {days} days...")
    
    metrics_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'period_days': days,
        'metrics_by_service': {},
        'resources': []
    }
    
    for resource in inventory_data['resources']:
        resource_metrics = {'resource_id': resource['resource_id']}
        
        if resource['service'] == 'ec2':
            metrics_info = collect_ec2_metrics(resource, days)
            resource_metrics.update(metrics_info)
            
        elif resource['service'] == 's3':
            metrics_info = collect_s3_metrics(resource, days)
            resource_metrics.update(metrics_info)
            
        elif resource['service'] == 'rds':
            metrics_info = collect_rds_metrics(resource, days)
            resource_metrics.update(metrics_info)
        
        else:
            resource_metrics['metrics'] = {}
            resource_metrics['service'] = resource['service']
        
        # Add service to metrics breakdown
        service = resource['service']
        if service not in metrics_data['metrics_by_service']:
            metrics_data['metrics_by_service'][service] = {
                'resources_count': 0,
                'active_resources': 0,
                'idle_resources': 0
            }
        
        metrics_data['metrics_by_service'][service]['resources_count'] += 1
        
        # Count active vs idle resources
        if 'status' in resource_metrics.get('metrics', {}):
            if resource_metrics['metrics']['status'] in ['idle', 'underutilized']:
                metrics_data['metrics_by_service'][service]['idle_resources'] += 1
            else:
                metrics_data['metrics_by_service'][service]['active_resources'] += 1
        
        metrics_data['resources'].append(resource_metrics)
    
    logger.info(f"Metrics collection complete. Collected metrics for {len(metrics_data['resources'])} resources")
    return metrics_data

def main():
    inventory = load_inventory()
    region = inventory["region"]

    enriched_resources = []

    for r in inventory["resources"]:

        if r["service"] == "ec2":

            metrics = collect_ec2_metrics(
                r,
                1
            )

            r["metrics"] = metrics

        enriched_resources.append(r)

    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "resources": enriched_resources
    }

    with open("data/metrics_inventory.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Metrics collection completed.")
    print("Resources processed:", len(enriched_resources))

def load_inventory():
    with open("data/inventory.json") as f:
        return json.load(f)

if __name__ == "__main__":
    main()
