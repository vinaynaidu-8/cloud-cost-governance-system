import boto3
import json
import logging
from datetime import datetime, timedelta
from config import AWS_REGION, DEFAULT_TIME_RANGE, METRICS_PERIOD

logger = logging.getLogger(__name__)

def get_cloudwatch_metrics(resource_id, namespace, metric_name, dimensions, days=DEFAULT_TIME_RANGE):
    """Get real metrics from CloudWatch"""
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
        network_in_metrics = get_cloudwatch_metrics(
            instance_id,
            'AWS/EC2',
            'NetworkIn',
            [{'Name': 'InstanceId', 'Value': instance_id}],
            days
        )
        
        network_out_metrics = get_cloudwatch_metrics(
            instance_id,
            'AWS/EC2',
            'NetworkOut',
            [{'Name': 'InstanceId', 'Value': instance_id}],
            days
        )
        
        # Process metrics data
        processed_metrics = {
            'resource_id': instance_id,
            'service': 'ec2',
            'metrics': {
                'cpu_utilization': {
                    'average': round(sum(dp['Average'] for dp in cpu_metrics) / len(cpu_metrics), 2) if cpu_metrics else 0.0,
                    'maximum': max(dp['Maximum'] for dp in cpu_metrics) if cpu_metrics else 0.0,
                    'minimum': min(dp['Minimum'] for dp in cpu_metrics) if cpu_metrics else 0.0,
                    'datapoints': len(cpu_metrics)
                },
                'network': {
                    'in_mb_per_hour': round(sum(dp['Average'] for dp in network_in_metrics) / len(network_in_metrics) / (1024*1024), 2) if network_in_metrics else 0.0,
                    'out_mb_per_hour': round(sum(dp['Average'] for dp in network_out_metrics) / len(network_out_metrics) / (1024*1024), 2) if network_out_metrics else 0.0,
                    'datapoints': len(network_in_metrics) + len(network_out_metrics)
                }
            }
        }
        
        logger.info(f"Collected EC2 metrics for {instance_id}: CPU {processed_metrics['metrics']['cpu_utilization']['average']}%")
        return processed_metrics
        
    except Exception as e:
        logger.error(f"Error collecting EC2 metrics for {instance_data['resource_id']}: {str(e)}")
        return {
            'resource_id': instance_data['resource_id'],
            'service': 'ec2',
            'metrics': {
                'cpu_utilization': {'average': 0.0, 'maximum': 0.0, 'minimum': 0.0, 'datapoints': 0},
                'network': {'in_mb_per_hour': 0.0, 'out_mb_per_hour': 0.0, 'datapoints': 0}
            }
        }

