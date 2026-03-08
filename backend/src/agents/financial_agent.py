"""Financial agent for GramSaarthi AI platform."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from src.models.financial import (
    FinancialData,
    FinancialSummary,
    CreditworthinessScore,
    CreditworthinessIndicators,
    SalesData,
    ExpensesData,
    ExpenseCategories,
    InventoryData,
    CashFlowData,
    CalculatedMetrics,
    ProductBreakdown,
    InventoryItem,
    SalesRecord
)
from src.models.orchestration import UserContext
from src.services.financial_calculator_service import financial_calculator_service
from src.services.pdf_export_service import pdf_export_service
from src.aws_client import aws_client
from src.config import settings


class FinancialAgent:
    """
    Bedrock Agent for financial analysis and credit readiness.
    Handles financial data collection, summary generation, and creditworthiness assessment.
    """
    
    def __init__(self):
        """Initialize financial agent."""
        self.dynamodb = aws_client.dynamodb
        self.table_name = "FinancialData"
    
    def collect_financial_data(
        self,
        enterprise_id: str,
        conversation_turns: List[Dict[str, Any]]
    ) -> FinancialData:
        """
        Extract financial data from voice conversation.
        
        Args:
            enterprise_id: Enterprise identifier
            conversation_turns: List of conversation turns with user inputs
            
        Returns:
            FinancialData object with extracted information
        """
        # Extract financial information from conversation
        # In a real implementation, this would use NLP/LLM to extract structured data
        # For MVP, we'll use a simplified extraction approach
        
        extracted_data = {
            "revenue": 0.0,
            "expenses": 0.0,
            "inventory_value": 0.0,
            "cash_balance": 0.0,
            "receivables": 0.0,
            "payables": 0.0
        }
        
        # Simple keyword-based extraction (would be replaced with LLM in production)
        for turn in conversation_turns:
            text = turn.get("user_text", "").lower()
            
            # Extract revenue mentions
            if "revenue" in text or "sales" in text or "income" in text:
                # Extract numbers (simplified)
                import re
                numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', text)
                if numbers:
                    extracted_data["revenue"] = float(numbers[0].replace(',', ''))
            
            # Extract expense mentions
            if "expense" in text or "cost" in text or "spent" in text:
                import re
                numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', text)
                if numbers:
                    extracted_data["expenses"] = float(numbers[0].replace(',', ''))
        
        # Create FinancialData object
        period = datetime.now().strftime("%Y-%m")
        
        financial_data = FinancialData(
            enterprise_id=enterprise_id,
            period=period,
            sales=SalesData(
                total_revenue=extracted_data["revenue"],
                product_breakdown=[]
            ),
            expenses=ExpensesData(
                total_expenses=extracted_data["expenses"],
                categories=ExpenseCategories()
            ),
            inventory=InventoryData(
                products=[],
                total_value=extracted_data["inventory_value"]
            ),
            cash_flow=CashFlowData(
                opening_balance=extracted_data["cash_balance"],
                closing_balance=extracted_data["cash_balance"],
                receivables=extracted_data["receivables"],
                payables=extracted_data["payables"]
            )
        )
        
        return financial_data
    
    def generate_financial_summary(
        self,
        enterprise_id: str,
        enterprise_name: Optional[str] = None
    ) -> FinancialSummary:
        """
        Generate comprehensive financial summary.
        
        Args:
            enterprise_id: Enterprise identifier
            enterprise_name: Optional enterprise name
            
        Returns:
            FinancialSummary with metrics, ratios, trends, recommendations
        """
        # Fetch financial data from DynamoDB
        financial_records = self._fetch_financial_data(enterprise_id)
        
        if not financial_records:
            # Return empty summary if no data
            return self._create_empty_summary(enterprise_id, enterprise_name or enterprise_id)
        
        # Get most recent financial data
        latest_record = financial_records[0]
        
        # Calculate metrics
        total_revenue = latest_record["sales"]["total_revenue"]
        total_expenses = latest_record["expenses"]["total_expenses"]
        net_profit = total_revenue - total_expenses
        
        profit_margin = financial_calculator_service.calculate_profit_margin(
            total_revenue,
            total_expenses
        )
        
        # Cash flow projection
        cash_flow_data = {
            "opening_balance": latest_record["cash_flow"]["opening_balance"],
            "monthly_revenue": total_revenue,
            "monthly_expenses": total_expenses,
            "receivables": latest_record["cash_flow"].get("receivables", 0.0),
            "payables": latest_record["cash_flow"].get("payables", 0.0)
        }
        
        cash_flow_projection = financial_calculator_service.calculate_cash_flow(
            cash_flow_data,
            months=3
        )
        
        # Revenue stability assessment
        sales_history = [
            SalesRecord(
                period=record["period"],
                revenue=record["sales"]["total_revenue"],
                date=datetime.fromisoformat(record["recorded_date"])
            )
            for record in financial_records
        ]
        
        stability = financial_calculator_service.assess_revenue_stability(
            [{"revenue": sr.revenue, "period": sr.period} for sr in sales_history]
        )
        
        # Calculate creditworthiness
        creditworthiness = self.calculate_creditworthiness({
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "profit_margin": profit_margin,
            "cash_balance": latest_record["cash_flow"]["closing_balance"],
            "total_debt": 0.0,  # Would be extracted from data
            "monthly_income": total_revenue,
            "revenue_stability": stability.score,
            "cash_flow_projection": cash_flow_projection
        })
        
        # Generate simple language explanations
        explanations = self._generate_explanations(
            profit_margin,
            net_profit,
            cash_flow_projection,
            stability
        )
        
        # Create summary
        summary = FinancialSummary(
            enterprise_id=enterprise_id,
            enterprise_name=enterprise_name or enterprise_id,
            period_covered=latest_record["period"],
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            net_profit=net_profit,
            profit_margin=profit_margin,
            current_cash_balance=latest_record["cash_flow"]["closing_balance"],
            cash_flow_projection={
                "months": cash_flow_projection.months,
                "projected_closing_balance": cash_flow_projection.projected_closing_balance,
                "has_shortfall": cash_flow_projection.has_shortfall,
                "shortfall_month": cash_flow_projection.shortfall_month
            },
            revenue_stability={
                "score": stability.score,
                "trend": stability.trend,
                "assessment": stability.assessment
            },
            creditworthiness=creditworthiness,
            explanations=explanations
        )
        
        return summary
    
    def calculate_creditworthiness(
        self,
        financial_data: Dict[str, Any]
    ) -> CreditworthinessScore:
        """
        Calculate creditworthiness indicators.
        
        Args:
            financial_data: Dictionary with financial metrics
            
        Returns:
            CreditworthinessScore with indicators and recommendations
        """
        # Calculate debt-to-income ratio
        dti_ratio = financial_calculator_service.calculate_debt_to_income({
            "total_debt": financial_data.get("total_debt", 0.0),
            "monthly_income": financial_data.get("monthly_income", 0.0)
        })
        
        # Get revenue stability
        revenue_stability = financial_data.get("revenue_stability", 0.0)
        
        # Get profit margin
        profit_margin = financial_data.get("profit_margin", 0.0)
        
        # Assess cash flow health
        cash_flow_projection = financial_data.get("cash_flow_projection")
        if cash_flow_projection and cash_flow_projection.has_shortfall:
            cash_flow_health = "At Risk"
        elif financial_data.get("cash_balance", 0.0) < 0:
            cash_flow_health = "Poor"
        else:
            cash_flow_health = "Healthy"
        
        # Calculate overall score (0-100)
        # Weighted scoring:
        # - DTI ratio: 30% (lower is better)
        # - Revenue stability: 30%
        # - Profit margin: 25%
        # - Cash flow: 15%
        
        # DTI score (inverse - lower DTI is better)
        dti_score = max(0, 100 - dti_ratio) if dti_ratio < 100 else 0
        
        # Revenue stability score (0-1 to 0-100)
        stability_score = revenue_stability * 100
        
        # Profit margin score (normalize to 0-100, assuming 50% is excellent)
        margin_score = min(100, (profit_margin / 50) * 100) if profit_margin > 0 else 0
        
        # Cash flow score
        if cash_flow_health == "Healthy":
            cf_score = 100
        elif cash_flow_health == "At Risk":
            cf_score = 50
        else:
            cf_score = 0
        
        # Weighted overall score
        overall_score = (
            dti_score * 0.30 +
            stability_score * 0.30 +
            margin_score * 0.25 +
            cf_score * 0.15
        )
        
        # Overall assessment
        if overall_score >= 80:
            assessment = "Excellent"
        elif overall_score >= 60:
            assessment = "Good"
        elif overall_score >= 40:
            assessment = "Fair"
        else:
            assessment = "Needs Improvement"
        
        # Generate recommendations
        recommendations = []
        
        if dti_ratio > 40:
            recommendations.append(
                "Consider reducing debt burden to improve creditworthiness"
            )
        
        if revenue_stability < 0.6:
            recommendations.append(
                "Focus on stabilizing revenue streams through diversification"
            )
        
        if profit_margin < 10:
            recommendations.append(
                "Work on improving profit margins by reducing costs or increasing prices"
            )
        
        if cash_flow_health != "Healthy":
            recommendations.append(
                "Improve cash flow management by reducing receivables and managing payables"
            )
        
        if not recommendations:
            recommendations.append(
                "Maintain current financial practices and continue monitoring key metrics"
            )
        
        return CreditworthinessScore(
            score=round(overall_score, 1),
            indicators=CreditworthinessIndicators(
                debt_to_income_ratio=dti_ratio,
                revenue_stability_score=revenue_stability,
                profit_margin=profit_margin,
                cash_flow_health=cash_flow_health,
                overall_assessment=assessment
            ),
            recommendations=recommendations
        )
    
    def export_summary_pdf(
        self,
        summary: FinancialSummary
    ) -> str:
        """
        Export summary as PDF to S3.
        
        Args:
            summary: FinancialSummary object
            
        Returns:
            S3 presigned URL for shareable PDF
        """
        if not pdf_export_service:
            raise RuntimeError("PDF export service not available. Install reportlab.")
        
        url = pdf_export_service.export_and_upload(summary)
        return url
    
    def process(self, query: str, context: UserContext, intent: str) -> str:
        """
        Process financial query.
        
        Args:
            query: User query
            context: User context
            intent: Classified intent
            
        Returns:
            Response text
        """
        query_lower = query.lower()
        
        # Generate financial summary
        if "summary" in query_lower or "report" in query_lower:
            try:
                summary = self.generate_financial_summary(
                    context.enterprise_id,
                    context.enterprise_profile.get("name") if context.enterprise_profile else None
                )
                
                response = (
                    f"आपकी वित्तीय रिपोर्ट तैयार है:\n\n"
                    f"कुल राजस्व: ₹{summary.total_revenue:,.2f}\n"
                    f"कुल खर्च: ₹{summary.total_expenses:,.2f}\n"
                    f"शुद्ध लाभ: ₹{summary.net_profit:,.2f}\n"
                    f"लाभ मार्जिन: {summary.profit_margin:.1f}%\n\n"
                    f"साख योग्यता स्कोर: {summary.creditworthiness.score:.1f}/100\n"
                    f"मूल्यांकन: {summary.creditworthiness.indicators.overall_assessment}\n\n"
                )
                
                # Add recommendations
                if summary.creditworthiness.recommendations:
                    response += "सिफारिशें:\n"
                    for i, rec in enumerate(summary.creditworthiness.recommendations[:2], 1):
                        response += f"{i}. {rec}\n"
                
                return response
                
            except Exception as e:
                return (
                    "मुझे आपकी वित्तीय रिपोर्ट तैयार करने में समस्या हो रही है। "
                    "कृपया सुनिश्चित करें कि आपने अपना वित्तीय डेटा प्रदान किया है।"
                )
        
        # Default response
        return (
            "मैं आपकी वित्तीय जानकारी के साथ मदद कर सकता हूं। "
            "आप मुझसे वित्तीय सारांश, साख रिपोर्ट, या ऋण सलाह के बारे में पूछ सकते हैं।"
        )
    
    def _fetch_financial_data(self, enterprise_id: str) -> List[Dict[str, Any]]:
        """Fetch financial data from DynamoDB."""
        try:
            response = self.dynamodb.query(
                TableName=self.table_name,
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
                ExpressionAttributeValues={
                    ":pk": {"S": f"ENTERPRISE#{enterprise_id}"},
                    ":sk": {"S": "FINANCIAL#"}
                },
                ScanIndexForward=False,  # Most recent first
                Limit=12  # Last 12 months
            )
            
            items = response.get("Items", [])
            return [self._deserialize_item(item) for item in items]
            
        except Exception:
            return []
    
    def _deserialize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize DynamoDB item."""
        # Simplified deserialization
        result = {}
        for key, value in item.items():
            if "S" in value:
                result[key] = value["S"]
            elif "N" in value:
                result[key] = float(value["N"])
            elif "M" in value:
                result[key] = self._deserialize_item(value["M"])
            elif "L" in value:
                result[key] = [self._deserialize_item({"item": v})["item"] for v in value["L"]]
        return result
    
    def _create_empty_summary(self, enterprise_id: str, enterprise_name: str) -> FinancialSummary:
        """Create empty summary when no data available."""
        return FinancialSummary(
            enterprise_id=enterprise_id,
            enterprise_name=enterprise_name,
            period_covered="N/A",
            total_revenue=0.0,
            total_expenses=0.0,
            net_profit=0.0,
            profit_margin=0.0,
            current_cash_balance=0.0,
            creditworthiness=CreditworthinessScore(
                score=0.0,
                indicators=CreditworthinessIndicators(
                    debt_to_income_ratio=0.0,
                    revenue_stability_score=0.0,
                    profit_margin=0.0,
                    cash_flow_health="Unknown",
                    overall_assessment="Insufficient Data"
                ),
                recommendations=["Please provide financial data to generate assessment"]
            ),
            explanations={
                "status": "No financial data available. Please submit your financial information."
            }
        )
    
    def _generate_explanations(
        self,
        profit_margin: float,
        net_profit: float,
        cash_flow_projection: Any,
        stability: Any
    ) -> Dict[str, str]:
        """Generate simple language explanations."""
        explanations = {}
        
        # Profit margin explanation
        if profit_margin > 20:
            explanations["Profit Margin"] = (
                "आपका लाभ मार्जिन उत्कृष्ट है। आप अपनी बिक्री का अच्छा प्रतिशत लाभ के रूप में रख रहे हैं।"
            )
        elif profit_margin > 10:
            explanations["Profit Margin"] = (
                "आपका लाभ मार्जिन अच्छा है। आप स्वस्थ लाभ कमा रहे हैं।"
            )
        else:
            explanations["Profit Margin"] = (
                "आपका लाभ मार्जिन कम है। लागत कम करने या कीमतें बढ़ाने पर विचार करें।"
            )
        
        # Cash flow explanation
        if cash_flow_projection.has_shortfall:
            explanations["Cash Flow"] = (
                f"चेतावनी: अगले {cash_flow_projection.shortfall_month} महीने में नकदी की कमी हो सकती है। "
                "खर्चों को कम करने या राजस्व बढ़ाने की योजना बनाएं।"
            )
        else:
            explanations["Cash Flow"] = (
                "आपकी नकदी प्रवाह स्थिति स्वस्थ है। अगले कुछ महीनों के लिए पर्याप्त नकदी है।"
            )
        
        # Revenue stability explanation
        explanations["Revenue Stability"] = stability.assessment
        
        return explanations


# Global agent instance
financial_agent = FinancialAgent()
