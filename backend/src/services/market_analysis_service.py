"""Market analysis service for pricing intelligence and anomaly detection."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from statistics import mean, median, stdev

from src.services.mandi_price_cache import mandi_price_cache


class MarketAnalysisService:
    """Core business logic for market intelligence."""
    
    def __init__(self):
        """Initialize the market analysis service."""
        self.cache = mandi_price_cache
    
    def fetch_mandi_prices(
        self,
        commodity: str,
        state: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Fetch prices from Agmarknet API or cache.
        
        Args:
            commodity: Commodity name (e.g., 'tomato', 'wheat')
            state: State name for filtering
            days: Number of days of historical data (default: 30)
            
        Returns:
            List of price records sorted by date (newest first)
        """
        return self.cache.get_prices_for_commodity(
            commodity=commodity,
            days=days,
            state=state
        )
    
    def calculate_price_statistics(
        self,
        prices: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate mean, median, std dev, trends.
        
        Args:
            prices: List of price records with 'price_modal' field
            
        Returns:
            Dictionary with statistical metrics:
            - mean: Average price
            - median: Median price
            - std_dev: Standard deviation
            - min: Minimum price
            - max: Maximum price
            - count: Number of data points
        """
        if not prices:
            return {
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
                "count": 0
            }
        
        # Extract modal prices
        modal_prices = [float(p["price_modal"]) for p in prices]
        
        # Calculate statistics
        mean_price = mean(modal_prices)
        median_price = median(modal_prices)
        min_price = min(modal_prices)
        max_price = max(modal_prices)
        
        # Calculate standard deviation (need at least 2 data points)
        if len(modal_prices) >= 2:
            std_dev_price = stdev(modal_prices)
        else:
            std_dev_price = 0.0
        
        return {
            "mean": round(mean_price, 2),
            "median": round(median_price, 2),
            "std_dev": round(std_dev_price, 2),
            "min": round(min_price, 2),
            "max": round(max_price, 2),
            "count": len(modal_prices)
        }
    
    def detect_price_anomalies(
        self,
        prices: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect unusual price movements.
        
        Anomaly detection logic:
        - Price changes > 15% in 7 days are flagged as anomalies
        
        Args:
            prices: List of price records sorted by date (newest first)
            
        Returns:
            List of detected anomalies with details:
            - date: Date of anomaly
            - price: Price at anomaly
            - change_percent: Percentage change
            - severity: 'moderate' (15-25%) or 'high' (>25%)
            - description: Human-readable description
        """
        if len(prices) < 2:
            return []
        
        anomalies = []
        
        # Check for 7-day price changes
        # Group prices by date for easier comparison
        prices_by_date = {}
        for price in prices:
            date = price.get("date")
            if date:
                prices_by_date[date] = float(price["price_modal"])
        
        # Sort dates
        sorted_dates = sorted(prices_by_date.keys(), reverse=True)
        
        # Check each date against 7 days prior
        for i, current_date in enumerate(sorted_dates):
            current_price = prices_by_date[current_date]
            
            # Find price from 7 days ago
            target_date = (
                datetime.strptime(current_date, "%Y-%m-%d") - timedelta(days=7)
            ).strftime("%Y-%m-%d")
            
            # Look for closest date within a 3-day window
            comparison_price = None
            for days_offset in range(0, 4):
                check_date = (
                    datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=days_offset)
                ).strftime("%Y-%m-%d")
                if check_date in prices_by_date:
                    comparison_price = prices_by_date[check_date]
                    break
                
                check_date = (
                    datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=days_offset)
                ).strftime("%Y-%m-%d")
                if check_date in prices_by_date:
                    comparison_price = prices_by_date[check_date]
                    break
            
            if comparison_price is None:
                continue
            
            # Calculate percentage change
            change_percent = ((current_price - comparison_price) / comparison_price) * 100
            
            # Flag if change > 15%
            if abs(change_percent) > 15:
                # Determine severity
                if abs(change_percent) > 25:
                    severity = "high"
                else:
                    severity = "moderate"
                
                # Create description
                direction = "increased" if change_percent > 0 else "decreased"
                description = (
                    f"Price {direction} by {abs(change_percent):.1f}% "
                    f"in 7 days (from ₹{comparison_price:.2f} to ₹{current_price:.2f})"
                )
                
                anomalies.append({
                    "date": current_date,
                    "price": round(current_price, 2),
                    "previous_price": round(comparison_price, 2),
                    "change_percent": round(change_percent, 2),
                    "severity": severity,
                    "description": description
                })
        
        return anomalies


# Global service instance
market_analysis_service = MarketAnalysisService()
