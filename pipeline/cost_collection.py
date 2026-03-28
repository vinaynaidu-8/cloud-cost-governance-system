import boto3
import json
from datetime import datetime, timedelta
from config import AWS_REGION, DEFAULT_TIME_RANGE, COST_EXPLORER_ENABLED

logger = logging.getLogger(__name__)

def get_real_ec2_pricing(instance_type):
    """Get real EC2 pricing from AWS Pricing API"""
    try:
        pricing_client = boto3.client('pricing', region_name='us-east-1')
        
        response = pricing_client.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'}
            ],
            MaxResults=1
        )
        
        if response['PriceList']:
            price_list = json.loads(response['PriceList'][0])
            # Extract on-demand price
            for item in price_list['terms']['OnDemand'].values():
                for dimension in item['priceDimensions'].values():
                    if dimension['rateCode'].endswith('.USD'):
                        return float(dimension['pricePerUnit']['USD'])
        
        return 0.0
        
    except Exception as e:
        logger.error(f"Error getting EC2 pricing for {instance_type}: {str(e)}")
        return 0.0

def get_real_s3_pricing():
    """Get real S3 pricing from AWS Pricing API"""
    try:
        pricing_client = boto3.client('pricing', region_name='us-east-1')
        
        # Get S3 storage pricing
        response = pricing_client.get_products(
            ServiceCode='AmazonS3',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                {'Type': 'TERM_MATCH', 'Field': 'storageClass', 'Value': 'Standard'},
                {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Storage'}
            ],
            MaxResults=1
        )
        
        if response['PriceList']:
            price_list = json.loads(response['PriceList'][0])
            for item in price_list['terms']['OnDemand'].values():
                for dimension in item['priceDimensions'].values():
                    if dimension['rateCode'].endswith('.GB-Month'):
                        return float(dimension['pricePerUnit']['USD'])
        
        return 0.023  # Fallback to standard rate
        
    except Exception as e:
        logger.error(f"Error getting S3 pricing: {str(e)}")
        return 0.023

def get_real_rds_pricing(instance_class, engine='mysql'):
    """Get real RDS pricing from AWS Pricing API"""
    try:
        pricing_client = boto3.client('pricing', region_name='us-east-1')
        
        response = pricing_client.get_products(
            ServiceCode='AmazonRDS',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'instanceClass', 'Value': instance_class},
                {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': engine},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                {'Type': 'TERM_MATCH', 'Field': 'deploymentOption', 'Value': 'Single-AZ'}
            ],
            MaxResults=1
        )
        
        if response['PriceList']:
            price_list = json.loads(response['PriceList'][0])
            for item in price_list['terms']['OnDemand'].values():
                for dimension in item['priceDimensions'].values():
                    if dimension['rateCode'].endswith('.USD'):
                        return float(dimension['pricePerUnit']['USD'])
        
        return 0.0
        
    except Exception as e:
        logger.error(f"Error getting RDS pricing for {instance_class}: {str(e)}")
        return 0.0

def get_cost_explorer_costs(resource_type, resource_id, days=DEFAULT_TIME_RANGE):
    """Get actual costs from AWS Cost Explorer"""
    if not COST_EXPLORER_ENABLED:
        return 0.0
    
    try:
        ce = boto3.client('ce', region_name='us-east-1')
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build filters based on resource type
        if resource_type == 'ec2':
            dimension = 'EC2'
            filter_key = 'INSTANCE_TYPE'
        elif resource_type == 's3':
            dimension = 'S3'
            filter_key = 'BUCKET'
        elif resource_type == 'rds':
            dimension = 'RDS'
            filter_key = 'DB_INSTANCE_CLASS'
        else:
            return 0.0
        
        response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': dimension
                }
            ],
            Filter={
                'Dimensions': {
                    'Key': filter_key,
                    'Values': [resource_id] if resource_type != 's3' else []
                }
            }
        )
        
        total_cost = 0.0
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                amount = float(group['Metrics']['BlendedCost']['Amount'])
                total_cost += amount
        
        return total_cost
        
    except Exception as e:
        logger.error(f"Error getting Cost Explorer data for {resource_id}: {str(e)}")
        return 0.0

def calculate_ec2_cost(instance_data, days=DEFAULT_TIME_RANGE):
    """Calculate EC2 instance cost using real pricing"""
    try:
        instance_type = instance_data['resource_type']
        
        # Try to get actual cost from Cost Explorer first
        actual_cost = get_cost_explorer_costs('ec2', instance_data['resource_id'], days)
        if actual_cost > 0:
            return actual_cost
        
        # Fallback to pricing API
        hourly_rate = get_real_ec2_pricing(instance_type)
        
        # Calculate running hours
        if instance_data['state'] == 'running':
            # For running instances, assume 24/7 usage for the period
            running_hours = days * 24
        else:
            # For stopped instances, no cost
            running_hours = 0
        
        total_cost = hourly_rate * running_hours
        
        return {
            'hourly_rate': hourly_rate,
            'running_hours': running_hours,
            'total_cost': total_cost,
            'cost_source': 'pricing_api' if actual_cost == 0 else 'cost_explorer'
        }
        
    except Exception as e:
        logger.error(f"Error calculating EC2 cost: {str(e)}")
        return {'total_cost': 0.0, 'cost_source': 'error'}

