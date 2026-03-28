#!/usr/bin/env python3
"""
AWS Setup Script
Validates AWS credentials and permissions for the Cloud Cost Governance System
"""

import boto3
import json
import sys
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_credentials():
    """Test AWS credentials and permissions"""
    print("🔍 Testing AWS Credentials and Permissions...")
    print("-" * 50)
    
    try:
        # Test basic AWS connectivity
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"✅ AWS Credentials Valid")
        print(f"   Account ID: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")
        
        # Test required service permissions
        services_to_test = [
            ('EC2', 'ec2', 'describe_instances'),
            ('S3', 's3', 'list_buckets'),
            ('RDS', 'rds', 'describe_db_instances'),
            ('CloudWatch', 'cloudwatch', 'list_metrics'),
            ('Cost Explorer', 'ce', 'get_cost_and_usage'),
        ]
        
        print("\n🔐 Testing Service Permissions:")
        all_permissions_valid = True
        
        for service_name, service_name_boto, operation in services_to_test:
            try:
                if service_name == 'Cost Explorer':
                    client = boto3.client('ce')
                    # Test with minimal parameters
                    client.get_cost_and_usage(
                        TimePeriod={'Start': '2024-01-01', 'End': '2024-01-02'},
                        Granularity='DAILY',
                        Metrics=['BlendedCost'],
                        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
                    )
                elif service_name == 'CloudWatch':
                    client = boto3.client('cloudwatch')
                    client.list_metrics()
                elif service_name == 'EC2':
                    client = boto3.client('ec2')
                    client.describe_instances(MaxResults=5)
                elif service_name == 'S3':
                    client = boto3.client('s3')
                    client.list_buckets()
                elif service_name == 'RDS':
                    client = boto3.client('rds')
                    client.describe_db_instances(MaxRecords=5)
                
                print(f"   ✅ {service_name} - {operation}")
                
            except ClientError as e:
                if e.response['Error']['Code'] in ['AccessDenied', 'UnauthorizedOperation', 'Forbidden']:
                    print(f"   ❌ {service_name} - {operation}")
                    print(f"      Error: {e.response['Error']['Message']}")
                    all_permissions_valid = False
                else:
                    print(f"   ⚠️  {service_name} - {operation}")
                    print(f"      Warning: {e.response['Error']['Message']}")
            except Exception as e:
                print(f"   ⚠️  {service_name} - {operation}")
                print(f"      Warning: {str(e)}")
        
        if all_permissions_valid:
            print("\n🎉 All AWS permissions are valid!")
            return True
        else:
            print("\n⚠️  Some AWS permissions are missing.")
            print("   Please check IAM permissions and try again.")
            return False
            
    except NoCredentialsError:
        print("❌ AWS credentials not found!")
        print("   Please configure AWS credentials:")
        print("   1. Run 'aws configure'")
        print("   2. Or set environment variables:")
        print("      AWS_ACCESS_KEY_ID")
        print("      AWS_SECRET_ACCESS_KEY")
        print("      AWS_DEFAULT_REGION")
        return False
    except Exception as e:
        print(f"❌ Error testing AWS credentials: {str(e)}")
        return False

def check_cost_explorer_enabled():
    """Check if Cost Explorer is enabled"""
    print("\n💰 Checking Cost Explorer Status...")
    print("-" * 50)
    
    try:
        client = boto3.client('ce')
        
        # Try to get cost data for a recent date range
        try:
            response = client.get_cost_and_usage(
                TimePeriod={
                    'Start': '2024-01-01',
                    'End': '2024-01-02'
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            if response['ResultsByTime']:
                print("✅ Cost Explorer is enabled and accessible")
                return True
            else:
                print("⚠️  Cost Explorer is enabled but no data available")
                print("   This is normal for new accounts")
                return True
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDeniedException':
                print("❌ Cost Explorer is not enabled")
                print("   Please enable Cost Explorer in AWS Console:")
                print("   1. Go to AWS Cost Management Console")
                print("   2. Select Cost Explorer")
                print("   3. Click 'Enable Cost Explorer'")
                return False
            else:
                print(f"⚠️  Cost Explorer error: {e.response['Error']['Message']}")
                return False
                
    except Exception as e:
        print(f"❌ Error checking Cost Explorer: {str(e)}")
        return False

def generate_iam_policy():
    """Generate IAM policy document for required permissions"""
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:DescribeInstances",
                    "ec2:DescribeInstanceTypes",
                    "ec2:DescribeTags"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketLocation",
                    "s3:ListBucket",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "rds:DescribeDBInstances",
                    "rds:DescribeDBClusters"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ce:GetCostAndUsage",
                    "ce:GetDimensionValues",
                    "ce:GetTags"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "sts:GetCallerIdentity"
                ],
                "Resource": "*"
            }
        ]
    }
    
    print("\n📋 Required IAM Policy:")
    print("-" * 50)
    print(json.dumps(policy, indent=2))
    
    return policy

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 AWS Setup for Cloud Cost Governance System")
    print("=" * 60)
    
    # Test AWS credentials
    credentials_valid = test_aws_credentials()
    
    if not credentials_valid:
        print("\n❌ AWS setup failed!")
        sys.exit(1)
    
    # Check Cost Explorer
    cost_explorer_ok = check_cost_explorer_enabled()
    
    if not cost_explorer_ok:
        print("\n⚠️  Cost Explorer needs to be enabled")
        print("   You can still test the system with sample data")
    
    # Generate IAM policy
    generate_iam_policy()
    
    print("\n" + "=" * 60)
    print("✅ AWS Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run the pipeline: python pipeline/run_pipeline.py")
    print("2. Start dashboard: python web/app.py")
    print("3. Access dashboard: http://localhost:5000")

if __name__ == "__main__":
    main()
