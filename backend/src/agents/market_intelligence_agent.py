"""Market Intelligence Agent for pricing optimization and market analysis."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from math import radians, cos, sin, asin, sqrt

from src.services.market_analysis_service import market_analysis_service
from src.services.mandi_price_cache import mandi_price_cache
from src.models.orchestration import UserContext

logger = logging.getLogger(__name__)


class PricingRecommendation:
    """Pricing recommendation with reasoning."""
    
    def __init__(
        self,
        commodity: str,
        suggested_price: float,
        reasoning: str,
        trend_analysis: Dict[str, Any],
        confidence: float = 0.85
    ):
        """Initialize pricing recommendation."""
        self.commodity = commodity
        self.suggested_price = suggested_price
        self.reasoning = reasoning
        self.trend_analysis = trend_analysis
        self.confidence = confidence


class MarketOption:
    """Market option with location and pricing."""
    
    def __init__(
        self,
        market_name: str,
        state: str,
        district: str,
        distance_km: float,
        latest_price: float,
        average_price: float
    ):
        """Initialize market option."""
        self.market_name = market_name
        self.state = state
        self.district = district
        self.distance_km = distance_km
        self.latest_price = latest_price
        self.average_price = average_price


class PriceAlert:
    """Price alert for significant changes."""
    
    def __init__(
        self,
        commodity: str,
        current_price: float,
        market_price: float,
        difference_percent: float,
        message: str
    ):
        """Initialize price alert."""
        self.commodity = commodity
        self.current_price = current_price
        self.market_price = market_price
        self.difference_percent = difference_percent
        self.message = message


class MarketIntelligenceAgent:
    """
    Bedrock Agent for market analysis and pricing optimization.
    
    This agent provides:
    - Pricing recommendations based on market data
    - Price trend analysis
    - Best market selection within radius
    - Price alerts for significant changes
    """
    
    def __init__(self):
        """Initialize the market intelligence agent."""
        self.market_analysis = market_analysis_service
        self.price_cache = mandi_price_cache
        # Import alert service here to avoid circular imports
        from src.services.alert_service import alert_service
        self.alert_service = alert_service
    
    def process(self, query: str, context: UserContext, intent: str) -> str:
        """
        Process market intelligence query.
        
        Args:
            query: User query text
            context: User context with enterprise profile and entities
            intent: Classified intent
            
        Returns:
            Response text in simple language
        """
        try:
            # Extract commodity from entities or query
            commodities = context.entities.get("commodities", [])
            
            if not commodities:
                return self._get_help_message()
            
            commodity = commodities[0]
            
            # Get enterprise location if available
            location = None
            if context.enterprise_profile:
                location = context.enterprise_profile.get("location", {})
            
            # Get current price from entities if provided
            current_price = context.entities.get("current_price")
            
            # Generate pricing recommendation
            recommendation = self.get_pricing_recommendation(
                commodity=commodity,
                location=location.get("state") if location else None,
                current_price=current_price
            )
            
            # Format response in simple language
            return self._format_recommendation_response(recommendation)
            
        except Exception as e:
            logger.error(f"Market intelligence agent error: {str(e)}", exc_info=True)
            return "मुझे बाजार की जानकारी प्राप्त करने में समस्या हो रही है। कृपया बाद में पुनः प्रयास करें।"
    
    def get_pricing_recommendation(
        self,
        commodity: str,
        location: Optional[str] = None,
        current_price: Optional[float] = None
    ) -> PricingRecommendation:
        """
        Analyze market data and provide pricing recommendation.
        
        Args:
            commodity: Commodity name (e.g., 'tomato', 'wheat')
            location: State or location for filtering
            current_price: Current selling price (optional)
            
        Returns:
            PricingRecommendation with suggested price, reasoning, trends
        """
        # Fetch recent price data
        prices = self.market_analysis.fetch_mandi_prices(
            commodity=commodity,
            state=location or "",
            days=30
        )
        
        if not prices:
            # No data available
            return PricingRecommendation(
                commodity=commodity,
                suggested_price=0.0,
                reasoning=f"{commodity} के लिए बाजार डेटा उपलब्ध नहीं है।",
                trend_analysis={},
                confidence=0.0
            )
        
        # Calculate statistics
        stats = self.market_analysis.calculate_price_statistics(prices)
        
        # Analyze trends
        trend_analysis = self.analyze_price_trends(commodity, days=30)
        
        # Determine suggested price
        # Strategy: Recommend slightly above median for better returns
        suggested_price = stats["median"] * 1.05  # 5% above median
        
        # Generate reasoning in simple language
        reasoning = self._generate_pricing_reasoning(
            commodity=commodity,
            stats=stats,
            trend_analysis=trend_analysis,
            current_price=current_price,
            suggested_price=suggested_price
        )
        
        return PricingRecommendation(
            commodity=commodity,
            suggested_price=round(suggested_price, 2),
            reasoning=reasoning,
            trend_analysis=trend_analysis,
            confidence=0.85
        )
    
    def analyze_price_trends(
        self,
        commodity: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze historical price trends.
        
        Args:
            commodity: Commodity name
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend direction, change percentage, and analysis
        """
        return self.price_cache.get_price_trend(
            commodity=commodity,
            days=days
        )
    
    def find_best_market(
        self,
        commodity: str,
        user_location: Dict[str, Any],
        radius_km: int = 50
    ) -> List[MarketOption]:
        """
        Find best markets within radius.
        
        Args:
            commodity: Commodity name
            user_location: User location with lat/lon coordinates
            radius_km: Maximum distance in kilometers (default: 50)
            
        Returns:
            List of MarketOption sorted by price (best first)
        """
        # Get all markets for commodity
        state = user_location.get("state")
        markets = self.price_cache.get_markets_for_commodity(
            commodity=commodity,
            state=state
        )
        
        if not markets:
            return []
        
        # Get user coordinates
        user_coords = user_location.get("coordinates", {})
        user_lat = user_coords.get("lat")
        user_lon = user_coords.get("lon")
        
        if not user_lat or not user_lon:
            # No coordinates available, return markets without distance filtering
            return self._get_market_options_without_distance(commodity, markets)
        
        # Calculate distances and filter by radius
        market_options = []
        
        for market in markets:
            # For MVP, use approximate coordinates based on district
            # In production, would use actual market coordinates
            market_coords = self._get_approximate_market_coordinates(
                market["state"],
                market["district"]
            )
            
            if not market_coords:
                continue
            
            # Calculate distance
            distance = self._calculate_distance(
                user_lat, user_lon,
                market_coords["lat"], market_coords["lon"]
            )
            
            # Filter by radius
            if distance <= radius_km:
                # Get price data for this market
                prices = self.price_cache.get_prices_for_commodity(
                    commodity=commodity,
                    days=7,
                    state=market["state"],
                    market=market["market_name"]
                )
                
                if prices:
                    latest_price = prices[0]["price_modal"]
                    avg_price = sum(p["price_modal"] for p in prices) / len(prices)
                    
                    market_options.append(MarketOption(
                        market_name=market["market_name"],
                        state=market["state"],
                        district=market["district"],
                        distance_km=round(distance, 1),
                        latest_price=round(latest_price, 2),
                        average_price=round(avg_price, 2)
                    ))
        
        # Sort by latest price (highest first for selling)
        market_options.sort(key=lambda x: x.latest_price, reverse=True)
        
        return market_options
    
    def check_price_alerts(
        self,
        enterprise_id: str,
        commodity: Optional[str] = None,
        current_price: Optional[float] = None
    ) -> List[PriceAlert]:
        """
        Check if any price alerts should be triggered.
        
        Args:
            enterprise_id: Enterprise identifier
            commodity: Commodity to check (optional)
            current_price: Current selling price (optional)
            
        Returns:
            List of PriceAlert objects
        """
        alerts = []
        
        if not commodity or not current_price:
            return alerts
        
        # Get latest market price
        latest = self.price_cache.get_latest_price(commodity=commodity)
        
        if not latest:
            return alerts
        
        market_price = latest["price_modal"]
        
        # Calculate difference percentage
        difference_percent = ((market_price - current_price) / current_price) * 100
        
        # Trigger alert if difference > 10%
        if difference_percent > 10:
            message = (
                f"{commodity} की बाजार कीमत आपकी वर्तमान कीमत से {difference_percent:.1f}% अधिक है। "
                f"बाजार कीमत: ₹{market_price:.2f}, आपकी कीमत: ₹{current_price:.2f}। "
                f"अधिक लाभ के लिए कीमत बढ़ाने पर विचार करें।"
            )
            
            alerts.append(PriceAlert(
                commodity=commodity,
                current_price=current_price,
                market_price=market_price,
                difference_percent=round(difference_percent, 2),
                message=message
            ))
        
        return alerts
    
    def check_7day_price_change_alerts(
        self,
        enterprise_id: str,
        commodities: Optional[List[str]] = None
    ) -> List[str]:
        """
        Check for significant price changes (> 15%) in the last 7 days.
        Creates alerts for affected enterprises.
        
        Args:
            enterprise_id: Enterprise identifier
            commodities: List of commodities to check (optional, checks all if None)
            
        Returns:
            List of alert IDs created
        """
        alert_ids = []
        
        try:
            # If no commodities specified, we can't check
            if not commodities:
                return alert_ids
            
            for commodity in commodities:
                # Get price data for last 7 days
                prices = self.market_analysis.fetch_mandi_prices(
                    commodity=commodity,
                    state="",  # All states
                    days=7
                )
                
                if len(prices) < 2:
                    # Not enough data to compare
                    continue
                
                # Get most recent and 7-day-old prices
                latest_price = prices[0]["price_modal"]
                oldest_price = prices[-1]["price_modal"]
                
                # Calculate percentage change
                if oldest_price > 0:
                    change_percent = ((latest_price - oldest_price) / oldest_price) * 100
                else:
                    continue
                
                # Trigger alert if change > 15%
                if abs(change_percent) > 15:
                    if change_percent > 0:
                        severity = "WARNING"
                        title = f"Price Increase Alert: {commodity}"
                        message = (
                            f"{commodity} की कीमत पिछले 7 दिनों में {abs(change_percent):.1f}% बढ़ी है। "
                            f"7 दिन पहले: ₹{oldest_price:.2f}, आज: ₹{latest_price:.2f}। "
                            f"यह बेचने का अच्छा समय हो सकता है।"
                        )
                    else:
                        severity = "INFO"
                        title = f"Price Decrease Alert: {commodity}"
                        message = (
                            f"{commodity} की कीमत पिछले 7 दिनों में {abs(change_percent):.1f}% गिरी है। "
                            f"7 दिन पहले: ₹{oldest_price:.2f}, आज: ₹{latest_price:.2f}। "
                            f"जल्दी बेचने पर विचार करें।"
                        )
                    
                    # Create alert using alert service
                    alert_id = self.alert_service.create_alert(
                        enterprise_id=enterprise_id,
                        alert_type="PRICE",
                        severity=severity,
                        title=title,
                        message=message,
                        delivery_method="VOICE_CALL",
                        action_required=True
                    )
                    
                    alert_ids.append(alert_id)
                    logger.info(
                        f"Created 7-day price change alert for {commodity}: "
                        f"{change_percent:.1f}% change"
                    )
            
            return alert_ids
            
        except Exception as e:
            logger.error(f"Error checking 7-day price change alerts: {str(e)}", exc_info=True)
            return alert_ids
    
    def _generate_pricing_reasoning(
        self,
        commodity: str,
        stats: Dict[str, float],
        trend_analysis: Dict[str, Any],
        current_price: Optional[float],
        suggested_price: float
    ) -> str:
        """Generate simple language reasoning for pricing recommendation."""
        reasoning_parts = []
        
        # Current market situation
        reasoning_parts.append(
            f"{commodity} की औसत बाजार कीमत ₹{stats['mean']:.2f} प्रति किलो है। "
            f"कीमतें ₹{stats['min']:.2f} से ₹{stats['max']:.2f} के बीच हैं।"
        )
        
        # Trend analysis
        trend = trend_analysis.get("trend", "stable")
        change_percent = trend_analysis.get("change_percent", 0)
        
        if trend == "rising":
            reasoning_parts.append(
                f"पिछले 30 दिनों में कीमतें {abs(change_percent):.1f}% बढ़ी हैं। "
                f"यह बेचने का अच्छा समय है।"
            )
        elif trend == "falling":
            reasoning_parts.append(
                f"पिछले 30 दिनों में कीमतें {abs(change_percent):.1f}% गिरी हैं। "
                f"जल्दी बेचना बेहतर होगा।"
            )
        else:
            reasoning_parts.append(
                f"पिछले 30 दिनों में कीमतें स्थिर रही हैं।"
            )
        
        # Recommendation
        reasoning_parts.append(
            f"मैं ₹{suggested_price:.2f} प्रति किलो की कीमत सुझाता हूं। "
            f"यह बाजार औसत से थोड़ा अधिक है और अच्छा लाभ देगा।"
        )
        
        # Comparison with current price if provided
        if current_price:
            if suggested_price > current_price:
                increase_percent = ((suggested_price - current_price) / current_price) * 100
                reasoning_parts.append(
                    f"आपकी वर्तमान कीमत (₹{current_price:.2f}) से {increase_percent:.1f}% अधिक है। "
                    f"कीमत बढ़ाने से अधिक लाभ होगा।"
                )
            elif suggested_price < current_price:
                reasoning_parts.append(
                    f"आपकी वर्तमान कीमत (₹{current_price:.2f}) बाजार से अधिक है। "
                    f"बिक्री बढ़ाने के लिए कीमत कम करने पर विचार करें।"
                )
        
        return " ".join(reasoning_parts)
    
    def _format_recommendation_response(
        self,
        recommendation: PricingRecommendation
    ) -> str:
        """Format recommendation as simple language response."""
        if recommendation.confidence == 0.0:
            return recommendation.reasoning
        
        response = f"{recommendation.commodity} के लिए बाजार विश्लेषण:\n\n"
        response += recommendation.reasoning
        
        return response
    
    def _get_help_message(self) -> str:
        """Get help message when no commodity specified."""
        return (
            "मैं आपको बाजार की कीमतों और सिफारिशों में मदद कर सकता हूं। "
            "कृपया बताएं कि आप किस फसल या उत्पाद के बारे में जानना चाहते हैं।"
        )
    
    def _get_market_options_without_distance(
        self,
        commodity: str,
        markets: List[Dict[str, str]]
    ) -> List[MarketOption]:
        """Get market options without distance filtering."""
        market_options = []
        
        for market in markets[:5]:  # Limit to top 5 markets
            prices = self.price_cache.get_prices_for_commodity(
                commodity=commodity,
                days=7,
                state=market["state"],
                market=market["market_name"]
            )
            
            if prices:
                latest_price = prices[0]["price_modal"]
                avg_price = sum(p["price_modal"] for p in prices) / len(prices)
                
                market_options.append(MarketOption(
                    market_name=market["market_name"],
                    state=market["state"],
                    district=market["district"],
                    distance_km=0.0,  # Unknown distance
                    latest_price=round(latest_price, 2),
                    average_price=round(avg_price, 2)
                ))
        
        # Sort by latest price (highest first)
        market_options.sort(key=lambda x: x.latest_price, reverse=True)
        
        return market_options
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Earth radius in kilometers
        r = 6371
        
        return c * r
    
    def _get_approximate_market_coordinates(
        self,
        state: str,
        district: str
    ) -> Optional[Dict[str, float]]:
        """
        Get approximate coordinates for a market based on district.
        
        For MVP, uses hardcoded approximate coordinates.
        In production, would use actual market location data.
        
        Args:
            state: State name
            district: District name
            
        Returns:
            Dictionary with lat/lon or None
        """
        # Approximate district coordinates for major markets
        # This is simplified for MVP - production would use actual data
        district_coords = {
            "Pune": {"lat": 18.5204, "lon": 73.8567},
            "Mumbai": {"lat": 19.0760, "lon": 72.8777},
            "Nashik": {"lat": 19.9975, "lon": 73.7898},
            "Nagpur": {"lat": 21.1458, "lon": 79.0882},
            "Delhi": {"lat": 28.7041, "lon": 77.1025},
            "Bangalore": {"lat": 12.9716, "lon": 77.5946},
            "Chennai": {"lat": 13.0827, "lon": 80.2707},
            "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
            "Kolkata": {"lat": 22.5726, "lon": 88.3639},
        }
        
        return district_coords.get(district)


# Global agent instance
market_intelligence_agent = MarketIntelligenceAgent()
