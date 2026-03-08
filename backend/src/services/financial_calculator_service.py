"""Financial calculator service for GramSaarthi AI platform."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CashFlowProjection:
    """Cash flow projection data."""
    
    months: int
    opening_balance: float
    projected_closing_balance: float
    monthly_projections: List[Dict[str, float]]
    has_shortfall: bool
    shortfall_month: Optional[int] = None


@dataclass
class StabilityScore:
    """Revenue stability assessment."""
    
    score: float  # 0.0 to 1.0
    coefficient_of_variation: float
    trend: str  # "increasing", "stable", "decreasing"
    assessment: str  # Human-readable assessment


class FinancialCalculatorService:
    """
    Core business logic for financial calculations.
    Implements financial metric calculations for creditworthiness assessment.
    """
    
    def calculate_profit_margin(self, revenue: float, expenses: float) -> float:
        """
        Calculate profit margin percentage.
        
        Args:
            revenue: Total revenue
            expenses: Total expenses
            
        Returns:
            Profit margin as percentage (0-100)
        """
        if revenue <= 0:
            return 0.0
        
        profit = revenue - expenses
        margin = (profit / revenue) * 100
        return round(margin, 2)
    
    def calculate_cash_flow(
        self,
        financial_data: Dict[str, Any],
        months: int = 3
    ) -> CashFlowProjection:
        """
        Project cash flow for coming months.
        
        Args:
            financial_data: Dictionary containing financial data with keys:
                - opening_balance: Current cash balance
                - monthly_revenue: Average monthly revenue
                - monthly_expenses: Average monthly expenses
                - receivables: Outstanding receivables
                - payables: Outstanding payables
            months: Number of months to project
            
        Returns:
            CashFlowProjection with monthly breakdown
        """
        opening_balance = financial_data.get("opening_balance", 0.0)
        monthly_revenue = financial_data.get("monthly_revenue", 0.0)
        monthly_expenses = financial_data.get("monthly_expenses", 0.0)
        receivables = financial_data.get("receivables", 0.0)
        payables = financial_data.get("payables", 0.0)
        
        # Calculate net monthly cash flow
        net_monthly_flow = monthly_revenue - monthly_expenses
        
        # Project month by month
        monthly_projections = []
        current_balance = opening_balance
        has_shortfall = False
        shortfall_month = None
        
        for month in range(1, months + 1):
            # Add receivables in first month
            if month == 1:
                current_balance += receivables
                current_balance -= payables
            
            # Add monthly net flow
            current_balance += net_monthly_flow
            
            monthly_projections.append({
                "month": month,
                "opening": round(current_balance - net_monthly_flow, 2),
                "inflow": round(monthly_revenue, 2),
                "outflow": round(monthly_expenses, 2),
                "closing": round(current_balance, 2)
            })
            
            # Check for shortfall
            if current_balance < 0 and not has_shortfall:
                has_shortfall = True
                shortfall_month = month
        
        return CashFlowProjection(
            months=months,
            opening_balance=round(opening_balance, 2),
            projected_closing_balance=round(current_balance, 2),
            monthly_projections=monthly_projections,
            has_shortfall=has_shortfall,
            shortfall_month=shortfall_month
        )
    
    def calculate_debt_to_income(self, financial_data: Dict[str, Any]) -> float:
        """
        Calculate debt-to-income ratio.
        
        Args:
            financial_data: Dictionary containing:
                - total_debt: Total outstanding debt
                - monthly_income: Average monthly income/revenue
                
        Returns:
            Debt-to-income ratio as percentage
        """
        total_debt = financial_data.get("total_debt", 0.0)
        monthly_income = financial_data.get("monthly_income", 0.0)
        
        if monthly_income <= 0:
            return 0.0
        
        # Calculate annual income
        annual_income = monthly_income * 12
        
        if annual_income <= 0:
            return 0.0
        
        ratio = (total_debt / annual_income) * 100
        return round(ratio, 2)
    
    def assess_revenue_stability(
        self,
        sales_history: List[Dict[str, Any]]
    ) -> StabilityScore:
        """
        Assess revenue stability over time.
        
        Args:
            sales_history: List of sales records with 'revenue' and 'period' keys
            
        Returns:
            StabilityScore with stability assessment
        """
        if not sales_history or len(sales_history) < 2:
            return StabilityScore(
                score=0.0,
                coefficient_of_variation=0.0,
                trend="unknown",
                assessment="Insufficient data for stability assessment"
            )
        
        # Extract revenue values
        revenues = [record.get("revenue", 0.0) for record in sales_history]
        
        # Calculate mean and standard deviation
        mean_revenue = sum(revenues) / len(revenues)
        
        if mean_revenue == 0:
            return StabilityScore(
                score=0.0,
                coefficient_of_variation=0.0,
                trend="stable",
                assessment="No revenue recorded"
            )
        
        variance = sum((r - mean_revenue) ** 2 for r in revenues) / len(revenues)
        std_dev = variance ** 0.5
        
        # Calculate coefficient of variation (CV)
        cv = (std_dev / mean_revenue) * 100
        
        # Calculate stability score (inverse of CV, normalized to 0-1)
        # Lower CV = higher stability
        # CV < 10% = excellent (score ~0.9-1.0)
        # CV 10-20% = good (score ~0.7-0.9)
        # CV 20-40% = moderate (score ~0.5-0.7)
        # CV > 40% = poor (score <0.5)
        if cv < 10:
            score = 1.0 - (cv / 100)
        elif cv < 20:
            score = 0.8 - ((cv - 10) / 100)
        elif cv < 40:
            score = 0.6 - ((cv - 20) / 100)
        else:
            score = max(0.0, 0.4 - ((cv - 40) / 200))
        
        # Determine trend
        if len(revenues) >= 3:
            # Simple trend analysis: compare first half vs second half
            mid = len(revenues) // 2
            first_half_avg = sum(revenues[:mid]) / mid
            second_half_avg = sum(revenues[mid:]) / (len(revenues) - mid)
            
            change_pct = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
            
            if change_pct > 10:
                trend = "increasing"
            elif change_pct < -10:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Generate assessment
        if score >= 0.8:
            assessment = "Excellent revenue stability with consistent performance"
        elif score >= 0.6:
            assessment = "Good revenue stability with minor fluctuations"
        elif score >= 0.4:
            assessment = "Moderate revenue stability with noticeable variations"
        else:
            assessment = "Poor revenue stability with significant fluctuations"
        
        return StabilityScore(
            score=round(score, 2),
            coefficient_of_variation=round(cv, 2),
            trend=trend,
            assessment=assessment
        )


# Global service instance
financial_calculator_service = FinancialCalculatorService()