def collect_s3_metrics(bucket_data, days=DEFAULT_TIME_RANGE):
    """Collect real S3 metrics from CloudWatch"""
    try:
        bucket_name = bucket_data['resource_id']
        
        # Get bucket size metrics
        size_metrics = get_cloudwatch_metrics(
            bucket_name,
            'AWS/S3',
            'BucketSizeBytes',
            [
                {'Name': 'BucketName', 'Value': bucket_name},
                {'Name': 'StorageType', 'Value': 'StandardStorage'}
            ],
            days
        )
        
        # Get object count metrics
        count_metrics = get_cloudwatch_metrics(
            bucket_name,
            'AWS/S3',
            'NumberOfObjects',
            [
                {'Name': 'BucketName', 'Value': bucket_name},
                {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
            ],
            days
        )
        
        # Get request metrics
        get_requests = get_cloudwatch_metrics(
            bucket_name,
            'AWS/S3',
            'GetRequests',
            [{'Name': 'BucketName', 'Value': bucket_name}],
            days
        )
        
        put_requests = get_cloudwatch_metrics(
            bucket_name,
            'AWS/S3',
            'PutRequests',
            [{'Name': 'BucketName', 'Value': bucket_name}],
            days
        )
        
        # Process metrics
        total_size_gb = sum(dp['Average'] for dp in size_metrics) / (1024**3) if size_metrics else 0.0
        total_objects = sum(dp['Average'] for dp in count_metrics) if count_metrics else 0
        total_get_requests = sum(dp['Sum'] for dp in get_requests) if get_requests else 0
        total_put_requests = sum(dp['Sum'] for dp in put_requests) if put_requests else 0
        
        processed_metrics = {
            'resource_id': bucket_name,
            'service': 's3',
            'metrics': {
                'storage': {
                    'size_gb': round(total_size_gb, 2),
                    'object_count': total_objects,
                    'datapoints': len(size_metrics) + len(count_metrics)
                },
                'requests': {
                    'total_get_requests': total_get_requests,
                    'total_put_requests': total_put_requests,
                    'average_per_hour': round((total_get_requests + total_put_requests) / (days * 24), 2) if days > 0 else 0,
                    'datapoints': len(get_requests) + len(put_requests)
                }
            }
        }
        
        logger.info(f"Collected S3 metrics for {bucket_name}: {total_size_gb:.2f}GB, {total_objects} objects")
        return processed_metrics
        
    except Exception as e:
        logger.error(f"Error collecting S3 metrics for {bucket_data['resource_id']}: {str(e)}")
        return {
            'resource_id': bucket_data['resource_id'],
            'service': 's3',
            'metrics': {
                'storage': {'size_gb': 0.0, 'object_count': 0, 'datapoints': 0},
                'requests': {'total_get_requests': 0, 'total_put_requests': 0, 'average_per_hour': 0, 'datapoints': 0}
            }
        }

def collect_rds_metrics(db_data, days=DEFAULT_TIME_RANGE):
    """Collect real RDS metrics from CloudWatch"""
    try:
        db_id = db_data['resource_id']
        
        # Get CPU utilization
        cpu_metrics = get_cloudwatch_metrics(
            db_id,
            'AWS/RDS',
            'CPUUtilization',
            [{'Name': 'DBInstanceIdentifier', 'Value': db_id}],
            days
        )
        
        # Get memory metrics
        memory_metrics = get_cloudwatch_metrics(
            db_id,
            'AWS/RDS',
            'FreeableMemory',
            [{'Name': 'DBInstanceIdentifier', 'Value': db_id}],
            days
        )
        
        # Get connection metrics
        connection_metrics = get_cloudwatch_metrics(
            db_id,
            'AWS/RDS',
            'DatabaseConnections',
            [{'Name': 'DBInstanceIdentifier', 'Value': db_id}],
            days
        )
        
        # Process metrics
        avg_cpu = sum(dp['Average'] for dp in cpu_metrics) / len(cpu_metrics) if cpu_metrics else 0.0
        avg_memory = sum(dp['Average'] for dp in memory_metrics) / len(memory_metrics) if memory_metrics else 0.0
        avg_connections = sum(dp['Average'] for dp in connection_metrics) / len(connection_metrics) if connection_metrics else 0.0
        
        processed_metrics = {
            'resource_id': db_id,
            'service': 'rds',
            'metrics': {
                'cpu_utilization': {
                    'average': round(avg_cpu, 2),
                    'maximum': max(dp['Maximum'] for dp in cpu_metrics) if cpu_metrics else 0.0,
                    'datapoints': len(cpu_metrics)
                },
                'memory': {
                    'freeable_memory_gb': round(avg_memory / (1024**3), 2),
                    'datapoints': len(memory_metrics)
                },
                'connections': {
                    'average': round(avg_connections, 2),
                    'datapoints': len(connection_metrics)
                }
            }
        }
        
        logger.info(f"Collected RDS metrics for {db_id}: CPU {avg_cpu:.2f}%, Connections {avg_connections:.1f}")
        return processed_metrics
        
    except Exception as e:
        logger.error(f"Error collecting RDS metrics for {db_data['resource_id']}: {str(e)}")
        return {
            'resource_id': db_data['resource_id'],
            'service': 'rds',
            'metrics': {
                'cpu_utilization': {'average': 0.0, 'maximum': 0.0, 'datapoints': 0},
                'memory': {'freeable_memory_gb': 0.0, 'datapoints': 0},
                'connections': {'average': 0.0, 'datapoints': 0}
            }
        }

def main():
    """Main function to collect all metrics"""
    logger.info("Starting metrics collection...")
    
    # Load inventory data
    import os
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    inventory_file = os.path.join(data_dir, 'inventory.json')
    
    try:
        with open(inventory_file, 'r') as f:
            inventory_data = json.load(f)
        
        resources = inventory_data.get('resources', [])
        logger.info(f"Loaded {len(resources)} resources from inventory")
        
    except FileNotFoundError:
        logger.error("Inventory file not found. Please run resource discovery first.")
        return
    except Exception as e:
        logger.error(f"Error loading inventory: {str(e)}")
        return
    
    # Collect metrics for each resource
    all_metrics = []
    
    for resource in resources:
        service = resource.get('service')
        
        if service == 'ec2':
            metrics = collect_ec2_metrics(resource)
            all_metrics.append(metrics)
            
        elif service == 's3':
            metrics = collect_s3_metrics(resource)
            all_metrics.append(metrics)
            
        elif service == 'rds':
            metrics = collect_rds_metrics(resource)
            all_metrics.append(metrics)
    
    # Save metrics data
    metrics_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'collection_period_days': DEFAULT_TIME_RANGE,
        'total_resources': len(all_metrics),
        'resources': all_metrics
    }
    
    output_file = os.path.join(data_dir, 'metrics_inventory.json')
    with open(output_file, 'w') as f:
        json.dump(metrics_data, f, indent=2, default=str)
    
    logger.info(f"Metrics collection completed. Results saved to {output_file}")
    logger.info(f"Collected metrics for {len(all_metrics)} resources")
    
    return metrics_data

if __name__ == "__main__":
    main()
