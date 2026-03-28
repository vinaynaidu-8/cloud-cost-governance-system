import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        logger.error(f"Error discovering EC2 instances: {str(e)}")
    
    return resources

def discover_ebs_volumes() -> List[Dict[str, Any]]:
    """Discover all EBS volumes with detailed information"""
    resources = []
    
    try:
        ec2 = boto3.client('ec2')
        volumes = ec2.describe_volumes()
        
        for volume in volumes['Volumes']:
            volume_info = {
                "service": "ebs",
                "resource_id": volume['VolumeId'],
                "resource_type": f"{volume['VolumeType']} ({volume['Size']}GB)",
                "region": ec2.meta.region_name,
                "state": volume['State'],
                "size_gb": volume['Size'],
                "volume_type": volume['VolumeType'],
                "iops": volume.get('Iops', 'N/A'),
                "throughput": volume.get('Throughput', 'N/A'),
                "encrypted": volume['Encrypted'],
                "attached_to": volume.get('Attachments', []),
                "creation_time": volume['CreateTime'].isoformat() if 'CreateTime' in volume else 'N/A',
                "tags": {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])}
            }
            resources.append(volume_info)
            
        logger.info(f"Discovered {len(resources)} EBS volumes")
        
    except Exception as e:
        logger.error(f"Error discovering EBS volumes: {str(e)}")
    
    return resources

def discover_lambda_functions() -> List[Dict[str, Any]]:
    """Discover all Lambda functions with detailed information"""
    resources = []
    
    try:
        lambda_client = boto3.client('lambda')
        functions = lambda_client.list_functions()
        
        for func in functions['Functions']:
            func_info = {
                "service": "lambda",
                "resource_id": func['FunctionArn'],
                "resource_type": f"{func['Runtime']} ({func['MemorySize']}MB)",
                "region": lambda_client.meta.region_name,
                "state": "Active" if func['State'] == 'Active' else 'Inactive',
                "runtime": func['Runtime'],
                "memory_size": func['MemorySize'],
                "timeout": func['Timeout'],
                "code_size": func['CodeSize'],
                "last_modified": func['LastModified'],
                "tags": {tag['Key']: tag['Value'] for tag in func.get('Tags', [])}
            }
            resources.append(func_info)
            
        logger.info(f"Discovered {len(resources)} Lambda functions")
        
    except Exception as e:
        logger.error(f"Error discovering Lambda functions: {str(e)}")
    
    return resources

def discover_vpc_resources() -> List[Dict[str, Any]]:
    """Discover all VPC resources (VPCs, Subnets, NAT Gateways)"""
    resources = []
    
    try:
        ec2 = boto3.client('ec2')
        
        # Get VPCs
        vpcs = ec2.describe_vpcs()
        for vpc in vpcs['Vpcs']:
            vpc_info = {
                "service": "vpc",
                "resource_id": vpc['VpcId'],
                "resource_type": "VPC",
                "region": ec2.meta.region_name,
                "state": "Available",
                "cidr_block": vpc['CidrBlock'],
                "is_default": vpc['IsDefault'],
                "tags": {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])}
            }
            resources.append(vpc_info)
        
        # Get Subnets
        subnets = ec2.describe_subnets()
        for subnet in subnets['Subnets']:
            subnet_info = {
                "service": "vpc",
                "resource_id": subnet['SubnetId'],
                "resource_type": "Subnet",
                "region": ec2.meta.region_name,
                "state": subnet['State'],
                "vpc_id": subnet['VpcId'],
                "cidr_block": subnet['CidrBlock'],
                "available_ip_count": subnet['AvailableIpAddressCount'],
                "tags": {tag['Key']: tag['Value'] for tag in subnet.get('Tags', [])}
            }
            resources.append(subnet_info)
        
        # Get NAT Gateways
        nat_gateways = ec2.describe_nat_gateways()
        for nat in nat_gateways['NatGateways']:
            nat_info = {
                "service": "vpc",
                "resource_id": nat['NatGatewayId'],
                "resource_type": "NAT Gateway",
                "region": ec2.meta.region_name,
                "state": nat['State'],
                "vpc_id": nat['VpcId'],
                "subnet_id": nat['SubnetId'] if 'SubnetId' in nat else 'N/A',
                "tags": {tag['Key']: tag['Value'] for tag in nat.get('Tags', [])}
            }
            resources.append(nat_info)
            
        logger.info(f"Discovered {len(resources)} VPC resources")
        
    except Exception as e:
        logger.error(f"Error discovering VPC resources: {str(e)}")
    
    return resources

def discover_all_resources():
    """Main function to discover all AWS resources"""
    try:
        # Get account information
        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()["Account"]
        
        # Discover all resource types
        ec2_resources = discover_ec2_resources()
        ebs_volumes = discover_ebs_volumes()
        lambda_functions = discover_lambda_functions()
        vpc_resources = discover_vpc_resources()
        
        # Combine all resources
        all_resources = ec2_resources + ebs_volumes + lambda_functions + vpc_resources
        
        # Create inventory data structure
        data = {
            "account_id": account_id,
            "region": boto3.session.Session().region_name,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_resources": len(all_resources),
                "ec2_instances": len(ec2_resources),
                "ebs_volumes": len(ebs_volumes),
                "lambda_functions": len(lambda_functions),
                "vpc_resources": len(vpc_resources)
            },
            "resources": all_resources
        }
        
        # Save to file
        with open("data/inventory.json", "w") as f:
            json.dump(data, f, indent=4, default=str)
        
        logger.info(f"Successfully discovered {len(all_resources)} total resources")
        logger.info(f"Resource breakdown: {data['summary']}")
        
        return data
        
    except Exception as e:
        logger.error(f"Error in resource discovery: {str(e)}")
        return None

if __name__ == "__main__":
    discover_all_resources()
