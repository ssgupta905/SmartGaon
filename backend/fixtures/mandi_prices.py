"""Mandi price fixtures for GramSaarthi AI demo and testing."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import random


# Commodity configurations with realistic price ranges and volatility
COMMODITY_CONFIGS = [
    {
        "name": "tomato",
        "base_price": 25.0,  # Rs per kg
        "volatility": 5.0,
        "seasonal_factor": 1.2,  # Higher prices in winter
        "unit": "kg"
    },
    {
        "name": "onion",
        "base_price": 30.0,  # Rs per kg
        "volatility": 8.0,
        "seasonal_factor": 1.3,  # High volatility commodity
        "unit": "kg"
    },
    {
        "name": "potato",
        "base_price": 20.0,  # Rs per kg
        "volatility": 3.0,
        "seasonal_factor": 1.1,  # Relatively stable
        "unit": "kg"
    },
    {
        "name": "wheat",
        "base_price": 2000.0,  # Rs per quintal
        "volatility": 50.0,
        "seasonal_factor": 1.05,  # Government procurement stabilizes
        "unit": "quintal"
    },
    {
        "name": "rice",
        "base_price": 2500.0,  # Rs per quintal
        "volatility": 100.0,
        "seasonal_factor": 1.08,  # MSP support
        "unit": "quintal"
    }
]

# Market locations across India
MARKET_LOCATIONS = [
    {
        "state": "Maharashtra",
        "district": "Pune",
        "market": "Pune Mandi",
        "price_multiplier": 1.0  # Base market
    },
    {
        "state": "Maharashtra",
        "district": "Mumbai",
        "market": "Vashi APMC",
        "price_multiplier": 1.15  # Metro premium
    },
    {
        "state": "Punjab",
        "district": "Ludhiana",
        "market": "Ludhiana Grain Market",
        "price_multiplier": 0.95  # Production region discount
    },
    {
        "state": "Tamil Nadu",
        "district": "Coimbatore",
        "market": "Coimbatore Market",
        "price_multiplier": 1.05  # Regional variation
    },
    {
        "state": "Karnataka",
        "district": "Bangalore",
        "market": "Bangalore APMC",
        "price_multiplier": 1.12  # Metro premium
    }
]


def generate_price_with_trend(
    base_price: float,
    volatility: float,
    days_ago: int,
    seasonal_factor: float = 1.0
) -> float:
    """
    Generate realistic price with trend and seasonality.
    
    Args:
        base_price: Base commodity price
        volatility: Price volatility range
        days_ago: Days in the past (0 = today)
        seasonal_factor: Seasonal price multiplier
        
    Returns:
        Generated price with trend
    """
    # Create a trend: prices declining for first 15 days, then rising
    if days_ago < 15:
        trend = -0.3 * days_ago  # Declining trend
    else:
        trend = 0.5 * (days_ago - 15)  # Rising trend
    
    # Add random daily variation
    daily_variation = random.uniform(-volatility, volatility)
    
    # Add weekly cycle (market activity patterns)
    weekly_cycle = volatility * 0.3 * random.choice([-1, 0, 1])
    
    # Calculate final price
    price = base_price + trend + daily_variation + weekly_cycle
    
    # Apply seasonal factor
    price *= seasonal_factor
    
    # Ensure price doesn't go negative or too low
    min_price = base_price * 0.5
    return max(price, min_price)


def generate_mandi_price_fixtures(days: int = 30) -> List[Dict[str, Any]]:
    """
    Generate mandi price fixtures for demo and testing.
    
    Args:
        days: Number of days of historical data to generate
        
    Returns:
        List of mandi price records
    """
    fixtures = []
    
    # Set seed for reproducible demo data
    random.seed(42)
    
    for commodity_config in COMMODITY_CONFIGS:
        for market in MARKET_LOCATIONS:
            for days_ago in range(days):
                date = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                
                # Generate modal price with trend
                modal_price = generate_price_with_trend(
                    base_price=commodity_config["base_price"],
                    volatility=commodity_config["volatility"],
                    days_ago=days_ago,
                    seasonal_factor=commodity_config["seasonal_factor"]
                )
                
                # Apply market-specific multiplier
                modal_price *= market["price_multiplier"]
                
                # Generate min/max prices (±10% of modal)
                price_min = modal_price * 0.9
                price_max = modal_price * 1.1
                
                # Generate realistic arrival quantities
                base_arrivals = 500 if commodity_config["unit"] == "kg" else 200
                arrivals = random.randint(
                    int(base_arrivals * 0.5),
                    int(base_arrivals * 1.5)
                )
                
                # Create DynamoDB item
                item = {
                    "PK": f"COMMODITY#{commodity_config['name']}",
                    "SK": f"PRICE#{market['state']}#{market['market']}#{date}",
                    "commodity_name": commodity_config["name"],
                    "state": market["state"],
                    "district": market["district"],
                    "market_name": market["market"],
                    "date": date,
                    "price_min": round(price_min, 2),
                    "price_max": round(price_max, 2),
                    "price_modal": round(modal_price, 2),
                    "unit": commodity_config["unit"],
                    "arrivals": arrivals,
                    "source": "agmarknet",
                    "fetched_timestamp": datetime.utcnow().isoformat() + "Z",
                    "ttl": int((datetime.utcnow() + timedelta(days=90)).timestamp())
                }
                
                fixtures.append(item)
    
    return fixtures


def get_commodity_summary() -> Dict[str, Any]:
    """
    Get summary of commodities in fixtures.
    
    Returns:
        Summary with commodity names, markets, and date range
    """
    return {
        "commodities": [c["name"] for c in COMMODITY_CONFIGS],
        "markets": [
            {
                "state": m["state"],
                "district": m["district"],
                "market": m["market"]
            }
            for m in MARKET_LOCATIONS
        ],
        "total_records": len(COMMODITY_CONFIGS) * len(MARKET_LOCATIONS) * 30,
        "date_range_days": 30
    }


# Pre-generate fixtures for quick access
MANDI_PRICE_FIXTURES = generate_mandi_price_fixtures(days=30)
