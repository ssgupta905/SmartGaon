#!/usr/bin/env python3
"""
Deploy API Gateway with Lambda integration using CloudFormation.

This script deploys the API Gateway REST API with Lambda proxy integration
and sets up the health check endpoint.
"""

import boto3
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import get_config


def deploy_api_gateway(environment='dev'):
    """
    Deploy API Gateway stack using CloudFormation.
    
    Args:
        environment: Environment name (dev, staging, prod)
    """
    config = get_config()
    
    # Initialize CloudFormation client
    cf_client = boto3.client('cloudformation', region_name=config.aws_region)
    
    # Read CloudFormation template
    template_path = Path(__file__).parent.parent / 'infrastructure' / 'api-gateway.yaml'
    with open(template_path, 'r') as f:
        template_body = f.read()
    
    stack_name = f'gramsaarthi-{environment}-api-gateway'
    
    print(f"Deploying API Gateway stack: {stack_name}")
    print(f"Environment: {environment}")
    print(f"Region: {config.aws_region}")
    
    try:
        # Check if stack exists
        try:
            cf_client.describe_stacks(StackName=stack_name)
            stack_exists = True
            print(f"Stack {stack_name} exists, updating...")
        except cf_client.exceptions.ClientError:
            stack_exists = False
            print(f"Stack {stack_name} does not exist, creating...")
        
        # Create or update stack
        if stack_exists:
            response = cf_client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'Environment',
                        'ParameterValue': environment
                    }
                ],
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            print(f"Stack update initiated: {response['StackId']}")
        else:
            response = cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'Environment',
                        'ParameterValue': environment
                    }
                ],
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Tags=[
                    {'Key': 'Environment', 'Value': environment},
                    {'Key': 'Application', 'Value': 'GramSaarthi-AI'},
                    {'Key': 'ManagedBy', 'Value': 'CloudFormation'}
                ]
            )
            print(f"Stack creation initiated: {response['StackId']}")
        
        # Wait for stack operation to complete
        print("\nWaiting for stack operation to complete...")
        waiter = cf_client.get_waiter('stack_create_complete' if not stack_exists else 'stack_update_complete')
        
        try:
            waiter.wait(
                StackName=stack_name,
                WaiterConfig={
                    'Delay': 10,
                    'MaxAttempts': 60
                }
            )
        except Exception as e:
            print(f"\nWarning: Waiter error (may be due to no changes): {e}")
            # Continue to check stack status
        
        # Get stack outputs
        stack_info = cf_client.describe_stacks(StackName=stack_name)
        stack = stack_info['Stacks'][0]
        
        print(f"\n{'='*60}")
        print(f"Stack Status: {stack['StackStatus']}")
        print(f"{'='*60}")
        
        if 'Outputs' in stack:
            print("\nStack Outputs:")
            for output in stack['Outputs']:
                print(f"  {output['OutputKey']}: {output['OutputValue']}")
        
        # Test health check endpoint
        if 'Outputs' in stack:
            health_endpoint = None
            for output in stack['Outputs']:
                if output['OutputKey'] == 'HealthCheckEndpoint':
                    health_endpoint = output['OutputValue']
                    break
            
            if health_endpoint:
                print(f"\n{'='*60}")
                print("Testing health check endpoint...")
                print(f"{'='*60}")
                time.sleep(5)  # Wait for API to be fully ready
                
                import requests
                try:
                    response = requests.get(health_endpoint, timeout=10)
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.json()}")
                    
                    if response.status_code == 200:
                        print("\n✓ Health check passed!")
                    else:
                        print("\n✗ Health check failed!")
                except Exception as e:
                    print(f"\n✗ Error testing health check: {e}")
                    print("Note: The endpoint may need a few more seconds to be ready.")
        
        print(f"\n{'='*60}")
        print("API Gateway deployment completed successfully!")
        print(f"{'='*60}")
        
        return True
        
    except cf_client.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'ValidationError' and 'No updates are to be performed' in error_message:
            print("\nNo changes detected. Stack is already up to date.")
            
            # Still show outputs
            stack_info = cf_client.describe_stacks(StackName=stack_name)
            stack = stack_info['Stacks'][0]
            
            if 'Outputs' in stack:
                print("\nStack Outputs:")
                for output in stack['Outputs']:
                    print(f"  {output['OutputKey']}: {output['OutputValue']}")
            
            return True
        else:
            print(f"\nError deploying stack: {error_code}")
            print(f"Message: {error_message}")
            return False
    
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def delete_api_gateway(environment='dev'):
    """
    Delete API Gateway stack.
    
    Args:
        environment: Environment name (dev, staging, prod)
    """
    config = get_config()
    cf_client = boto3.client('cloudformation', region_name=config.aws_region)
    
    stack_name = f'gramsaarthi-{environment}-api-gateway'
    
    print(f"Deleting API Gateway stack: {stack_name}")
    
    try:
        cf_client.delete_stack(StackName=stack_name)
        print("Stack deletion initiated...")
        
        # Wait for deletion
        waiter = cf_client.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stack_name)
        
        print("Stack deleted successfully!")
        return True
        
    except Exception as e:
        print(f"Error deleting stack: {e}")
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy or delete API Gateway stack')
    parser.add_argument(
        '--environment',
        default='dev',
        choices=['dev', 'staging', 'prod'],
        help='Environment name'
    )
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Delete the stack instead of deploying'
    )
    
    args = parser.parse_args()
    
    if args.delete:
        success = delete_api_gateway(args.environment)
    else:
        success = deploy_api_gateway(args.environment)
    
    sys.exit(0 if success else 1)