def calculate_s3_cost(bucket_data, days=DEFAULT_TIME_RANGE):
    """Calculate S3 bucket cost using real pricing"""
    try:
        # Get real S3 pricing
        storage_price_per_gb = get_real_s3_pricing()
        
        # Calculate storage cost
        storage_gb = bucket_data.get('size_gb', 0)
        storage_cost = storage_gb * storage_price_per_gb * (days / 30)  # Monthly to daily
        
        # Estimate request costs (rough estimate)
        object_count = bucket_data.get('object_count', 0)
        request_cost = (object_count * 0.0004 / 10000) * days  # Rough estimate
        
        total_cost = storage_cost + request_cost
        
        return {
            'storage_cost': storage_cost,
            'request_cost': request_cost,
            'total_cost': total_cost,
            'cost_source': 'pricing_api'
        }
        
    except Exception as e:
        logger.error(f"Error calculating S3 cost: {str(e)}")
        return {'total_cost': 0.0, 'cost_source': 'error'}

def calculate_rds_cost(rds_data, days=DEFAULT_TIME_RANGE):
    """Calculate RDS instance cost using real pricing"""
    try:
        instance_class = rds_data['resource_type']
        engine = rds_data.get('engine', 'mysql')
        
        # Try to get actual cost from Cost Explorer first
        actual_cost = get_cost_explorer_costs('rds', rds_data['resource_id'], days)
        if actual_cost > 0:
            return actual_cost
        
        # Fallback to pricing API
        hourly_rate = get_real_rds_pricing(instance_class, engine)
        
        # Calculate running hours
        if rds_data['state'] == 'available':
            # For available instances, assume 24/7 usage
            running_hours = days * 24
        else:
            # For stopped instances, no cost
            running_hours = 0
        
        total_cost = hourly_rate * running_hours
        
        # Add storage cost
        storage_gb = rds_data.get('allocated_storage', 0)
        storage_cost = storage_gb * 0.115 * (days / 30)  # RDS storage cost
        
        total_cost += storage_cost
        
        return {
            'hourly_rate': hourly_rate,
            'running_hours': running_hours,
            'storage_cost': storage_cost,
            'total_cost': total_cost,
            'cost_source': 'pricing_api' if actual_cost == 0 else 'cost_explorer'
        }
        
    except Exception as e:
        logger.error(f"Error calculating RDS cost: {str(e)}")
        return {'total_cost': 0.0, 'cost_source': 'error'}

def collect_all_costs(inventory_data, days=DEFAULT_TIME_RANGE):
    """Collect costs for all resources using real AWS data"""
    logger.info(f"Starting cost collection for {days} days...")
    
    cost_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'period_days': days,
        'total_cost': 0.0,
        'costs_by_service': {},
        'resources': []
    }
    
    for resource in inventory_data['resources']:
        resource_cost = {'resource_id': resource['resource_id']}
        
        if resource['service'] == 'ec2':
            cost_info = calculate_ec2_cost(resource, days)
            resource_cost.update(cost_info)
            
        elif resource['service'] == 's3':
            cost_info = calculate_s3_cost(resource, days)
            resource_cost.update(cost_info)
            
        elif resource['service'] == 'rds':
            cost_info = calculate_rds_cost(resource, days)
            resource_cost.update(cost_info)
        
        else:
            resource_cost['total_cost'] = 0.0
            resource_cost['cost_source'] = 'unsupported'
        
        # Add service to cost breakdown
        service = resource['service']
        if service not in cost_data['costs_by_service']:
            cost_data['costs_by_service'][service] = 0.0
        
        resource_total = resource_cost.get('total_cost', 0.0)
        cost_data['costs_by_service'][service] += resource_total
        cost_data['total_cost'] += resource_total
        
        cost_data['resources'].append(resource_cost)
    
    logger.info(f"Cost collection complete. Total cost: ${cost_data['total_cost']:.2f}")
    return cost_data

def get_service_cost(service_name, days=7):
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)

    ce = boto3.client("ce")

    response = ce.get_cost_and_usage(
        TimePeriod={
            "Start": str(start),
            "End": str(end)
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        Filter={
            "Dimensions": {
                "Key": "SERVICE",
                "Values": [service_name]
            }
        }
    )

    total = 0

    for day in response["ResultsByTime"]:
        total += float(day["Total"]["UnblendedCost"]["Amount"])

    return round(total, 4)

def main():
    ec2_cost = get_service_cost(
        "Amazon Elastic Compute Cloud - Compute"
    )

    s3_cost = get_service_cost(
        "Amazon Simple Storage Service"
    )

    resources = [
        {
            "service": "ec2",
            "cost": {
                "last_7_days": ec2_cost
            }
        },
        {
            "service": "s3",
            "cost": {
                "last_7_days": s3_cost
            }
        }
    ]

    with open("data/cost_metrics_inventory.json", "w") as f:
        json.dump({"resources": resources}, f, indent=4)

    print("Cost collection completed.")
    print("EC2 Cost:", ec2_cost)
    print("S3 Cost:", s3_cost)

if __name__ == "__main__":
    main()
