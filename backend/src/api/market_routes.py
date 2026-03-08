"""Market intelligence API routes."""

from typing import Dict, Any, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Request, Query
from pydantic import BaseModel, Field

from src.api.models import ErrorResponse
from src.agents.market_intelligence_agent import market_intelligence_agent
from src.services.enterprise_profile_service import (
    EnterpriseProfileService,
    ProfileNotFoundError,
)


router = APIRouter(prefix="/api/v1/market", tags=["market"])


# Request/Response Models
class MandiPriceData(BaseModel):
    """Mandi price data model."""
    
    commodity_name: str = Field(..., description="Commodity name")
    state: str = Field(..., description="State name")
    district: str = Field(..., description="District name")
    market_name: str = Field(..., description="Market name")
    date: str = Field(..., description="Price date (YYYY-MM-DD)")
    price_min: float = Field(..., description="Minimum price")
    price_max: float = Field(..., description="Maximum price")
    price_modal: float = Field(..., description="Modal/most common price")
    unit: str = Field(..., description="Unit (quintal/kg)")


class MandiPricesResponse(BaseModel):
    """Response model for mandi prices."""
    
    prices: List[MandiPriceData] = Field(..., description="List of price records")
    last_updated: str = Field(..., description="Last update timestamp")
    count: int = Field(..., description="Number of price records")


class TrendAnalysis(BaseModel):
    """Price trend analysis model."""
    
    trend: str = Field(..., description="Trend direction (rising/falling/stable)")
    change_percent: float = Field(..., description="Percentage change")
    period_days: int = Field(..., description="Analysis period in days")


class PricingRecommendationResponse(BaseModel):
    """Response model for pricing recommendation."""
    
    commodity: str = Field(..., description="Commodity name")
    suggested_price: float = Field(..., description="Suggested selling price")
    reasoning: str = Field(..., description="Recommendation reasoning in simple language")
    trend_analysis: TrendAnalysis = Field(..., description="Price trend analysis")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")


class MarketOptionData(BaseModel):
    """Market option data model."""
    
    market_name: str = Field(..., description="Market name")
    state: str = Field(..., description="State name")
    district: str = Field(..., description="District name")
    distance_km: float = Field(..., description="Distance in kilometers")
    latest_price: float = Field(..., description="Latest price")
    average_price: float = Field(..., description="Average price (7 days)")


class PriceTrendsResponse(BaseModel):
    """Response model for price trends."""
    
    commodity: str = Field(..., description="Commodity name")
    trends: TrendAnalysis = Field(..., description="Trend analysis")
    statistics: Dict[str, float] = Field(..., description="Price statistics")
    period_days: int = Field(..., description="Analysis period in days")


def create_error_response(
    error_type: str,
    message: str,
    details: Dict[str, Any] = None,
    request_id: str = None,
) -> ErrorResponse:
    """Create a standardized error response."""
    return ErrorResponse(
        error=error_type,
        message=message,
        details=details,
        request_id=request_id,
    )


