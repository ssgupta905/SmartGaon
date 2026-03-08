#!/usr/bin/env python3
"""Script to load government scheme fixtures into DynamoDB for GramSaarthi AI demo."""

import sys
import json
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, ".")

from src.aws_client import aws_client
from src.config import settings
from fixtures.schemes import (
    SCHEME_FIXTURES,
    get_scheme_summary,
    SCHEME_CONFIGS
)


def load_schemes_to_dynamodb(batch_size: int = 25) -> int:
    """
    Load government scheme fixtures into DynamoDB table.
    
    Args:
        batch_size: Number of items per batch write (max 25 for DynamoDB)
        
    Returns:
        Number of items loaded
    """
    table = aws_client.get_table("Schemes")
    
    total_loaded = 0
    batch = []
    
    print(f"Loading {len(SCHEME_FIXTURES)} government scheme records...")
    
    for item in SCHEME_FIXTURES:
        batch.append(item)
        
        # Write batch when it reaches batch_size
        if len(batch) >= batch_size:
            _write_batch(table, batch)
            total_loaded += len(batch)
            print(f"  Loaded {total_loaded}/{len(SCHEME_FIXTURES)} records...", end="\r")
            batch = []
    
    # Write remaining items
    if batch:
        _write_batch(table, batch)
        total_loaded += len(batch)
    
    print(f"\n✓ Loaded {total_loaded} government scheme records")
    return total_loaded


def _write_batch(table, items: List[Dict[str, Any]]) -> None:
    """Write a batch of items to DynamoDB."""
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


def verify_data_loaded() -> bool:
    """
    Verify that scheme data was loaded correctly.
    
    Returns:
        True if verification passes
    """
    table = aws_client.get_table("Schemes")
    
    print("\nVerifying loaded data...")
    
    # Scan for all schemes (small dataset, scan is acceptable)
    response = table.scan(Limit=5)
    
    if response["Count"] > 0:
        print(f"✓ Found {response['Count']} scheme records")
        
        # Display sample record
        sample = response["Items"][0]
        print(f"\nSample scheme:")
        print(f"  Name: {sample['name']}")
        print(f"  Name (Hindi): {sample['name_local'].get('hi', 'N/A')}")
        print(f"  Type: {sample['scheme_type']}")
        print(f"  Authority: {sample['authority']}")
        print(f"  Eligible for: {', '.join(sample['eligibility_criteria']['enterprise_types'])}")
        print(f"  Benefit: {sample['benefits']['financial_benefit']}")
        print(f"  Max amount: ₹{sample['benefits']['benefit_amount']:,}")
        
        return True
    else:
        print(f"✗ No scheme records found")
        return False


def print_summary():
    """Print summary of fixtures to be loaded."""
    summary = get_scheme_summary()
    
    print(f"\n{'='*70}")
    print(f"Government Scheme Fixtures Summary")
    print(f"{'='*70}")
    print(f"Total schemes: {summary['total_schemes']}")
    print(f"\nScheme types:")
    for scheme_type, count in summary['scheme_types'].items():
        print(f"  - {scheme_type}: {count}")
    print(f"\nEligible enterprise types: {', '.join(summary['enterprise_types'])}")
    print(f"\nSchemes included:")
    for idx, scheme in enumerate(summary['schemes'], 1):
        print(f"  {idx}. {scheme['name']}")
        print(f"     Type: {scheme['type']} | Eligible: {', '.join(scheme['eligible_for'])}")
        print(f"     Max benefit: ₹{scheme['benefit_amount']:,}")
    print(f"{'='*70}\n")


def export_fixtures_to_json(output_file: str = "fixtures/schemes.json"):
    """
    Export fixtures to JSON file for backup/inspection.
    
    Args:
        output_file: Path to output JSON file
    """
    import json
    from decimal import Decimal
    
    # Convert Decimal to float for JSON serialization
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(SCHEME_FIXTURES, f, indent=2, default=decimal_default, ensure_ascii=False)
    
    print(f"✓ Exported fixtures to {output_file}")


def print_scheme_details():
    """Print detailed information about each scheme."""
    print(f"\n{'='*70}")
    print(f"Detailed Scheme Information")
    print(f"{'='*70}\n")
    
    for idx, scheme in enumerate(SCHEME_CONFIGS, 1):
        print(f"{idx}. {scheme['name']}")
        print(f"   Hindi: {scheme['name_local']['hi']}")
        print(f"   Type: {scheme['scheme_type']} | Authority: {scheme['authority']}")
        print(f"   Eligible: {', '.join(scheme['eligibility_criteria']['enterprise_types'])}")
        print(f"   Sectors: {', '.join(scheme['eligibility_criteria']['sectors'])}")
        print(f"   Benefit: {scheme['benefits']['financial_benefit']}")
        print(f"   Documents: {len(scheme['application_process']['required_documents'])} required")
        print(f"   Contact: {scheme['application_process']['contact_info']['phone']}")
        print(f"   URL: {scheme['application_process']['application_url']}")
        print()


def main():
    """Main function to load government scheme fixtures."""
    print(f"\n{'='*70}")
    print(f"GramSaarthi AI - Government Scheme Fixtures Loader")
    print(f"{'='*70}")
    print(f"Region: {settings.aws_region}")
    print(f"Table: Schemes")
    print(f"{'='*70}")
    
    try:
        # Print summary
        print_summary()
        
        # Ask if user wants detailed info
        print("Loading schemes into DynamoDB...")
        print()
        
        # Load data
        total_loaded = load_schemes_to_dynamodb()
        
        # Verify data
        if verify_data_loaded():
            print(f"\n{'='*70}")
            print("✓ Government scheme fixtures loaded and verified successfully!")
            print(f"{'='*70}\n")
        else:
            print(f"\n{'='*70}")
            print("⚠ Data loaded but verification failed")
            print(f"{'='*70}\n")
            sys.exit(1)
        
        # Optional: Export to JSON for inspection
        export_fixtures_to_json()
        
        # Print detailed scheme information
        print("\nFor detailed scheme information, the following schemes are available:")
        for idx, scheme in enumerate(SCHEME_CONFIGS, 1):
            print(f"  {idx}. {scheme['name']} ({scheme['scheme_type']})")
        
    except Exception as e:
        print(f"\n✗ Error loading government scheme fixtures: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
