#!/usr/bin/env python3
"""Script to create DynamoDB tables for GramSaarthi AI."""

import sys
import time
from typing import List
import boto3
from botocore.exceptions import ClientError

# Add src to path
sys.path.insert(0, ".")

from src.config import settings
from src.db.table_schemas import ALL_TABLE_SCHEMAS, TableSchema


def create_table(dynamodb_client, schema: TableSchema, table_prefix: str) -> bool:
    """
    Create a DynamoDB table from schema definition.
    
    Args:
        dynamodb_client: Boto3 DynamoDB client
        schema: Table schema definition
        table_prefix: Prefix for table name
        
    Returns:
        True if table created successfully, False otherwise
    """
    full_table_name = f"{table_prefix}_{schema.table_name}"
    
    try:
        # Check if table already exists
        try:
            dynamodb_client.describe_table(TableName=full_table_name)
            print(f"✓ Table {full_table_name} already exists")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise
        
        # Prepare table creation parameters
        create_params = {
            "TableName": full_table_name,
            "KeySchema": schema.key_schema,
            "AttributeDefinitions": schema.attribute_definitions,
            "BillingMode": schema.billing_mode
        }
        
        # Add GSIs if defined
        if schema.global_secondary_indexes:
            create_params["GlobalSecondaryIndexes"] = schema.global_secondary_indexes
        
        # Create table
        print(f"Creating table {full_table_name}...")
        dynamodb_client.create_table(**create_params)
        
        # Wait for table to be active
        waiter = dynamodb_client.get_waiter('table_exists')
        waiter.wait(
            TableName=full_table_name,
            WaiterConfig={'Delay': 2, 'MaxAttempts': 30}
        )
        
        # Enable TTL if specified
        if schema.ttl_attribute:
            print(f"  Enabling TTL on attribute '{schema.ttl_attribute}'...")
            dynamodb_client.update_time_to_live(
                TableName=full_table_name,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': schema.ttl_attribute
                }
            )
        
        print(f"✓ Table {full_table_name} created successfully")
        return True
        
    except ClientError as e:
        print(f"✗ Error creating table {full_table_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error creating table {full_table_name}: {e}")
        return False


def delete_table(dynamodb_client, schema: TableSchema, table_prefix: str) -> bool:
    """
    Delete a DynamoDB table.
    
    Args:
        dynamodb_client: Boto3 DynamoDB client
        schema: Table schema definition
        table_prefix: Prefix for table name
        
    Returns:
        True if table deleted successfully, False otherwise
    """
    full_table_name = f"{table_prefix}_{schema.table_name}"
    
    try:
        print(f"Deleting table {full_table_name}...")
        dynamodb_client.delete_table(TableName=full_table_name)
        
        # Wait for table to be deleted
        waiter = dynamodb_client.get_waiter('table_not_exists')
        waiter.wait(
            TableName=full_table_name,
            WaiterConfig={'Delay': 2, 'MaxAttempts': 30}
        )
        
        print(f"✓ Table {full_table_name} deleted successfully")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"✓ Table {full_table_name} does not exist")
            return True
        print(f"✗ Error deleting table {full_table_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error deleting table {full_table_name}: {e}")
        return False


def list_tables(dynamodb_client, table_prefix: str):
    """
    List all tables with the given prefix.
    
    Args:
        dynamodb_client: Boto3 DynamoDB client
        table_prefix: Prefix for table names
    """
    try:
        response = dynamodb_client.list_tables()
        tables = [t for t in response.get('Tables', []) if t.startswith(table_prefix)]
        
        if tables:
            print(f"\nExisting tables with prefix '{table_prefix}':")
            for table in tables:
                print(f"  - {table}")
        else:
            print(f"\nNo tables found with prefix '{table_prefix}'")
            
    except Exception as e:
        print(f"✗ Error listing tables: {e}")


def main():
    """Main function to create all DynamoDB tables."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage DynamoDB tables for GramSaarthi AI")
    parser.add_argument(
        "action",
        choices=["create", "delete", "list", "recreate"],
        help="Action to perform"
    )
    parser.add_argument(
        "--table",
        help="Specific table name (without prefix) to operate on"
    )
    
    args = parser.parse_args()
    
    # Initialize DynamoDB client
    session_kwargs = {"region_name": settings.aws_region}
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        session_kwargs["aws_access_key_id"] = settings.aws_access_key_id
        session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    
    session = boto3.Session(**session_kwargs)
    dynamodb_client = session.client("dynamodb")
    
    table_prefix = settings.dynamodb_table_prefix
    
    print(f"\n{'='*60}")
    print(f"GramSaarthi AI - DynamoDB Table Management")
    print(f"{'='*60}")
    print(f"Region: {settings.aws_region}")
    print(f"Table Prefix: {table_prefix}")
    print(f"Action: {args.action}")
    print(f"{'='*60}\n")
    
    # Filter schemas if specific table requested
    schemas = ALL_TABLE_SCHEMAS
    if args.table:
        schemas = [s for s in ALL_TABLE_SCHEMAS if s.table_name == args.table]
        if not schemas:
            print(f"✗ Table '{args.table}' not found in schema definitions")
            sys.exit(1)
    
    # Perform action
    if args.action == "list":
        list_tables(dynamodb_client, table_prefix)
        
    elif args.action == "create":
        success_count = 0
        for schema in schemas:
            if create_table(dynamodb_client, schema, table_prefix):
                success_count += 1
            time.sleep(0.5)  # Brief pause between operations
        
        print(f"\n{'='*60}")
        print(f"Created {success_count}/{len(schemas)} tables successfully")
        print(f"{'='*60}\n")
        
    elif args.action == "delete":
        confirm = input(f"Are you sure you want to delete {len(schemas)} table(s)? (yes/no): ")
        if confirm.lower() != "yes":
            print("Operation cancelled")
            sys.exit(0)
        
        success_count = 0
        for schema in schemas:
            if delete_table(dynamodb_client, schema, table_prefix):
                success_count += 1
            time.sleep(0.5)
        
        print(f"\n{'='*60}")
        print(f"Deleted {success_count}/{len(schemas)} tables successfully")
        print(f"{'='*60}\n")
        
    elif args.action == "recreate":
        confirm = input(f"Are you sure you want to recreate {len(schemas)} table(s)? (yes/no): ")
        if confirm.lower() != "yes":
            print("Operation cancelled")
            sys.exit(0)
        
        # Delete tables
        print("\nDeleting tables...")
        for schema in schemas:
            delete_table(dynamodb_client, schema, table_prefix)
            time.sleep(0.5)
        
        # Wait a bit before recreating
        print("\nWaiting 5 seconds before recreating...")
        time.sleep(5)
        
        # Create tables
        print("\nCreating tables...")
        success_count = 0
        for schema in schemas:
            if create_table(dynamodb_client, schema, table_prefix):
                success_count += 1
            time.sleep(0.5)
        
        print(f"\n{'='*60}")
        print(f"Recreated {success_count}/{len(schemas)} tables successfully")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
