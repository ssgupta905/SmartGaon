#!/usr/bin/env python3
"""Demo script for mandi price cache functionality."""

import sys
sys.path.insert(0, ".")

from src.services.mandi_price_cache import mandi_price_cache


def demo_get_latest_price():
    """Demo: Get latest price for a commodity."""
    print("\n" + "="*60)
    print("Demo: Get Latest Price")
    print("="*60)
    
    commodity = "tomato"
    state = "Maharashtra"
    
    latest = mandi_price_cache.get_latest_price(
        commodity=commodity,
        state=state
    )
    
    if latest:
        print(f"\nLatest price for {commodity} in {state}:")
        print(f"  Market: {latest['market_name']}")
        print(f"  Date: {latest['date']}")
        print(f"  Price: ₹{latest['price_modal']} per {latest['unit']}")
        print(f"  Range: ₹{latest['price_min']} - ₹{latest['price_max']}")
        print(f"  Arrivals: {latest['arrivals']} {latest['unit']}")
    else:
        print(f"No price data found for {commodity} in {state}")


def demo_get_price_statistics():
    """Demo: Get price statistics."""
    print("\n" + "="*60)
    print("Demo: Price Statistics")
    print("="*60)
    
    commodity = "onion"
    days = 30
    
    stats = mandi_price_cache.get_price_statistics(
        commodity=commodity,
        days=days
    )
    
    print(f"\nPrice statistics for {commodity} (last {days} days):")
    print(f"  Mean: ₹{stats['mean']}")
    print(f"  Median: ₹{stats['median']}")
    print(f"  Min: ₹{stats['min']}")
    print(f"  Max: ₹{stats['max']}")
    print(f"  Std Dev: ₹{stats['std_dev']}")
    print(f"  Data points: {stats['count']}")


def demo_get_price_trend():
    """Demo: Analyze price trend."""
    print("\n" + "="*60)
    print("Demo: Price Trend Analysis")
    print("="*60)
    
    commodity = "potato"
    days = 30
    
    trend = mandi_price_cache.get_price_trend(
        commodity=commodity,
        days=days
    )
    
    print(f"\nPrice trend for {commodity}:")
    print(f"  Trend: {trend['trend']}")
    print(f"  Change: {trend['change_percent']}%")
    print(f"  Latest price: ₹{trend['latest_price']}")
    print(f"  Price {days} days ago: ₹{trend['oldest_price']}")
    print(f"  Analysis: {trend['analysis']}")


def demo_compare_markets():
    """Demo: Compare prices across markets."""
    print("\n" + "="*60)
    print("Demo: Market Comparison")
    print("="*60)
    
    commodity = "wheat"
    
    # Get available markets
    markets = mandi_price_cache.get_markets_for_commodity(commodity)
    print(f"\nMarkets trading {commodity}: {len(markets)}")
    
    # Compare prices
    comparison = mandi_price_cache.compare_markets(
        commodity=commodity,
        markets=markets[:3],  # Compare top 3 markets
        days=7
    )
    
    print(f"\nPrice comparison for {commodity} (last 7 days):")
    for i, market in enumerate(comparison, 1):
        print(f"\n{i}. {market['market_name']}, {market['state']}")
        print(f"   Latest: ₹{market['latest_price']}")
        print(f"   Average: ₹{market['average_price']}")
        print(f"   Data points: {market['data_points']}")


def demo_get_historical_prices():
    """Demo: Get historical price data."""
    print("\n" + "="*60)
    print("Demo: Historical Prices")
    print("="*60)
    
    commodity = "rice"
    days = 7
    
    prices = mandi_price_cache.get_prices_for_commodity(
        commodity=commodity,
        days=days
    )
    
    print(f"\nLast {days} days of {commodity} prices:")
    print(f"Total records: {len(prices)}")
    
    # Show first 5 records
    for price in prices[:5]:
        print(f"\n  {price['date']} - {price['market_name']}, {price['state']}")
        print(f"    Price: ₹{price['price_modal']} per {price['unit']}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("Mandi Price Cache Demo")
    print("="*60)
    print("\nThis demo shows how to use the mandi price cache service")
    print("to efficiently access and analyze market price data.")
    
    try:
        demo_get_latest_price()
        demo_get_price_statistics()
        demo_get_price_trend()
        demo_compare_markets()
        demo_get_historical_prices()
        
        print("\n" + "="*60)
        print("✓ All demos completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error running demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
