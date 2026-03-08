"""Financial API routes for GramSaarthi AI platform."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

from src.agents.financial_agent import financial_agent
from src.models.financial import (
    FinancialData,
    FinancialSummary,
    CreditworthinessScore,
    SalesData,
    ExpensesData,
    InventoryData,
    CashFlowData,
    ProductBreakdown,
    InventoryItem,
    ExpenseCategories
)
from src.aws_client import aws_client
from src.config import settings


router = APIRouter(prefix="/api/v1/financial", tags=["financial"])


# Request/Response Models

class SubmitFinancialDataRequest(BaseModel):
    """Request model for submitting financial data."""
    
    period: str = Field(..., description="Period in YYYY-MM format")
    sales: SalesData = Field(..., description="Sales data")
    expenses: ExpensesData = Field(..., description="Expenses data")
    inventory: InventoryData = Field(..., description="Inventory data")
    cash_flow: CashFlowData = Field(..., description="Cash flow data")


class SubmitFinancialDataResponse(BaseModel):
    """Response model for financial data submission."""
    
    success: bool = Field(..., description="Whether submission succeeded")
    enterprise_id: str = Field(..., description="Enterprise ID")
    period: str = Field(..., description="Period")
    message: str = Field(..., description="Success message")


class FinancialSummaryResponse(BaseModel):
    """Response model for financial summary."""
    
    summary: FinancialSummary = Field(..., description="Financial summary")
    pdf_url: Optional[str] = Field(None, description="PDF download URL")


class CreditworthinessResponse(BaseModel):
    """Response model for creditworthiness assessment."""
    
    enterprise_id: str = Field(..., description="Enterprise ID")
    creditworthiness: CreditworthinessScore = Field(..., description="Creditworthiness score")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")


# API Endpoints

@router.post(
    "/data/{enterprise_id}",
    response_model=SubmitFinancialDataResponse,
    summary="Submit financial data",
    description="Submit financial data for an enterprise including sales, expenses, inventory, and cash flow"
)
async def submit_financial_data(
    enterprise_id: str = Path(..., description="Enterprise ID"),
    data: SubmitFinancialDataRequest = ...
) -> SubmitFinancialDataResponse:
    """
    Submit financial data for an enterprise.
    
    This endpoint stores financial data in DynamoDB for later analysis and reporting.
    """
    try:
        # Create FinancialData object
        financial_data = FinancialData(
            enterprise_id=enterprise_id,
            period=data.period,
            sales=data.sales,
            expenses=data.expenses,
            inventory=data.inventory,
            cash_flow=data.cash_flow
        )
        
        # Calculate metrics
        from src.services.financial_calculator_service import financial_calculator_service
        
        profit_margin = financial_calculator_service.calculate_profit_margin(
            financial_data.sales.total_revenue,
            financial_data.expenses.total_expenses
        )
        
        net_profit = financial_data.sales.total_revenue - financial_data.expenses.total_expenses
        cash_flow_change = financial_data.cash_flow.closing_balance - financial_data.cash_flow.opening_balance
        
        # Store in DynamoDB
        dynamodb = aws_client.dynamodb
        
        item = {
            "PK": {"S": f"ENTERPRISE#{enterprise_id}"},
            "SK": {"S": f"FINANCIAL#{data.period}"},
            "enterprise_id": {"S": enterprise_id},
            "period": {"S": data.period},
            "recorded_date": {"S": datetime.utcnow().isoformat()},
            "sales": {
                "M": {
                    "total_revenue": {"N": str(financial_data.sales.total_revenue)},
                    "product_breakdown": {
                        "L": [
                            {
                                "M": {
                                    "product": {"S": pb.product},
                                    "quantity": {"N": str(pb.quantity)},
                                    "revenue": {"N": str(pb.revenue)}
                                }
                            }
                            for pb in financial_data.sales.product_breakdown
                        ]
                    }
                }
            },
            "expenses": {
                "M": {
                    "total_expenses": {"N": str(financial_data.expenses.total_expenses)},
                    "categories": {
                        "M": {
                            "raw_materials": {"N": str(financial_data.expenses.categories.raw_materials)},
                            "labor": {"N": str(financial_data.expenses.categories.labor)},
                            "transport": {"N": str(financial_data.expenses.categories.transport)},
                            "utilities": {"N": str(financial_data.expenses.categories.utilities)},
                            "other": {"N": str(financial_data.expenses.categories.other)}
                        }
                    }
                }
            },
            "inventory": {
                "M": {
                    "total_value": {"N": str(financial_data.inventory.total_value)},
                    "products": {
                        "L": [
                            {
                                "M": {
                                    "product": {"S": item.product},
                                    "quantity": {"N": str(item.quantity)},
                                    "value": {"N": str(item.value)}
                                }
                            }
                            for item in financial_data.inventory.products
                        ]
                    }
                }
            },
            "cash_flow": {
                "M": {
                    "opening_balance": {"N": str(financial_data.cash_flow.opening_balance)},
                    "closing_balance": {"N": str(financial_data.cash_flow.closing_balance)},
                    "receivables": {"N": str(financial_data.cash_flow.receivables)},
                    "payables": {"N": str(financial_data.cash_flow.payables)}
                }
            },
            "calculated_metrics": {
                "M": {
                    "profit_margin": {"N": str(profit_margin)},
                    "net_profit": {"N": str(net_profit)},
                    "cash_flow_change": {"N": str(cash_flow_change)}
                }
            }
        }
        
        dynamodb.put_item(
            TableName="FinancialData",
            Item=item
        )
        
        return SubmitFinancialDataResponse(
            success=True,
            enterprise_id=enterprise_id,
            period=data.period,
            message=f"Financial data for period {data.period} submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit financial data: {str(e)}"
        )


@router.get(
    "/summary/{enterprise_id}",
    response_model=FinancialSummaryResponse,
    summary="Get financial summary",
    description="Generate comprehensive financial summary for an enterprise"
)
async def get_financial_summary(
    enterprise_id: str = Path(..., description="Enterprise ID"),
    include_pdf: bool = Query(False, description="Generate PDF export")
) -> FinancialSummaryResponse:
    """
    Get financial summary for an enterprise.
    
    Generates a comprehensive financial summary including:
    - Revenue and expense metrics
    - Profit margins and cash flow
    - Creditworthiness assessment
    - Simple language explanations
    - Optional PDF export
    """
    try:
        # Get enterprise profile for name
        dynamodb = aws_client.dynamodb
        
        try:
            profile_response = dynamodb.get_item(
                TableName="EnterpriseProfiles",
                Key={
                    "PK": {"S": f"ENTERPRISE#{enterprise_id}"},
                    "SK": {"S": "PROFILE"}
                }
            )
            enterprise_name = profile_response.get("Item", {}).get("name", {}).get("S", enterprise_id)
        except Exception:
            enterprise_name = enterprise_id
        
        # Generate summary
        summary = financial_agent.generate_financial_summary(
            enterprise_id=enterprise_id,
            enterprise_name=enterprise_name
        )
        
        # Generate PDF if requested
        pdf_url = None
        if include_pdf:
            try:
                pdf_url = financial_agent.export_summary_pdf(summary)
                summary.pdf_url = pdf_url
            except Exception as e:
                # PDF generation is optional, don't fail the request
                print(f"PDF generation failed: {e}")
        
        return FinancialSummaryResponse(
            summary=summary,
            pdf_url=pdf_url
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate financial summary: {str(e)}"
        )


@router.get(
    "/creditworthiness/{enterprise_id}",
    response_model=CreditworthinessResponse,
    summary="Get creditworthiness assessment",
    description="Get creditworthiness score and indicators for an enterprise"
)
async def get_creditworthiness(
    enterprise_id: str = Path(..., description="Enterprise ID")
) -> CreditworthinessResponse:
    """
    Get creditworthiness assessment for an enterprise.
    
    Returns:
    - Overall creditworthiness score (0-100)
    - Detailed indicators (DTI ratio, revenue stability, etc.)
    - Recommendations for improvement
    """
    try:
        # Generate full summary to get creditworthiness
        summary = financial_agent.generate_financial_summary(enterprise_id)
        
        return CreditworthinessResponse(
            enterprise_id=enterprise_id,
            creditworthiness=summary.creditworthiness,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate creditworthiness: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if financial service is operational"
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "financial",
        "timestamp": datetime.utcnow().isoformat()
    }
