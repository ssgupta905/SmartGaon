"""
Integration tests for API Gateway endpoints.

These tests verify that the API Gateway is properly configured and
Lambda functions are responding correctly.
"""

import pytest
import requests
import boto3
import json
from datetime import datetime


@pytest.fixture
def api_endpoint():
    """Get API endpoint from CloudFormation stack outputs."""
    cf_client = boto3.client('cloudformation')
    
    try:
        response = cf_client.describe_stacks(
            StackName='gramsaarthi-dev-api-gateway'
        )
        
        outputs = response['Stacks'][0]['Outputs']
        for output in outputs:
            if output['OutputKey'] == 'ApiEndpoint':
                return output['OutputValue']
        
        pytest.skip("API Gateway stack not deployed")
    except Exception as e:
        pytest.skip(f"Could not get API endpoint: {e}")


@pytest.fixture
def health_endpoint():
    """Get health check endpoint from CloudFormation stack outputs."""
    cf_client = boto3.client('cloudformation')
    
    try:
        response = cf_client.describe_stacks(
            StackName='gramsaarthi-dev-api-gateway'
        )
        
        outputs = response['Stacks'][0]['Outputs']
        for output in outputs:
            if output['OutputKey'] == 'HealthCheckEndpoint':
                return output['OutputValue']
        
        pytest.skip("API Gateway stack not deployed")
    except Exception as e:
        pytest.skip(f"Could not get health endpoint: {e}")


class TestHealthCheckEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check_returns_200(self, health_endpoint):
        """Health check should return 200 OK."""
        response = requests.get(health_endpoint, timeout=10)
        assert response.status_code == 200
    
    def test_health_check_returns_json(self, health_endpoint):
        """Health check should return JSON response."""
        response = requests.get(health_endpoint, timeout=10)
        assert response.headers['Content-Type'] == 'application/json'
        
        # Should be valid JSON
        data = response.json()
        assert isinstance(data, dict)
    
    def test_health_check_has_required_fields(self, health_endpoint):
        """Health check response should have required fields."""
        response = requests.get(health_endpoint, timeout=10)
        data = response.json()
        
        # Required fields
        assert 'status' in data
        assert 'timestamp' in data
        assert 'environment' in data
        assert 'services' in data
        
        # Status should be healthy or unhealthy
        assert data['status'] in ['healthy', 'unhealthy']
        
        # Timestamp should be valid ISO 8601
        try:
            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Invalid timestamp format")
        
        # Environment should be dev
        assert data['environment'] == 'dev'
        
        # Services should include dynamodb and s3
        assert 'dynamodb' in data['services']
        assert 's3' in data['services']
    
    def test_health_check_cors_headers(self, health_endpoint):
        """Health check should include CORS headers."""
        response = requests.get(health_endpoint, timeout=10)
        
        # Should have CORS header
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*'
    
    def test_health_check_options_method(self, health_endpoint):
        """OPTIONS request should return CORS headers."""
        response = requests.options(health_endpoint, timeout=10)
        
        # Should return 200
        assert response.status_code == 200
        
        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers


class TestAPIGatewayConfiguration:
    """Tests for API Gateway configuration."""
    
    def test_api_gateway_exists(self):
        """API Gateway stack should exist."""
        cf_client = boto3.client('cloudformation')
        
        response = cf_client.describe_stacks(
            StackName='gramsaarthi-dev-api-gateway'
        )
        
        assert len(response['Stacks']) == 1
        stack = response['Stacks'][0]
        
        # Stack should be in a successful state
        assert stack['StackStatus'] in [
            'CREATE_COMPLETE',
            'UPDATE_COMPLETE'
        ]
    
    def test_lambda_function_exists(self):
        """Health check Lambda function should exist."""
        lambda_client = boto3.client('lambda')
        
        response = lambda_client.get_function(
            FunctionName='gramsaarthi-dev-health-check'
        )
        
        # Function should exist
        assert response['Configuration']['FunctionName'] == 'gramsaarthi-dev-health-check'
        assert response['Configuration']['Runtime'] == 'python3.9'
        assert response['Configuration']['Handler'] == 'index.lambda_handler'
    
    def test_lambda_execution_role_has_permissions(self):
        """Lambda execution role should have required permissions."""
        iam_client = boto3.client('iam')
        
        # Get role
        role_name = 'gramsaarthi-dev-lambda-execution-role'
        response = iam_client.get_role(RoleName=role_name)
        
        assert response['Role']['RoleName'] == role_name
        
        # Check attached policies
        policies = iam_client.list_attached_role_policies(RoleName=role_name)
        policy_names = [p['PolicyName'] for p in policies['AttachedPolicies']]
        
        # Should have basic execution policy
        assert 'AWSLambdaBasicExecutionRole' in policy_names
        
        # Check inline policies
        inline_policies = iam_client.list_role_policies(RoleName=role_name)
        inline_policy_names = inline_policies['PolicyNames']
        
        # Should have DynamoDB and S3 access
        assert 'DynamoDBAccess' in inline_policy_names
        assert 'S3Access' in inline_policy_names


class TestAPIGatewayPerformance:
    """Performance tests for API Gateway."""
    
    def test_health_check_response_time(self, health_endpoint):
        """Health check should respond within 2 seconds."""
        import time
        
        start = time.time()
        response = requests.get(health_endpoint, timeout=10)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Response took {elapsed:.2f}s, expected < 2s"
    
    def test_concurrent_requests(self, health_endpoint):
        """API should handle concurrent requests."""
        import concurrent.futures
        
        def make_request():
            response = requests.get(health_endpoint, timeout=10)
            return response.status_code
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
