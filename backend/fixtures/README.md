# Mandi Price Fixtures

This directory contains fixture data for the GramSaarthi AI platform, specifically mandi (agricultural market) price data for demonstration and testing purposes.

## Overview

The mandi price fixtures provide 30 days of realistic historical price data for 5 key agricultural commodities across 5 major markets in India.

## Commodities

The fixtures include data for the following commodities:

1. **Tomato** - Base price: ₹25/kg, High volatility
2. **Onion** - Base price: ₹30/kg, Very high volatility
3. **Potato** - Base price: ₹20/kg, Low volatility
4. **Wheat** - Base price: ₹2000/quintal, Moderate volatility
5. **Rice** - Base price: ₹2500/quintal, Moderate volatility

## Markets

Data is available for the following markets:

1. **Pune Mandi** - Pune, Maharashtra (Base market)
2. **Vashi APMC** - Mumbai, Maharashtra (Metro premium +15%)
3. **Ludhiana Grain Market** - Ludhiana, Punjab (Production region -5%)
4. **Coimbatore Market** - Coimbatore, Tamil Nadu (Regional +5%)
5. **Bangalore APMC** - Bangalore, Karnataka (Metro premium +12%)

## Data Characteristics

### Price Generation

Prices are generated with realistic characteristics:

- **Trend**: Declining for first 15 days, then rising
- **Daily Variation**: Random fluctuations within volatility range
- **Weekly Cycle**: Market activity patterns
- **Seasonal Factor**: Commodity-specific seasonal multipliers
- **Market Premium**: Location-based price adjustments

### Data Structure

Each price record contains:

```python
{
    "PK": "COMMODITY#{commodity_name}",
    "SK": "PRICE#{state}#{market}#{date}",
    "commodity_name": str,
    "state": str,
    "district": str,
    "market_name": str,
    "date": str,  # YYYY-MM-DD
    "price_min": float,
    "price_max": float,
    "price_modal": float,  # Most common price
    "unit": str,  # "kg" or "quintal"
    "arrivals": int,  # Quantity arrived at market
    "source": "agmarknet",
    "fetched_timestamp": str,  # ISO 8601
    "ttl": int  # Unix timestamp for auto-deletion
}
```

## Usage

### Loading Fixtures into DynamoDB

Use the dedicated loader script:

```bash
python scripts/load_mandi_prices.py
```

Or use the general sample data loader:

```bash
python scripts/load_sample_data.py
```

### Accessing Data via Cache

Use the mandi price cache service for efficient data access:

```python
from src.services.mandi_price_cache import mandi_price_cache

# Get latest price
latest = mandi_price_cache.get_latest_price(
    commodity="tomato",
    state="Maharashtra"
)

# Get price statistics
stats = mandi_price_cache.get_price_statistics(
    commodity="onion",
    days=30
)

# Analyze price trend
trend = mandi_price_cache.get_price_trend(
    commodity="potato",
    days=30
)

# Compare markets
markets = mandi_price_cache.get_markets_for_commodity("wheat")
comparison = mandi_price_cache.compare_markets(
    commodity="wheat",
    markets=markets,
    days=7
)
```

### Demo Script

Run the demo to see all cache features:

```bash
python examples/mandi_price_cache_demo.py
```

## Total Records

- **Commodities**: 5
- **Markets**: 5
- **Days**: 30
- **Total Records**: 750 (5 × 5 × 30)

## Cache Features

The `MandiPriceCache` service provides:

1. **In-Memory Caching**: 1-hour TTL for frequently accessed data
2. **Flexible Filtering**: By commodity, state, market, date range
3. **Statistical Analysis**: Mean, median, min, max, standard deviation
4. **Trend Analysis**: Price direction, change percentage, insights
5. **Market Comparison**: Compare prices across multiple markets
6. **Efficient Queries**: Optimized DynamoDB access patterns

## Data Refresh

- **TTL**: Records auto-delete after 90 days
- **Cache TTL**: In-memory cache expires after 1 hour
- **Refresh Strategy**: Re-run loader script to update data

## Testing

The fixtures are designed for:

- **Unit Testing**: Predictable data for test assertions
- **Integration Testing**: Realistic data for end-to-end tests
- **Demo Scenarios**: Showcase platform capabilities
- **Property-Based Testing**: Diverse data for property validation

## Notes

- Prices are generated with a fixed seed (42) for reproducibility
- Data simulates realistic market behavior with trends and volatility
- Market premiums reflect typical urban/rural price differences
- Seasonal factors approximate real commodity price patterns
