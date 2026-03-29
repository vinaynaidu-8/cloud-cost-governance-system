import boto3
from datetime import datetime, timedelta
import json

def normalize_service(service):
    service = service.lower()

    if "ec2" in service or "elastic compute" in service:
        return "ec2"
    elif "s3" in service:
        return "s3"
    elif "rds" in service:
        return "rds"
    elif "lambda" in service:
        return "lambda"
    else:
        return service

def main():
    client = boto3.client('ce', region_name='us-east-1')

    end = datetime.utcnow().date()
    start = end - timedelta(days=7)

    response = client.get_cost_and_usage(
        TimePeriod={'Start': str(start), 'End': str(end)},
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )

    service_costs = {}

    for result in response['ResultsByTime']:
        for group in result['Groups']:
            service = normalize_service(group['Keys'][0])
            amount = float(group['Metrics']['UnblendedCost']['Amount'])

            if service not in service_costs:
                service_costs[service] = 0

            service_costs[service] += amount

    resources = []

    for service, total in service_costs.items():
        weekly_cost = total
        resources.append({
            "service": service,
            "cost": {
                "last_7_days": round(weekly_cost, 4)
            }
        })

    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "resources": resources
    }

    with open("data/enhanced_cost_metrics.json", "w") as f:
        json.dump(data, f, indent=4)

    print("✅ Real AWS cost data collected successfully!")

if __name__ == "__main__":
    main()
