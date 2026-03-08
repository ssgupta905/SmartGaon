"""Mandi price cache service for efficient data access."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal

from src.aws_client import aws_client


class MandiPriceCache:
    """Service for caching and retrieving mandi price data."""
    
    def __init__(self):
        """Initialize the mandi price cache service."""
        self.table = aws_client.get_table("MandiPrices")
        self._memory_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._cache_ttl_seconds = 3600  # 1 hour in-memory cache
        self._cache_timestamps: Dict[str, datetime] = {}
    
    def get_prices_for_commodity(
        self,
        commodity: str,
        days: int = 30,
        state: Optional[str] = None,
        market: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get price data for a commodity.
        
        Args:
            commodity: Commodity name (e.g., 'tomato', 'wheat')
            days: Number of days of historical data
            state: Optional state filter
            market: Optional market filter
            
        Returns:
            List of price records sorted by date (newest first)
        """
        cache_key = f"{commodity}:{state}:{market}:{days}"
        
        # Check memory cache
        if self._is_cache_valid(cache_key):
            return self._memory_cache[cache_key]
        
        # Query DynamoDB
        response = self.table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={
                ":pk": f"COMMODITY#{commodity}"
            }
        )
        
        items = response.get("Items", [])
        
        # Apply filters
        if state:
            items = [item for item in items if item.get("state") == state]
        
        if market:
            items = [item for item in items if item.get("market_name") == market]
        
        # Filter by date range
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        items = [item for item in items if item.get("date", "") >= cutoff_date]
        
        # Sort by date (newest first)
        items.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Convert Decimal to float for easier handling
        items = self._convert_decimals(items)
        
        # Update cache
        self._memory_cache[cache_key] = items
        self._cache_timestamps[cache_key] = datetime.utcnow()
        
        return items
    
    def get_latest_price(
        self,
        commodity: str,
        state: Optional[str] = None,
        market: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent price for a commodity.
        
        Args:
            commodity: Commodity name
            state: Optional state filter
            market: Optional market filter
            
        Returns:
            Latest price record or None if not found
        """
        prices = self.get_prices_for_commodity(
            commodity=commodity,
            days=7,  # Look at last week
            state=state,
            market=market
        )
        
        return prices[0] if prices else None
    
    def get_price_statistics(
        self,
        commodity: str,
        days: int = 30,
        state: Optional[str] = None,
        market: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate price statistics for a commodity.
        
        Args:
            commodity: Commodity name
            days: Number of days to analyze
            state: Optional state filter
            market: Optional market filter
            
        Returns:
            Dictionary with mean, median, min, max, std_dev
        """
        prices = self.get_prices_for_commodity(
            commodity=commodity,
            days=days,
            state=state,
            market=market
        )
        
        if not prices:
            return {
                "mean": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "std_dev": 0.0,
                "count": 0
            }
        
        # Extract modal prices
        modal_prices = [p["price_modal"] for p in prices]
        
        # Calculate statistics
        mean_price = sum(modal_prices) / len(modal_prices)
        sorted_prices = sorted(modal_prices)
        median_price = sorted_prices[len(sorted_prices) // 2]
        min_price = min(modal_prices)
        max_price = max(modal_prices)
        
        # Calculate standard deviation
        variance = sum((p - mean_price) ** 2 for p in modal_prices) / len(modal_prices)
        std_dev = variance ** 0.5
        
        return {
            "mean": round(mean_price, 2),
            "median": round(median_price, 2),
            "min": round(min_price, 2),
            "max": round(max_price, 2),
            "std_dev": round(std_dev, 2),
            "count": len(modal_prices)
        }
    
    def get_price_trend(
        self,
        commodity: str,
        days: int = 30,
        state: Optional[str] = None,
        market: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze price trend for a commodity.
        
        Args:
            commodity: Commodity name
            days: Number of days to analyze
            state: Optional state filter
            market: Optional market filter
            
        Returns:
            Dictionary with trend direction, change percentage, and analysis
        """
        prices = self.get_prices_for_commodity(
            commodity=commodity,
            days=days,
            state=state,
            market=market
        )
        
        if len(prices) < 2:
            return {
                "trend": "insufficient_data",
                "change_percent": 0.0,
                "latest_price": 0.0,
                "oldest_price": 0.0,
                "analysis": "Not enough data for trend analysis"
            }
        
        # Get latest and oldest prices
        latest = prices[0]["price_modal"]
        oldest = prices[-1]["price_modal"]
        
        # Calculate change
        change_percent = ((latest - oldest) / oldest) * 100
        
        # Determine trend
        if change_percent > 5:
            trend = "rising"
            analysis = f"Prices are rising. Increased by {abs(change_percent):.1f}% over {days} days."
        elif change_percent < -5:
            trend = "falling"
            analysis = f"Prices are falling. Decreased by {abs(change_percent):.1f}% over {days} days."
        else:
            trend = "stable"
            analysis = f"Prices are stable. Changed by {abs(change_percent):.1f}% over {days} days."
        
        return {
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "latest_price": round(latest, 2),
            "oldest_price": round(oldest, 2),
            "analysis": analysis,
            "days_analyzed": days
        }
    
    def get_markets_for_commodity(
        self,
        commodity: str,
        state: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get list of markets that trade a commodity.
        
        Args:
            commodity: Commodity name
            state: Optional state filter
            
        Returns:
            List of unique markets with state and district
        """
        prices = self.get_prices_for_commodity(
            commodity=commodity,
            days=7,  # Recent data
            state=state
        )
        
        # Extract unique markets
        markets = {}
        for price in prices:
            market_key = f"{price['state']}:{price['market_name']}"
            if market_key not in markets:
                markets[market_key] = {
                    "state": price["state"],
                    "district": price["district"],
                    "market_name": price["market_name"]
                }
        
        return list(markets.values())
    
    def compare_markets(
        self,
        commodity: str,
        markets: List[Dict[str, str]],
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Compare prices across multiple markets.
        
        Args:
            commodity: Commodity name
            markets: List of markets to compare (with state and market_name)
            days: Number of days to analyze
            
        Returns:
            List of market comparisons with average prices
        """
        comparisons = []
        
        for market in markets:
            prices = self.get_prices_for_commodity(
                commodity=commodity,
                days=days,
                state=market.get("state"),
                market=market.get("market_name")
            )
            
            if prices:
                avg_price = sum(p["price_modal"] for p in prices) / len(prices)
                latest_price = prices[0]["price_modal"]
                
                comparisons.append({
                    "state": market["state"],
                    "market_name": market["market_name"],
                    "average_price": round(avg_price, 2),
                    "latest_price": round(latest_price, 2),
                    "data_points": len(prices)
                })
        
        # Sort by latest price (best price first)
        comparisons.sort(key=lambda x: x["latest_price"])
        
        return comparisons
    
    def clear_cache(self):
        """Clear the in-memory cache."""
        self._memory_cache.clear()
        self._cache_timestamps.clear()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self._memory_cache:
            return False
        
        timestamp = self._cache_timestamps.get(cache_key)
        if not timestamp:
            return False
        
        age_seconds = (datetime.utcnow() - timestamp).total_seconds()
        return age_seconds < self._cache_ttl_seconds
    
    def _convert_decimals(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Decimal values to float for easier handling."""
        converted = []
        for item in items:
            converted_item = {}
            for key, value in item.items():
                if isinstance(value, Decimal):
                    converted_item[key] = float(value)
                else:
                    converted_item[key] = value
            converted.append(converted_item)
        return converted


# Global cache instance
mandi_price_cache = MandiPriceCache()
