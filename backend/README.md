# GramSaarthi AI

Voice-first rural growth orchestration platform for rural enterprises including Self-Help Groups (SHGs), Farmer Producer Organizations (FPOs), cooperatives, and MSMEs.

## Overview

GramSaarthi AI acts as an AI-powered virtual operations and growth manager, providing:
- Market intelligence and pricing optimization
- Government scheme discovery and execution guidance
- Financial readiness support for credit access
- Operational monitoring and replanning

All through natural Indic language voice interactions.

## Technology Stack

- **Backend**: Python 3.9+ with AWS Lambda
- **LLM Orchestration**: Amazon Bedrock Agents with Claude 3
- **Voice Processing**: AI4Bharat (IndicTrans2, IndicWav2Vec, IndicTTS)
- **API Layer**: AWS API Gateway
- **Data Storage**: DynamoDB, S3
- **Testing**: pytest, Hypothesis

## Project Structure

```
gramsaarthi-ai/
├── src/                    # Source code
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── aws_client.py      # AWS service clients
│   ├── db/                # Database schemas and services
│   └── storage/           # S3 storage services
├── infrastructure/         # CloudFormation templates
│   ├── dynamodb-tables.yaml
│   ├── s3-bucket.yaml
│   ├── api-gateway.yaml
│   └── *.md               # Setup guides
├── scripts/               # Deployment and utility scripts
│   ├── create_tables.py
│   ├── setup_s3_bucket.py
│   └── deploy_api_gateway.py
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── property/          # Property-based tests
│   └── integration/       # Integration tests
├── fixtures/              # Test fixtures and sample data
├── requirements.txt       # Python dependencies
├── .env.template         # Environment configuration template
└── pytest.ini            # Pytest configuration
```

## Setup

### Prerequisites

- Python 3.9 or higher
- AWS account with appropriate permissions
- AWS CLI configured (optional)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gramsaarthi-ai
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.template .env
# Edit .env with your AWS credentials and configuration
```

### AWS Infrastructure Setup

The platform requires the following AWS services:
- **DynamoDB**: For data storage
- **S3**: For file storage (audio, PDFs)
- **API Gateway**: For REST API endpoints
- **Lambda**: For serverless compute
- **Bedrock**: For LLM capabilities

#### 1. Configure AWS Credentials

Configure your AWS credentials either through:
1. Environment variables in `.env` file
2. AWS CLI configuration (`~/.aws/credentials`)
3. IAM role (when running on AWS)

#### 2. Deploy Infrastructure

Deploy the infrastructure components in order:

```bash
# 1. Create DynamoDB tables
python scripts/create_tables.py

# 2. Create S3 bucket
python scripts/setup_s3_bucket.py

# 3. Deploy API Gateway with Lambda
python scripts/deploy_api_gateway.py
```

For detailed setup instructions, see:
- [DynamoDB Setup](infrastructure/README.md)
- [S3 Setup](infrastructure/S3_SETUP.md)
- [API Gateway Setup](infrastructure/API_GATEWAY_SETUP.md)

#### 3. Verify Setup

Run the verification script to check all infrastructure is properly configured:

```bash
python verify_setup.py
```

Test the API Gateway health endpoint:

```bash
# Get the health endpoint URL from CloudFormation outputs
aws cloudformation describe-stacks \
  --stack-name gramsaarthi-dev-api-gateway \
  --query 'Stacks[0].Outputs[?OutputKey==`HealthCheckEndpoint`].OutputValue' \
  --output text

# Test the endpoint
curl <health-endpoint-url>
```

## Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run property-based tests only
pytest tests/property/

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py -v
```

## Development

### Demo Mode

For hackathon demonstration, the platform includes a demo mode that uses:
- Mock voice processing (pre-recorded audio)
- Cached market data
- Sample enterprise profiles and schemes

Enable demo mode in `.env`:
```
DEMO_MODE=true
USE_MOCK_VOICE=true
USE_CACHED_DATA=true
```

### Supported Languages

MVP supports three Indic languages:
- Hindi (hi)
- Tamil (ta)
- Telugu (te)

## Architecture

The platform uses a multi-agent architecture:
- **Orchestrator**: Routes queries and coordinates agents
- **Market Intelligence Agent**: Pricing and market analysis
- **Scheme Execution Agent**: Government scheme discovery
- **Financial Agent**: Financial summaries and credit readiness
- **Operations Agent**: Operational monitoring and alerts

## License

[License information to be added]

## Contributing

[Contributing guidelines to be added]

## Contact

[Contact information to be added]
