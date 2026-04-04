from datetime import datetime, timedelta
import boto3

ce = boto3.client('ce', region_name='us-east-1')

end = datetime.utcnow().date()
start = end - timedelta(days=7)

response = ce.get_cost_and_usage(
    TimePeriod={
        'Start': str(start),
        'End': str(end)
    },
    Granularity='MONTHLY',
    Metrics=['UnblendedCost']
)

print(response)
