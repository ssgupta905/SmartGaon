# GramSaarthi AI - Infrastructure Setup

This directory contains infrastructure-as-code templates and scripts for provisioning DynamoDB tables for the GramSaarthi AI platform.

## Table Overview

The platform uses 9 DynamoDB tables with a single-table design pattern using composite keys (PK/SK):

| Table Name | Purpose | GSI | TTL |
|------------|---------|-----|-----|
| **EnterpriseProfiles** | Store enterprise registration and profile data | - | No |
| **VoiceSessions** | Track voice interaction sessions and conversation history | GSI2-SessionsByEnterprise | Yes (7 days) |
| **ActionPlans** | Store scheme application action plans and progress | - | No |
| **FinancialData** | Store monthly financial data for enterprises | - | No |
| **OperationalData** | Track daily operational metrics | - | No |
| **Schemes** | Government scheme database with eligibility criteria | GSI3-SchemesByType | No |
| **MandiPrices** | Agricultural commodity market prices | - | Yes (90 days) |
| **Alerts** | Proactive alerts and notifications | GSI1-AlertsByStatus | Yes (30 days) |
| **AnalyticsEvents** | Platform usage analytics and events | - | Yes (90 days) |

## Global Secondary Indexes

### GSI1: AlertsByStatus
- **Purpose**: Query all pending alerts for batch processing
- **Keys**: alert_status (HASH), created_date (RANGE)
- **Projection**: ALL

### GSI2: SessionsByEnterprise
- **Purpose**: Get all sessions for an enterprise
- **Keys**: enterprise_id (HASH), start_time (RANGE)
- **Projection**: ALL

### GSI3: SchemesByType
- **Purpose**: Browse schemes by category
- **Keys**: scheme_type (HASH), last_updated (RANGE)
- **Projection**: ALL

## Deployment Options

### Option 1: Python Script (Recommended for Development)

The Python script provides interactive table management with create, delete, list, and recreate operations.

```bash
# Create all tables
python scripts/create_tables.py create

# Create specific table
python scripts/create_tables.py create --table EnterpriseProfiles

# List existing tables
python scripts/create_tables.py list

# Delete all tables (requires confirmation)
python scripts/create_tables.py delete

# Recreate all tables (delete + create)
python scripts/create_tables.py recreate
```

**Features:**
- Interactive confirmation for destructive operations
- Automatic TTL configuration
- Wait for table creation/deletion
- Detailed progress output
- Error handling and retry logic

### Option 2: CloudFormation (Recommended for Production)

Use AWS CloudFormation for production deployments with proper stack management.

```bash
# Deploy stack
aws cloudformation create-stack \
  --stack-name gramsaarthi-dynamodb-dev \
  --template-body file://infrastructure/dynamodb-tables.yaml \
  --parameters \
    ParameterKey=TablePrefix,ParameterValue=gramsaarthi \
    ParameterKey=Environment,ParameterValue=dev

# Update stack
aws cloudformation update-stack \
  --stack-name gramsaarthi-dynamodb-dev \
  --template-body file://infrastructure/dynamodb-tables.yaml \
  --parameters \
    ParameterKey=TablePrefix,ParameterValue=gramsaarthi \
    ParameterKey=Environment,ParameterValue=dev

# Delete stack
aws cloudformation delete-stack \
  --stack-name gramsaarthi-dynamodb-dev

# Check stack status
aws cloudformation describe-stacks \
  --stack-name gramsaarthi-dynamodb-dev
```

**Features:**
- Declarative infrastructure definition
- Stack-based lifecycle management
- Automatic rollback on failure
- Export outputs for cross-stack references
- Resource tagging for cost tracking

## Loading Sample Data

After creating tables, load sample data for development and testing:

```bash
python scripts/load_sample_data.py
```

This loads:
- **3 enterprise profiles**: SHG (Maharashtra), FPO (Punjab), MSME (Tamil Nadu)
- **3 government schemes**: PM Mudra Yojana, NRLM, PM FME
- **450 mandi price records**: 30 days × 5 commodities × 3 markets
- **6 financial records**: 3 months × 2 enterprises

## Configuration

Tables are configured via environment variables in `.env`:

```bash
# AWS Configuration
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# DynamoDB Configuration
DYNAMODB_TABLE_PREFIX=gramsaarthi_dev
```

## Table Naming Convention

