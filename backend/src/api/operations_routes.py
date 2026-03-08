"""Operations API routes for GramSaarthi AI platform."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from src.agents.operations_agent import operations_agent, InventoryAlert, PlanDeviation, WeeklyReport


router = APIRouter(prefix="/api/v1/operations", tags=["operations"])


# Request/Response Models

class DailySalesData(BaseModel):
    """Daily sales data."""
    
    total: float = Field(..., description="Total sales amount")
    transactions: int = Field(..., description="Number of transactions")
    products_sold: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of products sold with quantity and revenue"
    )


class InventorySnapshotData(BaseModel):
    """Inventory snapshot data."""
    
    products: List[Dict[str, Any]] = Field(
        ...,
        description="List of products with quantity, value, and reorder level"
    )


class TrackOperationsRequest(BaseModel):
    """Request model for tracking operational data."""
    
    date: Optional[str] = Field(
        None,
        description="Date in YYYY-MM-DD format (defaults to today)"
    )
    daily_sales: DailySalesData = Field(..., description="Daily sales data")
    inventory_snapshot: InventorySnapshotData = Field(..., description="Inventory snapshot")
    cash_position: float = Field(..., description="Current cash position")
    notes: str = Field(default="", description="Optional notes")


class TrackOperationsResponse(BaseModel):
    """Response model for tracking operational data."""
    
    success: bool = Field(..., description="Whether tracking succeeded")
    enterprise_id: str = Field(..., description="Enterprise ID")
    date: str = Field(..., description="Date of operational data")
    message: str = Field(..., description="Success message")


class InventoryAlertResponse(BaseModel):
    """Response model for inventory alert."""
    
    product: str = Field(..., description="Product name")
    current_quantity: float = Field(..., description="Current quantity")
    reorder_level: float = Field(..., description="Reorder level")
    average_monthly_sales: float = Field(..., description="Average monthly sales")
    percentage_remaining: float = Field(..., description="Percentage remaining")
    message: str = Field(..., description="Alert message")


class PlanDeviationResponse(BaseModel):
    """Response model for plan deviation."""
    
    metric: str = Field(..., description="Metric name")
    planned_value: float = Field(..., description="Planned value")
    actual_value: float = Field(..., description="Actual value")
    deviation_percent: float = Field(..., description="Deviation percentage")
    period: str = Field(..., description="Period")
    message: str = Field(..., description="Deviation message")


class AlertsResponse(BaseModel):
    """Response model for alerts."""
    
    inventory_alerts: List[InventoryAlertResponse] = Field(
        ...,
        description="List of inventory alerts"
    )
    plan_deviations: List[PlanDeviationResponse] = Field(
        ...,
        description="List of plan deviations"
    )
    total_alerts: int = Field(..., description="Total number of alerts")


class WeeklyReportResponse(BaseModel):
    """Response model for weekly report."""
    
    enterprise_id: str = Field(..., description="Enterprise ID")
    week_start: str = Field(..., description="Week start date")
    week_end: str = Field(..., description="Week end date")
    total_sales: float = Field(..., description="Total sales for the week")
    total_transactions: int = Field(..., description="Total transactions")
    inventory_status: Dict[str, Any] = Field(..., description="Inventory status")
    cash_flow_summary: Dict[str, Any] = Field(..., description="Cash flow summary")
    alerts: List[str] = Field(..., description="List of alerts")
    recommendations: List[str] = Field(..., description="List of recommendations")


# API Endpoints

@router.post(
    "/track/{enterprise_id}",
    response_model=TrackOperationsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record operational data",
    description="Track daily operational metrics including sales, inventory, and cash flow"
)
async def track_operations(
    enterprise_id: str = Path(..., description="Enterprise ID"),
    data: TrackOperationsRequest = ...
) -> TrackOperationsResponse:
    """
    Record operational data for an enterprise.
    
    This endpoint stores daily operational metrics in DynamoDB for monitoring
    and analysis. The data is used to generate alerts and reports.
    
    Args:
        enterprise_id: Enterprise identifier
        data: Operational data including sales, inventory, and cash position
        
    Returns:
        TrackOperationsResponse with success status
        
    Raises:
        HTTPException: If tracking fails
    """
    try:
        # Prepare operational data
        operational_data = {
            "date": data.date or datetime.utcnow().strftime("%Y-%m-%d"),
            "daily_sales": {
                "total": data.daily_sales.total,
                "transactions": data.daily_sales.transactions,
                "products_sold": data.daily_sales.products_sold
            },
            "inventory_snapshot": {
                "products": data.inventory_snapshot.products
            },
            "cash_position": data.cash_position,
            "notes": data.notes
        }
        
        # Track operations
        operations_agent.track_operations(
            enterprise_id=enterprise_id,
            operational_data=operational_data
        )
        
        return TrackOperationsResponse(
            success=True,
            enterprise_id=enterprise_id,
            date=operational_data["date"],
            message=f"Operational data for {operational_data['date']} recorded successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track operational data: {str(e)}"
        )


@router.get(
    "/alerts/{enterprise_id}",
    response_model=AlertsResponse,
    summary="Get active alerts",
    description="Retrieve active inventory alerts and plan deviations for an enterprise"
)
async def get_alerts(
    enterprise_id: str = Path(..., description="Enterprise ID")
) -> AlertsResponse:
    """
    Get active alerts for an enterprise.
    
    This endpoint checks for:
    - Inventory alerts (products below 20% threshold)
    - Plan deviations (sales deviating by more than 15%)
    
    Args:
        enterprise_id: Enterprise identifier
        
    Returns:
        AlertsResponse with inventory alerts and plan deviations
        
    Raises:
        HTTPException: If alert retrieval fails
    """
    try:
        # Check inventory alerts
        inventory_alerts = operations_agent.check_inventory_alerts(enterprise_id)
        
        # Detect plan deviations
        plan_deviations = operations_agent.detect_plan_deviations(enterprise_id)
        
        # Convert to response models
        inventory_alert_responses = [
            InventoryAlertResponse(
                product=alert.product,
                current_quantity=alert.current_quantity,
                reorder_level=alert.reorder_level,
                average_monthly_sales=alert.average_monthly_sales,
                percentage_remaining=alert.percentage_remaining,
                message=alert.message
            )
            for alert in inventory_alerts
        ]
        
        plan_deviation_responses = [
            PlanDeviationResponse(
                metric=deviation.metric,
                planned_value=deviation.planned_value,
                actual_value=deviation.actual_value,
                deviation_percent=deviation.deviation_percent,
                period=deviation.period,
                message=deviation.message
            )
            for deviation in plan_deviations
        ]
        
        return AlertsResponse(
            inventory_alerts=inventory_alert_responses,
            plan_deviations=plan_deviation_responses,
            total_alerts=len(inventory_alert_responses) + len(plan_deviation_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alerts: {str(e)}"
        )


@router.get(
    "/report/{enterprise_id}",
    response_model=WeeklyReportResponse,
    summary="Get weekly report",
    description="Generate weekly operational summary report with metrics and recommendations"
)
async def get_weekly_report(
    enterprise_id: str = Path(..., description="Enterprise ID"),
    week_start_date: Optional[str] = Query(
        None,
        description="Week start date in YYYY-MM-DD format (defaults to current week)"
    )
) -> WeeklyReportResponse:
    """
    Get weekly operational report for an enterprise.
    
    This endpoint generates a comprehensive weekly report including:
    - Total sales and transactions
    - Inventory status
    - Cash flow summary
    - Active alerts
    - Actionable recommendations
    
    Args:
        enterprise_id: Enterprise identifier
        week_start_date: Optional week start date (defaults to current week)
        
    Returns:
        WeeklyReportResponse with weekly metrics and recommendations
        
    Raises:
        HTTPException: If report generation fails
    """
    try:
        # Generate weekly report
        report = operations_agent.generate_weekly_report(
            enterprise_id=enterprise_id,
            week_start_date=week_start_date
        )
        
        return WeeklyReportResponse(
            enterprise_id=report.enterprise_id,
            week_start=report.week_start,
            week_end=report.week_end,
            total_sales=report.total_sales,
            total_transactions=report.total_transactions,
            inventory_status=report.inventory_status,
            cash_flow_summary=report.cash_flow_summary,
            alerts=report.alerts,
            recommendations=report.recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weekly report: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if operations service is operational"
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "operations",
        "timestamp": datetime.utcnow().isoformat()
    }