@router.get(
    "/prices",
    response_model=MandiPricesResponse,
    summary="Get current mandi prices",
    description="Retrieve current mandi prices for specified commodity and location",
    responses={
        200: {"description": "Mandi prices retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_mandi_prices(
    request: Request,
    commodity: str = Query(..., description="Commodity name (e.g., tomato, wheat)"),
    state: Optional[str] = Query(None, description="State name for filtering"),
    market: Optional[str] = Query(None, description="Market name for filtering"),
    days: int = Query(7, ge=1, le=90, description="Number of days of data (1-90)"),
) -> MandiPricesResponse:
    """
    Get current mandi prices.
    
    Retrieves mandi price data for the specified commodity, optionally filtered
    by state and market. Returns data for the specified number of days.
    
    Args:
        request: FastAPI request object
        commodity: Commodity name
        state: Optional state filter
        market: Optional market filter
        days: Number of days of data (default: 7)
        
    Returns:
        Mandi prices with metadata
        
    Raises:
        HTTPException: If retrieval fails
    """
    request_id = str(uuid4())
    
    try:
        # Fetch prices from cache
        from src.services.mandi_price_cache import mandi_price_cache
        from datetime import datetime
        
        prices = mandi_price_cache.get_prices_for_commodity(
            commodity=commodity,
            days=days,
            state=state or "",
            market=market or ""
        )
        
        if not prices:
            # No data found
            return MandiPricesResponse(
                prices=[],
                last_updated=datetime.utcnow().isoformat(),
                count=0
            )
        
        # Convert to response model
        price_data = [
            MandiPriceData(
                commodity_name=p["commodity_name"],
                state=p["state"],
                district=p["district"],
                market_name=p["market_name"],
                date=p["date"],
                price_min=p["price_min"],
                price_max=p["price_max"],
                price_modal=p["price_modal"],
                unit=p["unit"]
            )
            for p in prices
        ]
        
        return MandiPricesResponse(
            prices=price_data,
            last_updated=datetime.utcnow().isoformat(),
            count=len(price_data)
        )
        
    except ValueError as e:
        # Validation error
        error = create_error_response(
            error_type="VALIDATION_ERROR",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.model_dump(),
        )
    except Exception as e:
        # Unexpected error
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="Failed to retrieve mandi prices",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


@router.get(
    "/recommendations/{enterprise_id}",
    response_model=PricingRecommendationResponse,
    summary="Get pricing recommendations",
    description="Get AI-powered pricing recommendations for an enterprise",
    responses={
        200: {"description": "Pricing recommendation generated successfully"},
        404: {"model": ErrorResponse, "description": "Enterprise not found"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_pricing_recommendations(
    request: Request,
    enterprise_id: str,
    commodity: Optional[str] = Query(None, description="Commodity name (uses enterprise products if not specified)"),
    current_price: Optional[float] = Query(None, description="Current selling price for comparison"),
) -> PricingRecommendationResponse:
    """
    Get pricing recommendations for an enterprise.
    
    Analyzes market data and provides AI-powered pricing recommendations
    based on the enterprise's products and location. If commodity is not
    specified, uses the first product from the enterprise profile.
    
    Args:
        request: FastAPI request object
        enterprise_id: Enterprise identifier
        commodity: Optional commodity name (uses enterprise products if not specified)
        current_price: Optional current selling price for comparison
        
    Returns:
        Pricing recommendation with reasoning and trend analysis
        
    Raises:
        HTTPException: If recommendation generation fails
    """
    request_id = str(uuid4())
    
    try:
        # Get enterprise profile
        profile_service = EnterpriseProfileService()
        profile = profile_service.get_profile(enterprise_id)
        
        # Determine commodity
        if not commodity:
            if not profile.products:
                error = create_error_response(
                    error_type="VALIDATION_ERROR",
                    message="No commodity specified and enterprise has no products",
                    request_id=request_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error.model_dump(),
                )
            commodity = profile.products[0]
        
        # Get location from profile
        location = profile.location.state if profile.location else None
        
        # Generate pricing recommendation
        recommendation = market_intelligence_agent.get_pricing_recommendation(
            commodity=commodity,
            location=location,
            current_price=current_price
        )
        
        # Convert to response model
        return PricingRecommendationResponse(
            commodity=recommendation.commodity,
            suggested_price=recommendation.suggested_price,
            reasoning=recommendation.reasoning,
            trend_analysis=TrendAnalysis(
                trend=recommendation.trend_analysis.get("trend", "stable"),
                change_percent=recommendation.trend_analysis.get("change_percent", 0.0),
                period_days=recommendation.trend_analysis.get("period_days", 30)
            ),
            confidence=recommendation.confidence
        )
        
    except ProfileNotFoundError as e:
        error = create_error_response(
            error_type="NOT_FOUND",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.model_dump(),
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Validation error
        error = create_error_response(
            error_type="VALIDATION_ERROR",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.model_dump(),
        )
    except Exception as e:
        # Unexpected error
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="Failed to generate pricing recommendation",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


@router.get(
    "/trends",
    response_model=PriceTrendsResponse,
    summary="Get price trends",
    description="Get price trend analysis for a commodity",
    responses={
        200: {"description": "Price trends retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_price_trends(
    request: Request,
    commodity: str = Query(..., description="Commodity name (e.g., tomato, wheat)"),
    days: int = Query(30, ge=7, le=90, description="Number of days to analyze (7-90)"),
) -> PriceTrendsResponse:
    """
    Get price trends for a commodity.
    
    Analyzes historical price data and provides trend analysis including
    direction (rising/falling/stable), percentage change, and statistics.
    
    Args:
        request: FastAPI request object
        commodity: Commodity name
        days: Number of days to analyze (default: 30)
        
    Returns:
        Price trend analysis with statistics
        
    Raises:
        HTTPException: If trend analysis fails
    """
    request_id = str(uuid4())
    
    try:
        # Get trend analysis
        trend_analysis = market_intelligence_agent.analyze_price_trends(
            commodity=commodity,
            days=days
        )
        
        # Get price statistics
        from src.services.market_analysis_service import market_analysis_service
        
        prices = market_analysis_service.fetch_mandi_prices(
            commodity=commodity,
            state="",
            days=days
        )
        
        if not prices:
            # No data available
            return PriceTrendsResponse(
                commodity=commodity,
                trends=TrendAnalysis(
                    trend="unknown",
                    change_percent=0.0,
                    period_days=days
                ),
                statistics={
                    "mean": 0.0,
                    "median": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "std_dev": 0.0
                },
                period_days=days
            )
        
        statistics = market_analysis_service.calculate_price_statistics(prices)
        
        return PriceTrendsResponse(
            commodity=commodity,
            trends=TrendAnalysis(
                trend=trend_analysis.get("trend", "stable"),
                change_percent=trend_analysis.get("change_percent", 0.0),
                period_days=days
            ),
            statistics=statistics,
            period_days=days
        )
        
    except ValueError as e:
        # Validation error
        error = create_error_response(
            error_type="VALIDATION_ERROR",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.model_dump(),
        )
    except Exception as e:
        # Unexpected error
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="Failed to analyze price trends",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )
