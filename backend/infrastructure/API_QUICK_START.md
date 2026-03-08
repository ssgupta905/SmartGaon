# API Gateway Quick Start

Quick reference for deploying and using the GramSaarthi AI API Gateway.

## Deploy

```bash
# Deploy to dev environment
python scripts/deploy_api_gateway.py

# Deploy to other environments
python scripts/deploy_api_gateway.py --environment staging
python scripts/deploy_api_gateway.py --environment prod
```

## Get API Endpoint

```bash
# Using AWS CLI
aws cloudformation describe-stacks \
  --stack-name gramsaarthi-dev-api-gateway \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text

# Using Python
python -c "
import boto3
cf = boto3.client('cloudformation')
stacks = cf.describe_stacks(StackName='gramsaarthi-dev-api-gateway')
outputs = stacks['Stacks'][0]['Outputs']
endpoint = [o['OutputValue'] for o in outputs if o['OutputKey'] == 'ApiEndpoint'][0]
print(endpoint)
"
```

## Test Health Check

```bash
# Get health endpoint
HEALTH_URL=$(aws cloudformation describe-stacks \
  --stack-name gramsaarthi-dev-api-gateway \
  --query 'Stacks[0].Outputs[?OutputKey==`HealthCheckEndpoint`].OutputValue' \
  --output text)

# Test it
curl $HEALTH_URL

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:00.000Z",
#   "environment": "dev",
#   "services": {
#     "dynamodb": "healthy",
#     "s3": "healthy"
#   }
# }
```

## Run Integration Tests

```bash
# Test API Gateway endpoints
pytest tests/integration/test_api_gateway.py -v

# Test specific test
pytest tests/integration/test_api_gateway.py::TestHealthCheckEndpoint::test_health_check_returns_200 -v
```

## View Logs

```bash
# API Gateway logs
aws logs tail /aws/apigateway/gramsaarthi-dev --follow

# Lambda function logs
aws logs tail /aws/lambda/gramsaarthi-dev-health-check --follow
```

## Update Stack

```bash
# Make changes to infrastructure/api-gateway.yaml
# Then redeploy
python scripts/deploy_api_gateway.py
```

## Delete Stack

```bash
python scripts/deploy_api_gateway.py --delete
```

## Common Issues

### 403 Forbidden
- Check Lambda permissions in CloudFormation template
- Verify API Gateway has permission to invoke Lambda

### 502 Bad Gateway
- Check Lambda function logs: `aws logs tail /aws/lambda/gramsaarthi-dev-health-check`
- Verify Lambda returns correct response format
- Check Lambda execution role permissions

### CORS Errors
- Verify OPTIONS method is configured
- Check CORS headers in Lambda response
- Ensure `Access-Control-Allow-Origin: *` is set

## Next Steps

1. Add more endpoints (voice, enterprise, market, etc.)
2. Implement authentication (API keys or Cognito)
3. Add request validation
4. Set up custom domain
5. Configure rate limiting

See [API_GATEWAY_SETUP.md](API_GATEWAY_SETUP.md) for detailed documentation.
