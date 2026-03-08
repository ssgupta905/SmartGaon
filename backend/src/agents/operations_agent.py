"""Operations Agent for operational monitoring and replanning."""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from src.models.orchestration import UserContext
from src.db.table_schemas import get_table_name
from src.aws_client import get_dynamodb_client

logger = logging.getLogger(__name__)


class InventoryAlert:
    """Inventory alert for low stock conditions."""
    
    def __init__(
        self,
        product: str,
        current_quantity: float,
        reorder_level: float,
        average_monthly_sales: float,
        percentage_remaining: float,
        message: str
    ):
        """Initialize inventory alert."""
        self.product = product
        self.current_quantity = current_quantity
        self.reorder_level = reorder_level
        self.average_monthly_sales = average_monthly_sales
        self.percentage_remaining = percentage_remaining
        self.message = message


class PlanDeviation:
    """Plan deviation for sales or operational metrics."""
    
    def __init__(
        self,
        metric: str,
        planned_value: float,
        actual_value: float,
        deviation_percent: float,
        period: str,
        message: str
    ):
        """Initialize plan deviation."""
        self.metric = metric
        self.planned_value = planned_value
        self.actual_value = actual_value
        self.deviation_percent = deviation_percent
        self.period = period
        self.message = message


class WeeklyReport:
    """Weekly operational summary report."""
    
    def __init__(
        self,
        enterprise_id: str,
        week_start: str,
        week_end: str,
        total_sales: float,
        total_transactions: int,
        inventory_status: Dict[str, Any],
        cash_flow_summary: Dict[str, Any],
        alerts: List[str],
        recommendations: List[str]
    ):
        """Initialize weekly report."""
        self.enterprise_id = enterprise_id
        self.week_start = week_start
        self.week_end = week_end
        self.total_sales = total_sales
        self.total_transactions = total_transactions
        self.inventory_status = inventory_status
        self.cash_flow_summary = cash_flow_summary
        self.alerts = alerts
        self.recommendations = recommendations


