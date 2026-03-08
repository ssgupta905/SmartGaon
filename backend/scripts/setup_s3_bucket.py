#!/usr/bin/env python3
"""Script to set up S3 bucket and folder structure for GramSaarthi AI."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import boto3
from botocore.exceptions import ClientError
from src.config import settings
from src.storage.s3_service import S3Folder


def create_bucket(bucket_name: str, region: str) -> bool:
    """
    Create S3 bucket if it doesn't exist.
    
    Args:
        bucket_name: Name of the bucket to create
        region: AWS region
        
    Returns:
        True if bucket was created or already exists, False on error
    """
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✓ Bucket '{bucket_name}' already exists")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # Bucket doesn't exist, create it
            try:
                if region == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                print(f"✓ Created bucket '{bucket_name}'")
                return True
            except ClientError as create_error:
                print(f"✗ Error creating bucket: {create_error}")
                return False
        else:
            print(f"✗ Error checking bucket: {e}")
            return False


def enable_bucket_encryption(bucket_name: str) -> bool:
    """
    Enable default encryption on S3 bucket.
    
    Args:
        bucket_name: Name of the bucket
        
    Returns:
        True if encryption was enabled, False on error
    """
    s3_client = boto3.client('s3')
    
    try:
        s3_client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        },
                        'BucketKeyEnabled': True
                    }
                ]
            }
        )
        print(f"✓ Enabled encryption on bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"✗ Error enabling encryption: {e}")
        return False


def configure_cors(bucket_name: str) -> bool:
    """
    Configure CORS for web access.
    
    Args:
        bucket_name: Name of the bucket
        
    Returns:
        True if CORS was configured, False on error
    """
    s3_client = boto3.client('s3')
    
    cors_configuration = {
        'CORSRules': [
            {
                'AllowedOrigins': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST', 'HEAD'],
                'AllowedHeaders': ['*'],
                'MaxAgeSeconds': 3600,
                'ExposeHeaders': ['ETag']
            }
        ]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        print(f"✓ Configured CORS on bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"✗ Error configuring CORS: {e}")
        return False


def configure_lifecycle_rules(bucket_name: str) -> bool:
    """
    Configure lifecycle rules for automatic cleanup.
    
    Args:
        bucket_name: Name of the bucket
        
    Returns:
        True if lifecycle rules were configured, False on error
    """
    s3_client = boto3.client('s3')
    
    lifecycle_configuration = {
        'Rules': [
            {
                'Id': 'DeleteOldAudioFiles',
                'Status': 'Enabled',
                'Prefix': 'audio/',
                'Expiration': {'Days': 7}
            },
            {
                'Id': 'DeleteOldCacheFiles',
                'Status': 'Enabled',
                'Prefix': 'cache/',
                'Expiration': {'Days': 90}
            },
            {
                'Id': 'DeleteOldDocuments',
                'Status': 'Enabled',
                'Prefix': 'documents/',
                'Expiration': {'Days': 365}
            }
        ]
    }
    
    try:
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_configuration
        )
        print(f"✓ Configured lifecycle rules on bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"✗ Error configuring lifecycle rules: {e}")
        return False


def create_folder_structure(bucket_name: str) -> bool:
    """
    Create folder structure by uploading placeholder files.
    
    Args:
        bucket_name: Name of the bucket
        
    Returns:
        True if folders were created, False on error
    """
    s3_client = boto3.client('s3')
    
    # Define folder structure
    folders = [
        "audio/sessions/",
        "audio/alerts/",
        "documents/financial-summaries/",
        "documents/reports/",
        "cache/mandi-prices/",
        "cache/schemes/",
        "demo/"
    ]
    
    try:
        for folder in folders:
            # Create a .gitkeep file to maintain folder structure
            key = f"{folder}.gitkeep"
            s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=b'',
                ContentType='text/plain'
            )
        
        print(f"✓ Created folder structure in bucket '{bucket_name}'")
        print("  Folders created:")
        for folder in folders:
            print(f"    - {folder}")
        return True
    except ClientError as e:
        print(f"✗ Error creating folder structure: {e}")
        return False


def upload_demo_data(bucket_name: str) -> bool:
    """
    Upload demo data files.
    
    Args:
        bucket_name: Name of the bucket
        
    Returns:
        True if demo data was uploaded, False on error
    """
    s3_client = boto3.client('s3')
    
    # Sample demo profiles
    demo_profiles = [
        {
            "enterprise_id": "demo-shg-001",
            "type": "SHG",
            "name": "Mahila Shakti SHG",
            "products": ["tomato", "onion", "vegetables"],
            "location": {
                "state": "Maharashtra",
                "district": "Pune",
                "village": "Khed"
            }
        },
        {
            "enterprise_id": "demo-fpo-001",
            "type": "FPO",
            "name": "Kisan Collective FPO",
            "products": ["wheat", "rice", "pulses"],
            "location": {
                "state": "Punjab",
                "district": "Ludhiana",
                "village": "Samrala"
            }
        },
        {
            "enterprise_id": "demo-msme-001",
            "type": "MSME",
            "name": "Rural Food Processing Unit",
            "products": ["pickles", "spices", "packaged_food"],
            "location": {
                "state": "Tamil Nadu",
                "district": "Coimbatore",
                "village": "Pollachi"
            }
        }
    ]
    
    # Sample demo scenarios
    demo_scenarios = [
        {
            "scenario_id": "scenario-1",
            "title": "SHG Market Intelligence Query",
            "description": "SHG asking for tomato pricing and market recommendation",
            "enterprise_id": "demo-shg-001",
            "query": "मुझे टमाटर की कीमत बताओ",
            "expected_agent": "MarketIntelligenceAgent"
        },
        {
            "scenario_id": "scenario-2",
            "title": "FPO Scheme Discovery",
            "description": "FPO discovering loan schemes and generating action plan",
            "enterprise_id": "demo-fpo-001",
            "query": "मुझे लोन योजनाओं के बारे में बताएं",
            "expected_agent": "SchemeExecutionAgent"
        },
        {
            "scenario_id": "scenario-3",
            "title": "MSME Financial Summary",
            "description": "MSME requesting financial summary for credit application",
            "enterprise_id": "demo-msme-001",
            "query": "मुझे वित्तीय सारांश चाहिए",
            "expected_agent": "FinancialAgent"
        }
    ]
    
    try:
        # Upload demo profiles
        s3_client.put_object(
            Bucket=bucket_name,
            Key='demo/sample-profiles.json',
            Body=json.dumps(demo_profiles, indent=2).encode('utf-8'),
            ContentType='application/json'
        )
        
        # Upload demo scenarios
        s3_client.put_object(
            Bucket=bucket_name,
            Key='demo/sample-scenarios.json',
            Body=json.dumps(demo_scenarios, indent=2).encode('utf-8'),
            ContentType='application/json'
        )
        
        print(f"✓ Uploaded demo data to bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"✗ Error uploading demo data: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("GramSaarthi AI - S3 Bucket Setup")
    print("=" * 60)
    print()
    
    bucket_name = settings.s3_bucket_name
    region = settings.aws_region
    
    print(f"Bucket name: {bucket_name}")
    print(f"Region: {region}")
    print()
    
    # Step 1: Create bucket
    print("Step 1: Creating S3 bucket...")
    if not create_bucket(bucket_name, region):
        print("\n✗ Setup failed at bucket creation")
        return 1
    print()
    
    # Step 2: Enable encryption
    print("Step 2: Enabling bucket encryption...")
    if not enable_bucket_encryption(bucket_name):
        print("\n⚠ Warning: Could not enable encryption")
    print()
    
    # Step 3: Configure CORS
    print("Step 3: Configuring CORS...")
    if not configure_cors(bucket_name):
        print("\n⚠ Warning: Could not configure CORS")
    print()
    
    # Step 4: Configure lifecycle rules
    print("Step 4: Configuring lifecycle rules...")
    if not configure_lifecycle_rules(bucket_name):
        print("\n⚠ Warning: Could not configure lifecycle rules")
    print()
    
    # Step 5: Create folder structure
    print("Step 5: Creating folder structure...")
    if not create_folder_structure(bucket_name):
        print("\n⚠ Warning: Could not create folder structure")
    print()
    
    # Step 6: Upload demo data
    print("Step 6: Uploading demo data...")
    if not upload_demo_data(bucket_name):
        print("\n⚠ Warning: Could not upload demo data")
    print()
    
    print("=" * 60)
    print("✓ S3 bucket setup completed successfully!")
    print("=" * 60)
    print()
    print("Bucket structure:")
    print(f"  s3://{bucket_name}/")
    print("    ├── audio/")
    print("    │   ├── sessions/")
    print("    │   └── alerts/")
    print("    ├── documents/")
    print("    │   ├── financial-summaries/")
    print("    │   └── reports/")
    print("    ├── cache/")
    print("    │   ├── mandi-prices/")
    print("    │   └── schemes/")
    print("    └── demo/")
    print("        ├── sample-profiles.json")
    print("        └── sample-scenarios.json")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