Tables follow the pattern: `{prefix}_{table_name}`

Examples:
- `gramsaarthi_dev_EnterpriseProfiles`
- `gramsaarthi_prod_VoiceSessions`

## Data Access Patterns

### Pattern 1: Get Enterprise Profile
```python
table.get_item(
    Key={
        'PK': 'ENTERPRISE#ent-001',
        'SK': 'PROFILE'
    }
)
```

### Pattern 2: Get Enterprise Action Plans
```python
table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': 'ENTERPRISE#ent-001',
        ':sk': 'PLAN#'
    }
)
```

### Pattern 3: Get Pending Alerts (using GSI1)
```python
table.query(
    IndexName='GSI1-AlertsByStatus',
    KeyConditionExpression='alert_status = :status',
    ExpressionAttributeValues={
        ':status': 'PENDING'
    }
)
```

### Pattern 4: Get Mandi Prices for Commodity
```python
table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': 'COMMODITY#tomato',
        ':sk': 'PRICE#Maharashtra#'
    }
)
```

## Billing and Cost Optimization

All tables use **PAY_PER_REQUEST** billing mode for:
- No capacity planning required
- Automatic scaling
- Pay only for actual usage
- Ideal for hackathon/MVP with unpredictable traffic

**Cost Estimates (Mumbai region):**
- Write: $1.4375 per million requests
- Read: $0.285 per million requests
- Storage: $0.285 per GB-month

For production with predictable traffic, consider switching to **PROVISIONED** mode with auto-scaling.

## TTL Configuration

Tables with TTL automatically delete expired items:

| Table | TTL Period | Purpose |
|-------|------------|---------|
| VoiceSessions | 7 days | Conversation history cleanup |
| MandiPrices | 90 days | Historical price data retention |
| Alerts | 30 days | Old alert cleanup |
| AnalyticsEvents | 90 days | Analytics data retention |

TTL is set as Unix timestamp in the `ttl` attribute.

## Monitoring

Monitor table health using CloudWatch metrics:
- **ConsumedReadCapacityUnits**: Read throughput
- **ConsumedWriteCapacityUnits**: Write throughput
- **UserErrors**: Client-side errors (validation, throttling)
- **SystemErrors**: Server-side errors
- **ThrottledRequests**: Rate limiting events

Set up alarms for:
- UserErrors > 10 per minute
- SystemErrors > 1 per minute
- ThrottledRequests > 0

## Backup and Recovery

### Point-in-Time Recovery (PITR)
Enable PITR for production tables:

```bash
aws dynamodb update-continuous-backups \
  --table-name gramsaarthi_prod_EnterpriseProfiles \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
```

### On-Demand Backups
Create manual backups before major changes:

```bash
aws dynamodb create-backup \
  --table-name gramsaarthi_prod_EnterpriseProfiles \
  --backup-name gramsaarthi-profiles-backup-$(date +%Y%m%d)
```

## Security Best Practices

1. **IAM Policies**: Use least-privilege IAM policies
2. **Encryption**: All tables use encryption at rest (AWS managed keys)
3. **VPC Endpoints**: Use VPC endpoints for Lambda access
4. **Access Logging**: Enable CloudTrail for audit logs
5. **Secrets Management**: Store credentials in AWS Secrets Manager

## Troubleshooting

### Table Creation Fails
- Check IAM permissions for `dynamodb:CreateTable`
- Verify region configuration
- Check for table name conflicts

### TTL Not Working
- TTL takes up to 48 hours to activate
- Verify `ttl` attribute is Unix timestamp (seconds)
- Check CloudWatch metrics for `TimeToLiveDeletedItemCount`

### GSI Queries Slow
- Verify GSI is in ACTIVE state
- Check if query uses both HASH and RANGE keys
- Consider adding filters after query, not during

### Throttling Errors
- Switch to provisioned mode with auto-scaling
- Implement exponential backoff in application
- Check for hot partitions (uneven key distribution)

## Next Steps

After setting up tables:
1. Run `python scripts/load_sample_data.py` to populate test data
2. Verify tables in AWS Console
3. Test data access patterns with sample queries
4. Proceed to implement application services (Task 2.1+)

## References

- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [Single-Table Design](https://aws.amazon.com/blogs/compute/creating-a-single-table-design-with-amazon-dynamodb/)
- [DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/)
