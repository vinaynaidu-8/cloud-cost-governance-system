import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AWS clients
ec2 = boto3.client("ec2")
s3 = boto3.client("s3")
rds = boto3.client("rds")
cloudwatch = boto3.client("cloudwatch")
ce = boto3.client("ce")
sts = boto3.client("sts")


def discover_ec2_resources() -> List[Dict[str, Any]]:
    """Discover all EC2 instances with detailed information"""
    resources = []
    
    try:
        paginator = ec2.get_paginator('describe_instances')
        for page in paginator.paginate():
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    # Get instance type information
                    instance_type = instance.get('InstanceType', 'unknown')
                    state = instance.get('State', {}).get('Name', 'unknown')
                    launch_time = instance.get('LaunchTime', datetime.utcnow())
                    
                    # Calculate running hours
                    running_hours = 0
                    if state == 'running':
                        running_hours = (datetime.utcnow() - launch_time).total_seconds() / 3600
                    
                    resources.append({
                        "service": "ec2",
                        "resource_id": instance["InstanceId"],
                        "resource_type": instance_type,
                        "region": ec2.meta.region_name,
                        "state": state,
                        "launch_time": launch_time.isoformat(),
                        "running_hours": round(running_hours, 2),
                        "tags": {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    })
        
        logger.info(f"Discovered {len(resources)} EC2 instances")
        
    except Exception as e:
        logger.error(f"Error discovering EC2 resources: {str(e)}")
    
    return resources


def discover_s3_resources() -> List[Dict[str, Any]]:
    """Discover all S3 buckets with size and object count"""
    resources = []
    
    try:
        paginator = s3.get_paginator('list_buckets')
        for page in paginator.paginate():
            for bucket in page['Buckets']:
                bucket_name = bucket['Name']
                creation_date = bucket['CreationDate']
                
                # Get bucket location
                try:
                    location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
                    if location is None:
                        location = 'us-east-1'
                except:
                    location = 'unknown'
                
                # Get bucket size (simplified - in production, use CloudWatch metrics)
                try:
                    size_bytes = 0
                    object_count = 0
                    
                    # Use CloudWatch for bucket size metrics
                    metrics = cloudwatch.list_metrics(
                        Namespace='AWS/S3',
                        MetricName='BucketSizeBytes',
                        Dimensions=[
                            {'Name': 'BucketName', 'Value': bucket_name},
                            {'Name': 'StorageType', 'Value': 'StandardStorage'}
                        ]
                    )
                    
                    if metrics['Metrics']:
                        response = cloudwatch.get_metric_statistics(
                            Namespace='AWS/S3',
                            MetricName='BucketSizeBytes',
                            Dimensions=[
                                {'Name': 'BucketName', 'Value': bucket_name},
                                {'Name': 'StorageType', 'Value': 'StandardStorage'}
                            ],
                            StartTime=datetime.utcnow() - timedelta(days=2),
                            EndTime=datetime.utcnow(),
                            Period=86400,
                            Statistics=['Average']
                        )
                        
                        if response['Datapoints']:
                            size_bytes = response['Datapoints'][-1]['Average']
                    
                    # Get object count
                    object_metrics = cloudwatch.list_metrics(
                        Namespace='AWS/S3',
                        MetricName='NumberOfObjects',
                        Dimensions=[
                            {'Name': 'BucketName', 'Value': bucket_name},
                            {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                        ]
                    )
                    
                    if object_metrics['Metrics']:
                        response = cloudwatch.get_metric_statistics(
                            Namespace='AWS/S3',
                            MetricName='NumberOfObjects',
                            Dimensions=[
                                {'Name': 'BucketName', 'Value': bucket_name},
                                {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                            ],
                            StartTime=datetime.utcnow() - timedelta(days=2),
                            EndTime=datetime.utcnow(),
                            Period=86400,
                            Statistics=['Average']
                        )
                        
                        if response['Datapoints']:
                            object_count = int(response['Datapoints'][-1]['Average'])
                    
                except Exception as e:
                    logger.warning(f"Could not get metrics for bucket {bucket_name}: {str(e)}")
                    size_bytes = 0
                    object_count = 0
                
                resources.append({
                    "service": "s3",
                    "resource_id": bucket_name,
                    "region": location,
                    "creation_date": creation_date.isoformat(),
                    "size_bytes": int(size_bytes),
                    "size_gb": round(size_bytes / (1024**3), 2),
                    "object_count": object_count
                })
        
        logger.info(f"Discovered {len(resources)} S3 buckets")
        
    except Exception as e:
        logger.error(f"Error discovering S3 resources: {str(e)}")
    
    return resources


def discover_rds_resources() -> List[Dict[str, Any]]:
    """Discover all RDS instances with detailed information"""
    resources = []
    
    try:
        paginator = rds.get_paginator('describe_db_instances')
        for page in paginator.paginate():
            for db_instance in page['DBInstances']:
                instance_id = db_instance['DBInstanceIdentifier']
                instance_class = db_instance['DBInstanceClass']
                engine = db_instance['Engine']
                status = db_instance['DBInstanceStatus']
                creation_time = db_instance['InstanceCreateTime']
                
                # Calculate running hours
                running_hours = 0
                if status == 'available':
                    running_hours = (datetime.utcnow() - creation_time.replace(tzinfo=None)).total_seconds() / 3600
                
                resources.append({
                    "service": "rds",
                    "resource_id": instance_id,
                    "resource_type": instance_class,
                    "region": rds.meta.region_name,
                    "engine": engine,
                    "status": status,
                    "creation_time": creation_time.isoformat(),
                    "running_hours": round(running_hours, 2),
                    "allocated_storage": db_instance.get('AllocatedStorage', 0),
                    "storage_type": db_instance.get('StorageType', 'unknown')
                })
        
        logger.info(f"Discovered {len(resources)} RDS instances")
        
    except Exception as e:
        logger.error(f"Error discovering RDS resources: {str(e)}")
    
    return resources


def discover_ec2_instances():
    """Discover real EC2 instances from AWS"""
    try:
        ec2 = boto3.client('ec2', region_name='us-east-1')
        instances = ec2.describe_instances()
        
        ec2_resources = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                # Get real instance details
                instance_data = {
                    'service': 'ec2',
                    'resource_id': instance['InstanceId'],
                    'resource_type': instance['InstanceType'],
                    'state': instance['State']['Name'],
                    'region': 'us-east-1',
                    'launch_time': instance['LaunchTime'].isoformat(),
                    'availability_zone': instance['Placement']['AvailabilityZone'],
                    'vpc_id': instance.get('VpcId', 'N/A'),
                    'subnet_id': instance.get('SubnetId', 'N/A'),
                    'security_groups': [sg['GroupId'] for sg in instance.get('SecurityGroups', [])],
                    'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                }
                ec2_resources.append(instance_data)
        
        logger.info(f"Discovered {len(ec2_resources)} EC2 instances")
        return ec2_resources
        
    except Exception as e:
        logger.error(f"Error discovering EC2 instances: {str(e)}")
        return []


def discover_s3_buckets():
    """Discover real S3 buckets from AWS"""
    try:
        s3 = boto3.client('s3', region_name='us-east-1')
        buckets = s3.list_buckets()
        
        s3_resources = []
        for bucket in buckets['Buckets']:
            # Get real bucket details
            try:
                # Get bucket location
                location = s3.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint'] or 'us-east-1'
                
                # Get bucket size and object count
                cloudwatch = boto3.client('cloudwatch', region_name=location)
                
                # Get bucket size
                size_metrics = cloudwatch.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName='BucketSizeBytes',
                    Dimensions=[{'Name': 'BucketName', 'Value': bucket['Name']}],
                    StartTime=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                    EndTime=datetime.utcnow(),
                    Period=86400,
                    Statistics=['Average']
                )
                
                # Get object count
                object_metrics = cloudwatch.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName='NumberOfObjects',
                    Dimensions=[{'Name': 'BucketName', 'Value': bucket['Name']}],
                    StartTime=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                    EndTime=datetime.utcnow(),
                    Period=86400,
                    Statistics=['Average']
                )
                
                size_bytes = size_metrics['Datapoints'][-1]['Average'] if size_metrics['Datapoints'] else 0
                object_count = object_metrics['Datapoints'][-1]['Average'] if object_metrics['Datapoints'] else 0
                
                bucket_data = {
                    'service': 's3',
                    'resource_id': bucket['Name'],
                    'region': location,
                    'creation_date': bucket['CreationDate'].isoformat(),
                    'size_bytes': size_bytes,
                    'size_gb': round(size_bytes / (1024**3), 2),
                    'object_count': int(object_count),
                    'tags': {}
                }
                
                # Get bucket tags
                try:
                    tags = s3.get_bucket_tagging(Bucket=bucket['Name'])
                    bucket_data['tags'] = {tag['Key']: tag['Value'] for tag in tags.get('TagSet', [])}
                except:
                    pass
                
                s3_resources.append(bucket_data)
                
            except Exception as e:
                logger.warning(f"Could not get detailed metrics for bucket {bucket['Name']}: {str(e)}")
                # Add basic bucket info without metrics
                s3_resources.append({
                    'service': 's3',
                    'resource_id': bucket['Name'],
                    'region': 'us-east-1',
                    'creation_date': bucket['CreationDate'].isoformat(),
                    'size_bytes': 0,
                    'size_gb': 0,
                    'object_count': 0,
                    'tags': {}
                })
        
        logger.info(f"Discovered {len(s3_resources)} S3 buckets")
        return s3_resources
        
    except Exception as e:
        logger.error(f"Error discovering S3 buckets: {str(e)}")
        return []


def discover_rds_instances():
    """Discover real RDS instances from AWS"""
    try:
        rds = boto3.client('rds', region_name='us-east-1')
        instances = rds.describe_db_instances()
        
        rds_resources = []
        for db in instances['DBInstances']:
            db_data = {
                'service': 'rds',
                'resource_id': db['DBInstanceIdentifier'],
                'resource_type': db['DBInstanceClass'],
                'state': db['DBInstanceStatus'],
                'region': 'us-east-1',
                'engine': db['Engine'],
                'engine_version': db['EngineVersion'],
                'allocated_storage': db['AllocatedStorage'],
                'storage_type': db['StorageType'],
                'multi_az': db['MultiAZ'],
                'creation_time': db['InstanceCreateTime'].isoformat(),
                'vpc_id': db.get('DBSubnetGroup', {}).get('VpcId', 'N/A'),
                'tags': {tag['Key']: tag['Value'] for tag in db.get('TagList', [])}
            }
            rds_resources.append(db_data)
        
        logger.info(f"Discovered {len(rds_resources)} RDS instances")
        return rds_resources
        
    except Exception as e:
        logger.error(f"Error discovering RDS instances: {str(e)}")
        return []


def discover_all_resources():
    """Discover all AWS resources"""
    logger.info("Starting AWS resource discovery...")
    
    all_resources = []
    
    # Discover each service
    all_resources.extend(discover_ec2_instances())
    all_resources.extend(discover_s3_buckets())
    all_resources.extend(discover_rds_instances())
    
    # Create inventory structure
    inventory = {
        'account_id': boto3.client('sts').get_caller_identity()['Account'],
        'region': 'us-east-1',
        'timestamp': datetime.utcnow().isoformat(),
        'summary': {
            'total_resources': len(all_resources),
            'ec2_instances': len([r for r in all_resources if r['service'] == 'ec2']),
            's3_buckets': len([r for r in all_resources if r['service'] == 's3']),
            'rds_instances': len([r for r in all_resources if r['service'] == 'rds'])
        },
        'resources': all_resources
    }
    
    logger.info(f"Discovery complete. Found {len(all_resources)} total resources")
    return inventory


def main():
    """Main function to discover all AWS resources"""
    logger.info("Starting AWS resource discovery...")
    
    try:
        # Get account information
        account_id = sts.get_caller_identity()["Account"]
        region = ec2.meta.region_name
        
        # Discover all resource types
        ec2_resources = discover_ec2_resources()
        s3_resources = discover_s3_resources()
        rds_resources = discover_rds_resources()
        
        # Combine all resources
        all_resources = ec2_resources + s3_resources + rds_resources
        
        # Create inventory data structure
        data = {
            "account_id": account_id,
            "region": region,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_resources": len(all_resources),
                "ec2_instances": len(ec2_resources),
                "s3_buckets": len(s3_resources),
                "rds_instances": len(rds_resources)
            },
            "resources": all_resources
        }
        
        # Ensure data directory exists
        import os
        os.makedirs("data", exist_ok=True)
        
        # Save to file
        with open("data/inventory.json", "w") as f:
            json.dump(data, f, indent=4, default=str)
        
        logger.info(f"Resource discovery completed successfully.")
        logger.info(f"Total resources discovered: {len(all_resources)}")
        logger.info(f"EC2 instances: {len(ec2_resources)}")
        logger.info(f"S3 buckets: {len(s3_resources)}")
        logger.info(f"RDS instances: {len(rds_resources)}")
        
    except Exception as e:
        logger.error(f"Error in resource discovery: {str(e)}")
        raise


if __name__ == "__main__":
    main()
