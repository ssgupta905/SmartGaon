# Quick Start - DynamoDB Setup

## Prerequisites

1. AWS credentials configured (via `.env` or AWS CLI)
2. Python dependencies installed: `pip install -r requirements.txt`
3. AWS region set in `.env`: `AWS_REGION=ap-south-1`

## 3-Step Setup

### Step 1: Create Tables (2-3 minutes)

```bash
python scripts/create_tables.py create
```

Expected output:
```
============================================================
GramSaarthi AI - DynamoDB Table Management
============================================================
Region: ap-south-1
Table Prefix: gramsaarthi_dev
Action: create
============================================================

Creating table gramsaarthi_dev_EnterpriseProfiles...
✓ Table gramsaarthi_dev_EnterpriseProfiles created successfully
Creating table gramsaarthi_dev_VoiceSessions...
  Enabling TTL on attribute 'ttl'...
✓ Table gramsaarthi_dev_VoiceSessions created successfully
...
============================================================
Created 9/9 tables successfully
============================================================
```

### Step 2: Load Sample Data (30 seconds)

```bash
python scripts/load_sample_data.py
```

Expected output:
```
============================================================
GramSaarthi AI - Sample Data Loader
============================================================
Region: ap-south-1
Table Prefix: gramsaarthi_dev
============================================================

Loading sample enterprises...
✓ Loaded enterprise: Mahila Shakti Self Help Group
✓ Loaded enterprise: Kisan Wheat Collective
✓ Loaded enterprise: Organic Food Processing Unit

Loading sample schemes...
✓ Loaded scheme: PM Mudra Yojana - Shishu
✓ Loaded scheme: National Rural Livelihood Mission
✓ Loaded scheme: PM Formalization of Micro Food Processing Enterprises

Loading sample mandi prices...
✓ Loaded 450 mandi price records

Loading sample financial data...
✓ Loaded financial data for 2 enterprises

============================================================
✓ All sample data loaded successfully!
============================================================
```

### Step 3: Verify Setup

```bash
python scripts/create_tables.py list
```

Expected output:
```
Existing tables with prefix 'gramsaarthi_dev':
  - gramsaarthi_dev_ActionPlans
  - gramsaarthi_dev_Alerts
  - gramsaarthi_dev_AnalyticsEvents
  - gramsaarthi_dev_EnterpriseProfiles
  - gramsaarthi_dev_FinancialData
  - gramsaarthi_dev_MandiPrices
  - gramsaarthi_dev_OperationalData
  - gramsaarthi_dev_Schemes
  - gramsaarthi_dev_VoiceSessions
```

## Verify Data

Test data access with Python:

```python
from src.aws_client import aws_client

# Get enterprise profile
table = aws_client.get_table("EnterpriseProfiles")
response = table.get_item(
    Key={'PK': 'ENTERPRISE#ent-001', 'SK': 'PROFILE'}
)
print(response['Item']['name'])
# Output: Mahila Shakti Self Help Group

# Get mandi prices
table = aws_client.get_table("MandiPrices")
response = table.query(
    KeyConditionExpression='PK = :pk',
    ExpressionAttributeValues={':pk': 'COMMODITY#tomato'},
    Limit=5
)
print(f"Found {len(response['Items'])} tomato price records")
# Output: Found 5 tomato price records
```

## Common Commands

```bash
# Create all tables
python scripts/create_tables.py create

# Create specific table
python scripts/create_tables.py create --table EnterpriseProfiles

# Delete all tables (with confirmation)
python scripts/create_tables.py delete

# Recreate all tables (delete + create)
python scripts/create_tables.py recreate

# List existing tables
python scripts/create_tables.py list

# Load sample data
python scripts/load_sample_data.py
```

## Troubleshooting

### Error: "Unable to locate credentials"
```bash
# Set credentials in .env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1
```

### Error: "Table already exists"
```bash
# Use recreate to delete and recreate
python scripts/create_tables.py recreate
```

### Error: "Access Denied"
Ensure IAM user has these permissions:
- `dynamodb:CreateTable`
- `dynamodb:DescribeTable`
- `dynamodb:DeleteTable`
- `dynamodb:UpdateTimeToLive`
- `dynamodb:PutItem`
- `dynamodb:GetItem`
- `dynamodb:Query`

## Next Steps

✅ Tables created and populated with sample data

Now you can:
1. Implement enterprise profile service (Task 2.1)
2. Build voice session management (Task 3.4)
3. Develop agent services (Tasks 6-10)

## Sample Data Summary

| Data Type | Count | Description |
|-----------|-------|-------------|
| Enterprises | 3 | SHG, FPO, MSME profiles |
| Schemes | 3 | Government loan/subsidy schemes |
| Mandi Prices | 450 | 30 days × 5 commodities × 3 markets |
| Financial Records | 6 | 3 months × 2 enterprises |

## Clean Up

To delete all tables and data:

```bash
python scripts/create_tables.py delete
```

⚠️ **Warning**: This permanently deletes all data. Use with caution!
