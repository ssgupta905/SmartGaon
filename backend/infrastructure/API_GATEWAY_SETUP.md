# API Gateway Setup Guide

This guide explains how to set up and use the API Gateway with Lambda integration for the GramSaarthi AI platform.

## Overview

The API Gateway provides a REST API interface for the GramSaarthi AI platform with the following features:

- **Lambda Proxy Integration**: Seamless integration with AWS Lambda functions
- **CORS Support**: Pre-configured CORS headers for web application access
- **Health Check Endpoint**: Built-in health monitoring endpoint
- **CloudWatch Logging**: Comprehensive logging and metrics
- **Environment-based Deployment**: Support for dev, staging, and prod environments

## Architecture

```
Client Request
    ↓
API Gateway (REST API)
    ↓
Lambda Proxy Integration
    ↓
Lambda Function (Python 3.9)
    ↓
DynamoDB / S3 / Other Services
```

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. Python 3.9+ installed
3. Required Python packages: `boto3`, `requests`
4. DynamoDB tables and S3 bucket already deployed

## Deployment

### Quick Start

Deploy the API Gateway stack using the deployment script:

```bash
# Deploy to dev environment (default)
python scripts/deploy_api_gateway.py

# Deploy to staging environment
python scripts/deploy_api_gateway.py --environment staging

# Deploy to production environment
python scripts/deploy_api_gateway.py --environment prod
```

### Manual Deployment

If you prefer to deploy manually using AWS CLI:

```bash
# Create the stack
aws cloudformation create-stack \
  --stack-name gramsaarthi-dev-api-gateway \
  --template-body file://infrastructure/api-gateway.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev \
  --capabilities CAPABILITY_NAMED_IAM

# Wait for stack creation
aws cloudformation wait stack-create-complete \
  --stack-name gramsaarthi-dev-api-gateway

# Get stack outputs
aws cloudformation describe-stacks \
  --stack-name gramsaarthi-dev-api-gateway \
  --query 'Stacks[0].Outputs'
```

## Stack Outputs

After deployment, the stack provides the following outputs:

- **ApiId**: The API Gateway REST API ID
- **ApiEndpoint**: The base URL for the API (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/dev`)
- **HealthCheckEndpoint**: The health check endpoint URL
- **LambdaExecutionRoleArn**: The IAM role ARN for Lambda functions
- **HealthCheckFunctionArn**: The health check Lambda function ARN

## Endpoints

### Health Check

**Endpoint**: `GET /health`

**Description**: Returns the health status of the platform and its dependencies.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "environment": "dev",
  "services": {
    "dynamodb": "healthy",
    "s3": "healthy"
  }
}
```

**Example**:
```bash
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/health
```

## CORS Configuration

The API Gateway is configured with CORS support for web applications:

- **Allowed Origins**: `*` (all origins)
- **Allowed Methods**: `GET, POST, PUT, DELETE, OPTIONS`
- **Allowed Headers**: `Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token`
- **Max Age**: 3600 seconds

## Lambda Integration

### Lambda Proxy Integration

The API uses Lambda Proxy Integration, which means:

1. The entire request is passed to the Lambda function
2. The Lambda function must return a response in the following format:

```python
{
    'statusCode': 200,
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    },
    'body': json.dumps({
        'message': 'Success'
    })
}
```

### Adding New Endpoints

To add new endpoints to the API Gateway:

1. **Create a Lambda function** in the CloudFormation template:

```yaml
MyNewFunction:
  Type: AWS::Lambda::Function
  Properties:
    FunctionName: !Sub 'gramsaarthi-${Environment}-my-function'
    Runtime: python3.9
    Handler: index.lambda_handler
    Role: !GetAtt LambdaExecutionRole.Arn
    Code:
      ZipFile: |
        import json
        
        def lambda_handler(event, context):
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Hello from Lambda'})
            }
```

2. **Add Lambda permission** for API Gateway:

```yaml
MyNewFunctionPermission:
  Type: AWS::Lambda::Permission
  Properties:
    FunctionName: !Ref MyNewFunction
    Action: lambda:InvokeFunction
    Principal: apigateway.amazonaws.com
    SourceArn: !Sub 'arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${GramSaarthiAPI}/*'
```

3. **Create API Gateway resource**:

```yaml
MyNewResource:
  Type: AWS::ApiGateway::Resource
  Properties:
    RestApiId: !Ref GramSaarthiAPI
    ParentId: !GetAtt GramSaarthiAPI.RootResourceId
    PathPart: my-endpoint
```

4. **Create API Gateway method**:

```yaml
MyNewMethod:
  Type: AWS::ApiGateway::Method
  Properties:
    RestApiId: !Ref GramSaarthiAPI
    ResourceId: !Ref MyNewResource
    HttpMethod: GET
    AuthorizationType: NONE
    Integration:
      Type: AWS_PROXY
      IntegrationHttpMethod: POST
      Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${MyNewFunction.Arn}/invocations'
```

5. **Update the deployment** to include the new method:

```yaml
ApiDeployment:
  Type: AWS::ApiGateway::Deployment
  DependsOn:
    - HealthCheckMethod
    - MyNewMethod  # Add this
  Properties:
    RestApiId: !Ref GramSaarthiAPI
```

## IAM Permissions

The Lambda execution role has the following permissions:

- **DynamoDB**: Full access to all DynamoDB operations
- **S3**: Read, write, and delete access to all S3 buckets
- **CloudWatch Logs**: Write logs to CloudWatch

To restrict permissions, modify the `LambdaExecutionRole` in the CloudFormation template.

## Monitoring and Logging

### CloudWatch Logs

API Gateway logs are stored in CloudWatch Logs:

- **Log Group**: `/aws/apigateway/gramsaarthi-{environment}`
- **Retention**: 7 days

View logs:
```bash
aws logs tail /aws/apigateway/gramsaarthi-dev --follow
```

### CloudWatch Metrics

The API Gateway publishes the following metrics to CloudWatch:

- **Count**: Number of API requests
- **Latency**: Time between request and response
- **IntegrationLatency**: Time for Lambda to process the request
- **4XXError**: Client-side errors
- **5XXError**: Server-side errors

View metrics in the AWS Console or using AWS CLI:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=gramsaarthi-api-dev \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-15T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

## Testing

### Test Health Check Endpoint

```bash
# Get the health check endpoint from stack outputs
HEALTH_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name gramsaarthi-dev-api-gateway \
  --query 'Stacks[0].Outputs[?OutputKey==`HealthCheckEndpoint`].OutputValue' \
  --output text)

# Test the endpoint
curl $HEALTH_ENDPOINT
```

### Test with Python

```python
import requests

# Replace with your API endpoint
api_endpoint = "https://your-api-id.execute-api.us-east-1.amazonaws.com/dev"

# Test health check
response = requests.get(f"{api_endpoint}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

## Troubleshooting

### Common Issues

1. **403 Forbidden Error**
   - Check that Lambda permissions are correctly configured
   - Verify the API Gateway has permission to invoke the Lambda function

2. **502 Bad Gateway Error**
   - Check Lambda function logs in CloudWatch
   - Verify Lambda function returns correct response format
   - Check Lambda execution role has required permissions

3. **CORS Errors**
   - Verify OPTIONS method is configured for the resource
   - Check CORS headers in Lambda response
   - Ensure `Access-Control-Allow-Origin` header is set

4. **Timeout Errors**
   - Increase Lambda function timeout (default: 10 seconds)
   - Check for slow DynamoDB or S3 operations
   - Optimize Lambda function code

### View Lambda Logs

```bash
# Get Lambda function name
FUNCTION_NAME="gramsaarthi-dev-health-check"

# View recent logs
aws logs tail /aws/lambda/$FUNCTION_NAME --follow
```

### Test Lambda Function Directly

```bash
# Invoke Lambda function directly
aws lambda invoke \
  --function-name gramsaarthi-dev-health-check \
  --payload '{}' \
  response.json

# View response
cat response.json
```

## Cleanup

To delete the API Gateway stack:

```bash
# Using the deployment script
python scripts/deploy_api_gateway.py --delete --environment dev

# Or using AWS CLI
aws cloudformation delete-stack --stack-name gramsaarthi-dev-api-gateway
```

## Next Steps

1. **Add Authentication**: Implement API key or Cognito authentication
2. **Add Rate Limiting**: Configure usage plans and API keys
3. **Add Custom Domain**: Set up a custom domain name for the API
4. **Add More Endpoints**: Implement voice, enterprise, market, scheme, financial, and operations endpoints
5. **Add Request Validation**: Configure request validators for input validation

## References

- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Lambda Proxy Integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html)
- [CloudFormation API Gateway Resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_ApiGateway.html)
