"""Financial data models for GramSaarthi AI platform."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ProductBreakdown(BaseModel):
    """Product-level sales breakdown."""
    
    product: str = Field(..., description="Product name")
    quantity: float = Field(..., description="Quantity sold")
    revenue: float = Field(..., description="Revenue from product")


class SalesData(BaseModel):
    """Sales data structure."""
    
    total_revenue: float = Field(..., description="Total revenue")
    product_breakdown: List[ProductBreakdown] = Field(
        default_factory=list,
        description="Product-level breakdown"
    )


class ExpenseCategories(BaseModel):
    """Expense categories breakdown."""
    
    raw_materials: float = Field(default=0.0, description="Raw materials cost")
    labor: float = Field(default=0.0, description="Labor cost")
    transport: float = Field(default=0.0, description="Transport cost")
    utilities: float = Field(default=0.0, description="Utilities cost")
    other: float = Field(default=0.0, description="Other expenses")


class ExpensesData(BaseModel):
    """Expenses data structure."""
    
    total_expenses: float = Field(..., description="Total expenses")
    categories: ExpenseCategories = Field(
        default_factory=ExpenseCategories,
        description="Expense categories"
    )


class InventoryItem(BaseModel):
    """Inventory item."""
    
    product: str = Field(..., description="Product name")
    quantity: float = Field(..., description="Quantity in stock")
    value: float = Field(..., description="Total value")


class InventoryData(BaseModel):
    """Inventory data structure."""
    
    products: List[InventoryItem] = Field(
        default_factory=list,
        description="Inventory items"
    )
    total_value: float = Field(..., description="Total inventory value")


class CashFlowData(BaseModel):
    """Cash flow data structure."""
    
    opening_balance: float = Field(..., description="Opening cash balance")
    closing_balance: float = Field(..., description="Closing cash balance")
    receivables: float = Field(default=0.0, description="Outstanding receivables")
    payables: float = Field(default=0.0, description="Outstanding payables")


class CalculatedMetrics(BaseModel):
    """Calculated financial metrics."""
    
    profit_margin: float = Field(..., description="Profit margin percentage")
    net_profit: float = Field(..., description="Net profit amount")
    cash_flow_change: float = Field(..., description="Cash flow change")


class FinancialData(BaseModel):
    """Complete financial data for an enterprise."""
    
    enterprise_id: str = Field(..., description="Enterprise identifier")
    period: str = Field(..., description="Period in YYYY-MM format")
    recorded_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date when data was recorded"
    )
    sales: SalesData = Field(..., description="Sales data")
    expenses: ExpensesData = Field(..., description="Expenses data")
    inventory: InventoryData = Field(..., description="Inventory data")
    cash_flow: CashFlowData = Field(..., description="Cash flow data")
    calculated_metrics: Optional[CalculatedMetrics] = Field(
        None,
        description="Calculated metrics"
    )


class CreditworthinessIndicators(BaseModel):
    """Creditworthiness indicators."""
    
    debt_to_income_ratio: float = Field(..., description="Debt-to-income ratio percentage")
    revenue_stability_score: float = Field(..., description="Revenue stability score (0-1)")
    profit_margin: float = Field(..., description="Profit margin percentage")
    cash_flow_health: str = Field(..., description="Cash flow health status")
    overall_assessment: str = Field(..., description="Overall creditworthiness assessment")


class CreditworthinessScore(BaseModel):
    """Creditworthiness score and assessment."""
    
    score: float = Field(..., ge=0.0, le=100.0, description="Overall creditworthiness score (0-100)")
    indicators: CreditworthinessIndicators = Field(..., description="Detailed indicators")
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )


class FinancialSummary(BaseModel):
    """Comprehensive financial summary."""
    
    enterprise_id: str = Field(..., description="Enterprise identifier")
    enterprise_name: str = Field(..., description="Enterprise name")
    summary_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Summary generation date"
    )
    period_covered: str = Field(..., description="Period covered by summary")
    
    # Financial metrics
    total_revenue: float = Field(..., description="Total revenue")
    total_expenses: float = Field(..., description="Total expenses")
    net_profit: float = Field(..., description="Net profit")
    profit_margin: float = Field(..., description="Profit margin percentage")
    
    # Cash flow
    current_cash_balance: float = Field(..., description="Current cash balance")
    cash_flow_projection: Dict[str, Any] = Field(
        default_factory=dict,
        description="Cash flow projection data"
    )
    
    # Growth metrics
    revenue_growth: Optional[float] = Field(None, description="Revenue growth percentage")
    revenue_stability: Dict[str, Any] = Field(
        default_factory=dict,
        description="Revenue stability assessment"
    )
    
    # Creditworthiness
    creditworthiness: CreditworthinessScore = Field(..., description="Creditworthiness assessment")
    
    # Simple language explanations
    explanations: Dict[str, str] = Field(
        default_factory=dict,
        description="Simple language explanations of metrics"
    )
    
    # PDF export
    pdf_url: Optional[str] = Field(None, description="URL to PDF export")


class SalesRecord(BaseModel):
    """Sales record for historical analysis."""
    
    period: str = Field(..., description="Period (YYYY-MM)")
    revenue: float = Field(..., description="Revenue for period")
    date: datetime = Field(..., description="Record date")
