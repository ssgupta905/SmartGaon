#!/usr/bin/env python3
"""Script to load mandi price fixtures into DynamoDB for GramSaarthi AI demo."""

import sys
import json
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, ".")

from src.aws_client import aws_client
from src.config import settings
from fixtures.mandi_prices import (
    MANDI_PRICE_FIXTURES,
    get_commodity_summary,
    COMMODITY_CONFIGS,
    MARKET_LOCATIONS
)


def load_mandi_prices_to_dynamodb(batch_size: int = 25) -> int:
    """
    Load mandi price fixtures into DynamoDB table.
    
    Args:
        batch_size: Number of items per batch write (max 25 for DynamoDB)
        
    Returns:
        Number of items loaded
    """
    table = aws_client.get_table("MandiPrices")
    
    total_loaded = 0
    batch = []
    
    print(f"Loading {len(MANDI_PRICE_FIXTURES)} mandi price records...")
    
    for item in MANDI_PRICE_FIXTURES:
        batch.append(item)
        
        # Write batch when it reaches batch_size
        if len(batch) >= batch_size:
            _write_batch(table, batch)
            total_loaded += len(batch)
            print(f"  Loaded {total_loaded}/{len(MANDI_PRICE_FIXTURES)} records...", end="\r")
            batch = []
    
    # Write remaining items
    if batch:
        _write_batch(table, batch)
        total_loaded += len(batch)
    
    print(f"\n✓ Loaded {total_loaded} mandi price records")
    return total_loaded


def _write_batch(table, items: List[Dict[str, Any]]) -> None:
    """Write a batch of items to DynamoDB."""
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


def verify_data_loaded() -> bool:
    """
    Verify that mandi price data was loaded correctly.
    
    Returns:
        True if verification passes
    """
    table = aws_client.get_table("MandiPrices")
    
    print("\nVerifying loaded data...")
    
    # Check a sample commodity
    sample_commodity = COMMODITY_CONFIGS[0]["name"]
    response = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={
            ":pk": f"COMMODITY#{sample_commodity}"
        },
        Limit=5
    )
    
    if response["Count"] > 0:
        print(f"✓ Found {response['Count']} records for {sample_commodity}")
        
        # Display sample record
        sample = response["Items"][0]
        print(f"\nSample record:")
        print(f"  Commodity: {sample['commodity_name']}")
        print(f"  Market: {sample['market_name']}, {sample['state']}")
        print(f"  Date: {sample['date']}")
        print(f"  Price (modal): ₹{sample['price_modal']} per {sample['unit']}")
        print(f"  Price range: ₹{sample['price_min']} - ₹{sample['price_max']}")
        print(f"  Arrivals: {sample['arrivals']} {sample['unit']}")
        
        return True
    else:
        print(f"✗ No records found for {sample_commodity}")
        return False


def print_summary():
    """Print summary of fixtures to be loaded."""
    summary = get_commodity_summary()
    
    print(f"\n{'='*60}")
    print(f"Mandi Price Fixtures Summary")
    print(f"{'='*60}")
    print(f"Commodities: {', '.join(summary['commodities'])}")
    print(f"Markets: {len(summary['markets'])}")
    for market in summary["markets"]:
        print(f"  - {market['market']}, {market['district']}, {market['state']}")
    print(f"Date range: Last {summary['date_range_days']} days")
    print(f"Total records: {summary['total_records']}")
    print(f"{'='*60}\n")


def export_fixtures_to_json(output_file: str = "fixtures/mandi_prices.json"):
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
    
    with open(output_file, "w") as f:
        json.dump(MANDI_PRICE_FIXTURES, f, indent=2, default=decimal_default)
    
    print(f"✓ Exported fixtures to {output_file}")


def main():
    """Main function to load mandi price fixtures."""
    print(f"\n{'='*60}")
    print(f"GramSaarthi AI - Mandi Price Fixtures Loader")
    print(f"{'='*60}")
    print(f"Region: {settings.aws_region}")
    print(f"Table: MandiPrices")
    print(f"{'='*60}")
    
    try:
        # Print summary
        print_summary()
        
        # Load data
        total_loaded = load_mandi_prices_to_dynamodb()
        
        # Verify data
        if verify_data_loaded():
            print(f"\n{'='*60}")
            print("✓ Mandi price fixtures loaded and verified successfully!")
            print(f"{'='*60}\n")
        else:
            print(f"\n{'='*60}")
            print("⚠ Data loaded but verification failed")
            print(f"{'='*60}\n")
            sys.exit(1)
        
        # Optional: Export to JSON for inspection
        export_fixtures_to_json()
        
    except Exception as e:
        print(f"\n✗ Error loading mandi price fixtures: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