class OperationsAgent:
    """
    Bedrock Agent for operational monitoring and replanning.
    
    This agent provides:
    - Operational data tracking (sales, inventory, cash flow)
    - Inventory alert detection (< 20% threshold)
    - Sales deviation detection (> 15% deviation)
    - Weekly summary report generation
    - Corrective action recommendations
    """
    
    def __init__(self):
        """Initialize the operations agent."""
        self.dynamodb = get_dynamodb_client()
        self.operational_data_table = get_table_name("OperationalData")
        self.alerts_table = get_table_name("Alerts")
    
    def process(self, query: str, context: UserContext, intent: str) -> str:
        """
        Process operations query.
        
        Args:
            query: User query text
            context: User context with enterprise profile and entities
            intent: Classified intent
            
        Returns:
            Response text in simple language
        """
        try:
            query_lower = query.lower()
            
            # Check for status query
            if any(keyword in query_lower for keyword in ["status", "स्थिति", "report", "रिपोर्ट"]):
                return self._get_operational_status(context.enterprise_id)
            
            # Check for alerts query
            if any(keyword in query_lower for keyword in ["alert", "चेतावनी", "warning"]):
                alerts = self.check_inventory_alerts(context.enterprise_id)
                deviations = self.detect_plan_deviations(context.enterprise_id)
                return self._format_alerts_response(alerts, deviations)
            
            # Check for weekly report query
            if any(keyword in query_lower for keyword in ["week", "सप्ताह", "weekly"]):
                report = self.generate_weekly_report(context.enterprise_id)
                return self._format_weekly_report_response(report)
            
            # Default operational status
            return self._get_operational_status(context.enterprise_id)
            
        except Exception as e:
            logger.error(f"Operations agent error: {str(e)}", exc_info=True)
            return "मुझे परिचालन की जानकारी प्राप्त करने में समस्या हो रही है। कृपया बाद में पुनः प्रयास करें।"
    
    def track_operations(
        self,
        enterprise_id: str,
        operational_data: Dict[str, Any]
    ) -> None:
        """
        Record operational metrics.
        
        Args:
            enterprise_id: Enterprise identifier
            operational_data: Dictionary with daily_sales, inventory_snapshot, cash_position, date
        """
        try:
            date = operational_data.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
            recorded_timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Prepare item for DynamoDB
            item = {
                "PK": f"ENTERPRISE#{enterprise_id}",
                "SK": f"OPS#{date}",
                "enterprise_id": enterprise_id,
                "date": date,
                "recorded_timestamp": recorded_timestamp,
                "daily_sales": operational_data.get("daily_sales", {}),
                "inventory_snapshot": operational_data.get("inventory_snapshot", {}),
                "cash_position": operational_data.get("cash_position", 0.0),
                "notes": operational_data.get("notes", "")
            }
            
            # Store in DynamoDB
            self.dynamodb.put_item(
                TableName=self.operational_data_table,
                Item=item
            )
            
            logger.info(f"Tracked operations for enterprise {enterprise_id} on {date}")
            
        except Exception as e:
            logger.error(f"Error tracking operations: {str(e)}", exc_info=True)
            raise
    
    def check_inventory_alerts(
        self,
        enterprise_id: str
    ) -> List[InventoryAlert]:
        """
        Check for low inventory conditions.
        
        Triggers alert when inventory < 20% of average monthly sales.
        
        Args:
            enterprise_id: Enterprise identifier
            
        Returns:
            List of InventoryAlert objects
        """
        alerts = []
        
        try:
            # Fetch recent operational data (last 30 days)
            operational_records = self._fetch_operational_data(
                enterprise_id=enterprise_id,
                days=30
            )
            
            if not operational_records:
                logger.warning(f"No operational data found for enterprise {enterprise_id}")
                return alerts
            
            # Get latest inventory snapshot
            latest_record = operational_records[0]
            inventory_snapshot = latest_record.get("inventory_snapshot", {})
            products = inventory_snapshot.get("products", [])
            
            if not products:
                return alerts
            
            # Calculate average monthly sales for each product
            product_sales = {}
            for record in operational_records:
                daily_sales = record.get("daily_sales", {})
                products_sold = daily_sales.get("products_sold", [])
                
                for product_sale in products_sold:
                    product_name = product_sale.get("product")
                    quantity = product_sale.get("quantity", 0)
                    
                    if product_name:
                        if product_name not in product_sales:
                            product_sales[product_name] = []
                        product_sales[product_name].append(quantity)
            
            # Check each product for low inventory
            for product_item in products:
                product_name = product_item.get("product")
                current_quantity = product_item.get("quantity", 0)
                reorder_level = product_item.get("reorder_level", 0)
                
                if not product_name:
                    continue
                
                # Calculate average monthly sales
                if product_name in product_sales and product_sales[product_name]:
                    daily_avg = sum(product_sales[product_name]) / len(product_sales[product_name])
                    monthly_avg = daily_avg * 30
                else:
                    # No sales data, use reorder level if available
                    monthly_avg = reorder_level * 5 if reorder_level > 0 else 100
                
                # Calculate percentage remaining
                if monthly_avg > 0:
                    percentage_remaining = (current_quantity / monthly_avg) * 100
                else:
                    percentage_remaining = 100
                
                # Trigger alert if < 20% threshold
                if percentage_remaining < 20:
                    message = (
                        f"{product_name} का स्टॉक कम है। "
                        f"वर्तमान मात्रा: {current_quantity:.1f}, "
                        f"औसत मासिक बिक्री: {monthly_avg:.1f}, "
                        f"शेष: {percentage_remaining:.1f}%। "
                        f"जल्द ही पुनः ऑर्डर करें।"
                    )
                    
                    alerts.append(InventoryAlert(
                        product=product_name,
                        current_quantity=current_quantity,
                        reorder_level=reorder_level,
                        average_monthly_sales=monthly_avg,
                        percentage_remaining=round(percentage_remaining, 1),
                        message=message
                    ))
                    
                    # Also create alert in Alerts table
                    self._create_alert(
                        enterprise_id=enterprise_id,
                        alert_type="INVENTORY",
                        severity="WARNING",
                        title=f"Low Inventory: {product_name}",
                        message=message
                    )
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking inventory alerts: {str(e)}", exc_info=True)
            return alerts
    
    def detect_plan_deviations(
        self,
        enterprise_id: str
    ) -> List[PlanDeviation]:
        """
        Detect deviations from planned metrics.
        
        Triggers alert when actual sales deviate from planned sales by > 15%.
        
        Args:
            enterprise_id: Enterprise identifier
            
        Returns:
            List of PlanDeviation objects
        """
        deviations = []
        
        try:
            # Fetch operational data for current month
            current_month = datetime.utcnow().strftime("%Y-%m")
            operational_records = self._fetch_operational_data(
                enterprise_id=enterprise_id,
                days=30
            )
            
            if not operational_records:
                return deviations
            
            # Calculate actual sales for the month
            actual_sales = 0.0
            for record in operational_records:
                daily_sales = record.get("daily_sales", {})
                actual_sales += daily_sales.get("total", 0.0)
            
            # For MVP, use a simple planned sales estimate
            # In production, this would come from a business plan or forecast
            # Estimate: average of last 3 months
            historical_records = self._fetch_operational_data(
                enterprise_id=enterprise_id,
                days=90
            )
            
            if len(historical_records) > 30:
                # Calculate average monthly sales from historical data
                historical_monthly_sales = []
                current_month_sales = 0.0
                current_month_str = ""
                
                for record in historical_records:
                    record_date = record.get("date", "")
                    month_str = record_date[:7] if len(record_date) >= 7 else ""
                    
                    if month_str != current_month_str:
                        if current_month_str and current_month_sales > 0:
                            historical_monthly_sales.append(current_month_sales)
                        current_month_str = month_str
                        current_month_sales = 0.0
                    
                    daily_sales = record.get("daily_sales", {})
                    current_month_sales += daily_sales.get("total", 0.0)
                
                if historical_monthly_sales:
                    planned_sales = sum(historical_monthly_sales) / len(historical_monthly_sales)
                else:
                    # No historical data, can't detect deviation
                    return deviations
            else:
                # Not enough historical data
                return deviations
            
            # Calculate deviation percentage
            if planned_sales > 0:
                deviation_percent = ((actual_sales - planned_sales) / planned_sales) * 100
            else:
                deviation_percent = 0.0
            
            # Trigger alert if deviation > 15%
            if abs(deviation_percent) > 15:
                if deviation_percent > 0:
                    message = (
                        f"बिक्री योजना से {abs(deviation_percent):.1f}% अधिक है। "
                        f"योजनाबद्ध: ₹{planned_sales:,.2f}, "
                        f"वास्तविक: ₹{actual_sales:,.2f}। "
                        f"बढ़िया प्रदर्शन!"
                    )
                    severity = "INFO"
                else:
                    message = (
                        f"बिक्री योजना से {abs(deviation_percent):.1f}% कम है। "
                        f"योजनाबद्ध: ₹{planned_sales:,.2f}, "
                        f"वास्तविक: ₹{actual_sales:,.2f}। "
                        f"बिक्री बढ़ाने के उपाय करें।"
                    )
                    severity = "WARNING"
                
                deviations.append(PlanDeviation(
                    metric="sales",
                    planned_value=planned_sales,
                    actual_value=actual_sales,
                    deviation_percent=round(deviation_percent, 1),
                    period=current_month,
                    message=message
                ))
                
                # Create alert in Alerts table
                self._create_alert(
                    enterprise_id=enterprise_id,
                    alert_type="PLAN_DEVIATION",
                    severity=severity,
                    title=f"Sales Deviation: {current_month}",
                    message=message
                )
            
            return deviations
            
        except Exception as e:
            logger.error(f"Error detecting plan deviations: {str(e)}", exc_info=True)
            return deviations
    
    def generate_weekly_report(
        self,
        enterprise_id: str,
        week_start_date: Optional[str] = None
    ) -> WeeklyReport:
        """
        Generate weekly operational summary.
        
        Args:
            enterprise_id: Enterprise identifier
            week_start_date: Optional week start date (YYYY-MM-DD), defaults to current week
            
        Returns:
            WeeklyReport with sales, inventory, cash flow, alerts, recommendations
        """
        try:
            # Determine week boundaries
            if week_start_date:
                week_start = datetime.fromisoformat(week_start_date)
            else:
                # Start from Monday of current week
                today = datetime.utcnow()
                week_start = today - timedelta(days=today.weekday())
            
            week_end = week_start + timedelta(days=6)
            
            # Fetch operational data for the week
            operational_records = self._fetch_operational_data(
                enterprise_id=enterprise_id,
                days=7,
                start_date=week_start.strftime("%Y-%m-%d")
            )
            
            # Calculate weekly metrics
            total_sales = 0.0
            total_transactions = 0
            product_sales = {}
            cash_positions = []
            
            for record in operational_records:
                daily_sales = record.get("daily_sales", {})
                total_sales += daily_sales.get("total", 0.0)
                total_transactions += daily_sales.get("transactions", 0)
                
                # Aggregate product sales
                products_sold = daily_sales.get("products_sold", [])
                for product_sale in products_sold:
                    product_name = product_sale.get("product")
                    quantity = product_sale.get("quantity", 0)
                    revenue = product_sale.get("revenue", 0)
                    
                    if product_name:
                        if product_name not in product_sales:
                            product_sales[product_name] = {"quantity": 0, "revenue": 0}
                        product_sales[product_name]["quantity"] += quantity
                        product_sales[product_name]["revenue"] += revenue
                
                # Track cash positions
                cash_position = record.get("cash_position", 0.0)
                if cash_position > 0:
                    cash_positions.append(cash_position)
            
            # Get latest inventory status
            inventory_status = {}
            if operational_records:
                latest_record = operational_records[0]
                inventory_snapshot = latest_record.get("inventory_snapshot", {})
                products = inventory_snapshot.get("products", [])
                
                inventory_status = {
                    "total_products": len(products),
                    "products": [
                        {
                            "product": p.get("product"),
                            "quantity": p.get("quantity", 0),
                            "value": p.get("value", 0)
                        }
                        for p in products
                    ]
                }
            
            # Calculate cash flow summary
            cash_flow_summary = {}
            if cash_positions:
                cash_flow_summary = {
                    "opening_balance": cash_positions[-1] if len(cash_positions) > 0 else 0.0,
                    "closing_balance": cash_positions[0] if len(cash_positions) > 0 else 0.0,
                    "average_balance": sum(cash_positions) / len(cash_positions)
                }
            
            # Check for alerts
            inventory_alerts = self.check_inventory_alerts(enterprise_id)
            plan_deviations = self.detect_plan_deviations(enterprise_id)
            
            alerts = []
            if inventory_alerts:
                alerts.append(f"{len(inventory_alerts)} inventory alert(s)")
            if plan_deviations:
                alerts.append(f"{len(plan_deviations)} plan deviation(s)")
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                total_sales=total_sales,
                inventory_alerts=inventory_alerts,
                plan_deviations=plan_deviations,
                cash_flow_summary=cash_flow_summary
            )
            
            return WeeklyReport(
                enterprise_id=enterprise_id,
                week_start=week_start.strftime("%Y-%m-%d"),
                week_end=week_end.strftime("%Y-%m-%d"),
                total_sales=round(total_sales, 2),
                total_transactions=total_transactions,
                inventory_status=inventory_status,
                cash_flow_summary=cash_flow_summary,
                alerts=alerts,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {str(e)}", exc_info=True)
            raise
    
    def _fetch_operational_data(
        self,
        enterprise_id: str,
        days: int = 30,
        start_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch operational data from DynamoDB.
        
        Args:
            enterprise_id: Enterprise identifier
            days: Number of days to fetch
            start_date: Optional start date (YYYY-MM-DD)
            
        Returns:
            List of operational records sorted by date (most recent first)
        """
        try:
            # Calculate date range
            if start_date:
                end_date = datetime.fromisoformat(start_date) + timedelta(days=days)
                start_sk = f"OPS#{start_date}"
                end_sk = f"OPS#{end_date.strftime('%Y-%m-%d')}"
            else:
                end_date = datetime.utcnow()
                start_date_obj = end_date - timedelta(days=days)
                start_sk = f"OPS#{start_date_obj.strftime('%Y-%m-%d')}"
                end_sk = f"OPS#{end_date.strftime('%Y-%m-%d')}"
            
            # Query DynamoDB
            response = self.dynamodb.query(
                TableName=self.operational_data_table,
                KeyConditionExpression="PK = :pk AND SK BETWEEN :start_sk AND :end_sk",
                ExpressionAttributeValues={
                    ":pk": f"ENTERPRISE#{enterprise_id}",
                    ":start_sk": start_sk,
                    ":end_sk": end_sk
                },
                ScanIndexForward=False  # Most recent first
            )
            
            return response.get("Items", [])
            
        except Exception as e:
            logger.error(f"Error fetching operational data: {str(e)}", exc_info=True)
            return []
    
    def _create_alert(
        self,
        enterprise_id: str,
        alert_type: str,
        severity: str,
        title: str,
        message: str
    ) -> None:
        """Create alert in Alerts table."""
        try:
            alert_id = str(uuid.uuid4())
            created_date = datetime.utcnow().isoformat() + "Z"
            
            # Calculate TTL (30 days from now)
            ttl = int((datetime.utcnow() + timedelta(days=30)).timestamp())
            
            item = {
                "PK": f"ENTERPRISE#{enterprise_id}",
                "SK": f"ALERT#{alert_id}",
                "alert_id": alert_id,
                "enterprise_id": enterprise_id,
                "alert_type": alert_type,
                "severity": severity,
                "title": title,
                "message": message,
                "created_date": created_date,
                "alert_status": "PENDING",
                "status": "PENDING",
                "delivery_method": "IN_APP",
                "action_required": True,
                "ttl": ttl
            }
            
            self.dynamodb.put_item(
                TableName=self.alerts_table,
                Item=item
            )
            
            logger.info(f"Created alert {alert_id} for enterprise {enterprise_id}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}", exc_info=True)
    
    def _generate_recommendations(
        self,
        total_sales: float,
        inventory_alerts: List[InventoryAlert],
        plan_deviations: List[PlanDeviation],
        cash_flow_summary: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on operational data."""
        recommendations = []
        
        # Inventory recommendations
        if inventory_alerts:
            recommendations.append(
                f"{len(inventory_alerts)} उत्पादों का स्टॉक कम है। जल्द ही पुनः ऑर्डर करें।"
            )
        
        # Sales deviation recommendations
        for deviation in plan_deviations:
            if deviation.deviation_percent < -15:
                recommendations.append(
                    "बिक्री बढ़ाने के लिए मार्केटिंग और प्रचार पर ध्यान दें।"
                )
            elif deviation.deviation_percent > 15:
                recommendations.append(
                    "बढ़िया बिक्री! इस गति को बनाए रखें और स्टॉक बढ़ाने पर विचार करें।"
                )
        
        # Cash flow recommendations
        if cash_flow_summary:
            closing_balance = cash_flow_summary.get("closing_balance", 0)
            if closing_balance < 10000:
                recommendations.append(
                    "नकदी की स्थिति कमजोर है। खर्चों को कम करें और प्राप्तियों में तेजी लाएं।"
                )
        
        # General recommendation if no issues
        if not recommendations:
            recommendations.append(
                "सभी परिचालन सामान्य हैं। वर्तमान प्रथाओं को जारी रखें।"
            )
        
        return recommendations
    
    def _get_operational_status(self, enterprise_id: str) -> str:
        """Get current operational status summary."""
        try:
            # Fetch recent data
            operational_records = self._fetch_operational_data(
                enterprise_id=enterprise_id,
                days=7
            )
            
            if not operational_records:
                return (
                    "आपके लिए कोई परिचालन डेटा उपलब्ध नहीं है। "
                    "कृपया अपना दैनिक बिक्री और इन्वेंट्री डेटा प्रदान करें।"
                )
            
            # Calculate weekly sales
            weekly_sales = sum(
                record.get("daily_sales", {}).get("total", 0.0)
                for record in operational_records
            )
            
            # Get latest cash position
            latest_cash = operational_records[0].get("cash_position", 0.0)
            
            # Check alerts
            inventory_alerts = self.check_inventory_alerts(enterprise_id)
            plan_deviations = self.detect_plan_deviations(enterprise_id)
            
            # Format response
            response = "आपकी परिचालन स्थिति:\n\n"
            response += f"इस सप्ताह की बिक्री: ₹{weekly_sales:,.2f}\n"
            response += f"नकदी की स्थिति: ₹{latest_cash:,.2f}\n\n"
            
            if inventory_alerts:
                response += f"चेतावनी: {len(inventory_alerts)} उत्पादों का स्टॉक कम है\n"
            
            if plan_deviations:
                for deviation in plan_deviations:
                    if deviation.deviation_percent < 0:
                        response += f"चेतावनी: बिक्री योजना से {abs(deviation.deviation_percent):.1f}% कम\n"
            
            if not inventory_alerts and not plan_deviations:
                response += "कोई महत्वपूर्ण चेतावनी नहीं। सभी परिचालन सामान्य हैं।"
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting operational status: {str(e)}", exc_info=True)
            return "परिचालन स्थिति प्राप्त करने में त्रुटि।"
    
    def _format_alerts_response(
        self,
        inventory_alerts: List[InventoryAlert],
        plan_deviations: List[PlanDeviation]
    ) -> str:
        """Format alerts response in simple language."""
        if not inventory_alerts and not plan_deviations:
            return "कोई सक्रिय चेतावनी नहीं। सभी परिचालन सामान्य हैं।"
        
        response = "सक्रिय चेतावनियां:\n\n"
        
        if inventory_alerts:
            response += "इन्वेंट्री चेतावनियां:\n"
            for i, alert in enumerate(inventory_alerts[:3], 1):
                response += f"{i}. {alert.message}\n"
            response += "\n"
        
        if plan_deviations:
            response += "योजना विचलन:\n"
            for i, deviation in enumerate(plan_deviations[:3], 1):
                response += f"{i}. {deviation.message}\n"
        
        return response
    
    def _format_weekly_report_response(self, report: WeeklyReport) -> str:
        """Format weekly report response in simple language."""
        response = f"साप्ताहिक रिपोर्ट ({report.week_start} से {report.week_end}):\n\n"
        
        response += f"कुल बिक्री: ₹{report.total_sales:,.2f}\n"
        response += f"कुल लेनदेन: {report.total_transactions}\n\n"
        
        if report.inventory_status:
            total_products = report.inventory_status.get("total_products", 0)
            response += f"इन्वेंट्री: {total_products} उत्पाद\n\n"
        
        if report.cash_flow_summary:
            closing_balance = report.cash_flow_summary.get("closing_balance", 0)
            response += f"नकदी शेष: ₹{closing_balance:,.2f}\n\n"
        
        if report.alerts:
            response += "चेतावनियां:\n"
            for alert in report.alerts:
                response += f"- {alert}\n"
            response += "\n"
        
        if report.recommendations:
            response += "सिफारिशें:\n"
            for i, rec in enumerate(report.recommendations[:3], 1):
                response += f"{i}. {rec}\n"
        
        return response


# Global agent instance
operations_agent = OperationsAgent()
