# S3 Bucket Setup Guide

This guide explains the S3 bucket structure and setup for the GramSaarthi AI platform.

## Bucket Structure

The S3 bucket follows a well-organized folder structure:

```
gramsaarthi-data/
├── audio/
│   ├── sessions/          # Voice session recordings
│   │   └── {session_id}/
│   │       ├── user_{turn_id}.wav
│   │       └── response_{turn_id}.wav
│   └── alerts/            # Alert audio files
│       └── {alert_id}.wav
├── documents/
│   ├── financial-summaries/  # Financial summary PDFs
│   │   └── {enterprise_id}/
│   │       └── summary_{date}.pdf
│   └── reports/           # Weekly operational reports
│       └── {enterprise_id}/
│           └── weekly_{date}.pdf
├── cache/
│   ├── mandi-prices/      # Cached mandi price data
│   │   └── {commodity}_{state}_{date}.json
│   └── schemes/           # Cached scheme snapshots
│       └── schemes_snapshot_{date}.json
└── demo/
    ├── sample-profiles.json    # Demo enterprise profiles
    └── sample-scenarios.json   # Demo conversation scenarios
```

## Setup Methods

### Method 1: Using Python Script (Recommended)

Run the setup script to create the bucket and configure it:

```bash
python scripts/setup_s3_bucket.py
```

This script will:
- Create the S3 bucket if it doesn't exist
- Enable server-side encryption (AES256)
- Configure CORS for web access
- Set up lifecycle rules for automatic cleanup
- Create the folder structure
- Upload demo data

### Method 2: Using CloudFormation

Deploy the CloudFormation template:

```bash
aws cloudformation create-stack \
  --stack-name gramsaarthi-s3 \
  --template-body file://infrastructure/s3-bucket.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev
```

## Bucket Configuration

### Encryption

All objects are encrypted at rest using AES256 server-side encryption. Unencrypted uploads are denied by bucket policy.

### CORS Configuration

CORS is configured to allow web access:
- Allowed origins: `*` (configure specific origins in production)
- Allowed methods: GET, PUT, POST, HEAD
- Allowed headers: `*`
- Max age: 3600 seconds
- Exposed headers: ETag

### Lifecycle Rules

Automatic cleanup policies:

| Folder | Retention Period | Reason |
|--------|-----------------|--------|
| `audio/` | 7 days | Voice recordings are temporary |
| `cache/` | 90 days | Cache data becomes stale |
| `documents/` | 365 days | Keep documents for one year |

### Access Control

- Public access is blocked
- Access is granted to Lambda functions via bucket policy
- Presigned URLs are used for temporary access (default: 24 hours)

## Using the S3 Service

### Basic Usage

```python
from src.storage import s3_service

# Upload a file
key = s3_service.upload_file(
    file_data=b"content",
    key="path/to/file.txt",
    content_type="text/plain"
)

# Download a file
content = s3_service.download_file(key)

# Generate presigned URL
url = s3_service.generate_presigned_url(key, expiration=3600)
```

### Convenience Methods

```python
# Upload session audio
key = s3_service.upload_session_audio(
    session_id="session-123",
    turn_id=1,
    audio_data=audio_bytes,
    audio_type="user"
)

# Upload financial summary
key = s3_service.upload_financial_summary(
    enterprise_id="enterprise-123",
    pdf_data=pdf_bytes
)

# Get presigned URL for financial summary
url = s3_service.get_financial_summary_url(
    enterprise_id="enterprise-123",
    expiration=86400  # 24 hours
)

# Cache mandi prices
key = s3_service.cache_mandi_prices(
    commodity="tomato",
    state="Maharashtra",
    data={"prices": [100, 110, 105]}
)

# Retrieve cached mandi prices
data = s3_service.get_cached_mandi_prices(
    commodity="tomato",
    state="Maharashtra"
)
```

## Environment Configuration

Configure the bucket name in `.env`:

```env
S3_BUCKET_NAME=gramsaarthi-data
AWS_REGION=ap-south-1
```

For different environments, use prefixed bucket names:
- Development: `gramsaarthi-data-dev`
- Staging: `gramsaarthi-data-staging`
- Production: `gramsaarthi-data-prod`

## Security Best Practices

1. **Encryption**: All data is encrypted at rest and in transit
2. **Access Control**: Use IAM roles for Lambda functions, not access keys
3. **Presigned URLs**: Use short expiration times (1-24 hours)
4. **Bucket Policies**: Deny unencrypted uploads
5. **Versioning**: Enabled to protect against accidental deletions
6. **Logging**: Enable S3 access logging in production

## Monitoring

Monitor bucket usage:

```bash
# Get bucket size
aws s3 ls s3://gramsaarthi-data --recursive --summarize

# Check lifecycle rules
aws s3api get-bucket-lifecycle-configuration --bucket gramsaarthi-data

# View bucket metrics in CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name BucketSizeBytes \
  --dimensions Name=BucketName,Value=gramsaarthi-data \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \
  --period 86400 \
  --statistics Average
```

## Troubleshooting

### Bucket Already Exists Error

If the bucket name is taken globally, modify the bucket name in `.env`:

```env
S3_BUCKET_NAME=gramsaarthi-data-yourorg
```

### Access Denied Errors

Ensure your AWS credentials have the necessary permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:PutBucketEncryption",
        "s3:PutBucketCors",
        "s3:PutLifecycleConfiguration"
      ],
      "Resource": [
        "arn:aws:s3:::gramsaarthi-data*",
        "arn:aws:s3:::gramsaarthi-data*/*"
      ]
    }
  ]
}
```

### CORS Issues

If web access fails, verify CORS configuration:

```bash
aws s3api get-bucket-cors --bucket gramsaarthi-data
```

## Cost Optimization

- **Lifecycle Rules**: Automatically delete old files to reduce storage costs
- **Intelligent Tiering**: Consider enabling for documents folder
- **Request Optimization**: Use batch operations when possible
- **Presigned URLs**: Reduce Lambda execution time by generating URLs

## Testing

Run the S3 service tests:

```bash
# Run all S3 tests
pytest tests/unit/storage/test_s3_service.py -v

# Run with coverage
pytest tests/unit/storage/test_s3_service.py --cov=src.storage.s3_service
```

## References

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [S3 Lifecycle Configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [S3 CORS Configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/cors.html)
- [S3 Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
