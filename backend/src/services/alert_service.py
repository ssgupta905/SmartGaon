"""Alert Management Service for GramSaarthi AI."""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from src.db.table_schemas import get_table_name
from src.aws_client import get_dynamodb_client

logger = logging.getLogger(__name__)


class AlertService:
    """
    Service for managing alerts in the GramSaarthi AI platform.
    
    This service provides:
    - Alert creation with automatic TTL (30 days)
    - Alert retrieval with filtering by status and type
    - Alert status updates (delivered, acknowledged)
    - Centralized alert management for all agents
    
    Alert Types:
    - PRICE: Market price alerts
    - SCHEME: Government scheme notifications
    - DEADLINE: Action plan deadline reminders
    - INVENTORY: Low inventory warnings
    - PLAN_DEVIATION: Sales/operational deviations
    
    Alert Statuses:
    - PENDING: Alert created but not yet delivered
    - DELIVERED: Alert delivered to user
    - ACKNOWLEDGED: User acknowledged the alert
    - DISMISSED: User dismissed the alert
    """
    
    def __init__(self):
        """Initialize the alert service."""
        self.dynamodb = get_dynamodb_client()
        self.alerts_table = get_table_name("Alerts")
    
    def create_alert(
        self,
        enterprise_id: str,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        delivery_method: str = "IN_APP",
        action_required: bool = False,
        related_entity_id: Optional[str] = None
    ) -> str:
        """
        Create a new alert.
        
        Args:
            enterprise_id: Enterprise identifier
            alert_type: Type of alert (PRICE, SCHEME, DEADLINE, INVENTORY, PLAN_DEVIATION)
            severity: Alert severity (INFO, WARNING, CRITICAL)
            title: Alert title
            message: Alert message
            delivery_method: How to deliver alert (VOICE_CALL, SMS, IN_APP)
            action_required: Whether user action is required
            related_entity_id: Optional ID of related entity (scheme_id, plan_id, etc.)
            
        Returns:
            Alert ID
            
        Raises:
            ValueError: If alert_type or severity is invalid
        """
        # Validate alert type
        valid_alert_types = ["PRICE", "SCHEME", "DEADLINE", "INVENTORY", "PLAN_DEVIATION"]
        if alert_type not in valid_alert_types:
            raise ValueError(f"Invalid alert_type. Must be one of: {valid_alert_types}")
        
        # Validate severity
        valid_severities = ["INFO", "WARNING", "CRITICAL"]
        if severity not in valid_severities:
            raise ValueError(f"Invalid severity. Must be one of: {valid_severities}")
        
        try:
            alert_id = str(uuid.uuid4())
            created_date = datetime.utcnow().isoformat() + "Z"
            
            # Calculate TTL (30 days from now)
            ttl = int((datetime.utcnow() + timedelta(days=30)).timestamp())
            
            # Prepare alert item
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
                "status": "PENDING",
                "alert_status": "PENDING",  # For GSI1
                "delivery_method": delivery_method,
                "action_required": action_required,
                "ttl": ttl
            }
            
            # Add optional related entity ID
            if related_entity_id:
                item["related_entity_id"] = related_entity_id
            
            # Store in DynamoDB
            self.dynamodb.put_item(
                TableName=self.alerts_table,
                Item=item
            )
            
            logger.info(
                f"Created alert {alert_id} for enterprise {enterprise_id}: "
                f"type={alert_type}, severity={severity}"
            )
            
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}", exc_info=True)
            raise
    
    def get_alerts(
        self,
        enterprise_id: str,
        status: Optional[str] = None,
        alert_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve alerts for an enterprise with optional filtering.
        
        Args:
            enterprise_id: Enterprise identifier
            status: Optional status filter (PENDING, DELIVERED, ACKNOWLEDGED, DISMISSED)
            alert_type: Optional type filter (PRICE, SCHEME, DEADLINE, INVENTORY, PLAN_DEVIATION)
            limit: Maximum number of alerts to return (default: 50)
            
        Returns:
            List of alert dictionaries sorted by created_date (most recent first)
        """
        try:
            # Query all alerts for the enterprise
            response = self.dynamodb.query(
                TableName=self.alerts_table,
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
                ExpressionAttributeValues={
                    ":pk": f"ENTERPRISE#{enterprise_id}",
                    ":sk_prefix": "ALERT#"
                },
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            alerts = response.get("Items", [])
            
            # Apply status filter if provided
            if status:
                alerts = [
                    alert for alert in alerts
                    if alert.get("status") == status
                ]
            
            # Apply alert_type filter if provided
            if alert_type:
                alerts = [
                    alert for alert in alerts
                    if alert.get("alert_type") == alert_type
                ]
            
            logger.info(
                f"Retrieved {len(alerts)} alerts for enterprise {enterprise_id} "
                f"(status={status}, type={alert_type})"
            )
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error retrieving alerts: {str(e)}", exc_info=True)
            return []
    
    def mark_delivered(
        self,
        enterprise_id: str,
        alert_id: str
    ) -> bool:
        """
        Mark an alert as delivered.
        
        Args:
            enterprise_id: Enterprise identifier
            alert_id: Alert identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            delivery_timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Update alert status
            self.dynamodb.update_item(
                TableName=self.alerts_table,
                Key={
                    "PK": f"ENTERPRISE#{enterprise_id}",
                    "SK": f"ALERT#{alert_id}"
                },
                UpdateExpression="SET #status = :status, #alert_status = :status, delivery_timestamp = :timestamp",
                ExpressionAttributeNames={
                    "#status": "status",
                    "#alert_status": "alert_status"
                },
                ExpressionAttributeValues={
                    ":status": "DELIVERED",
                    ":timestamp": delivery_timestamp
                }
            )
            
            logger.info(f"Marked alert {alert_id} as delivered for enterprise {enterprise_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking alert as delivered: {str(e)}", exc_info=True)
            return False
    
    def mark_acknowledged(
        self,
        enterprise_id: str,
        alert_id: str
    ) -> bool:
        """
        Mark an alert as acknowledged by the user.
        
        Args:
            enterprise_id: Enterprise identifier
            alert_id: Alert identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            acknowledged_timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Update alert status
            self.dynamodb.update_item(
                TableName=self.alerts_table,
                Key={
                    "PK": f"ENTERPRISE#{enterprise_id}",
                    "SK": f"ALERT#{alert_id}"
                },
                UpdateExpression="SET #status = :status, #alert_status = :status, acknowledged_timestamp = :timestamp",
                ExpressionAttributeNames={
                    "#status": "status",
                    "#alert_status": "alert_status"
                },
                ExpressionAttributeValues={
                    ":status": "ACKNOWLEDGED",
                    ":timestamp": acknowledged_timestamp
                }
            )
            
            logger.info(f"Marked alert {alert_id} as acknowledged for enterprise {enterprise_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking alert as acknowledged: {str(e)}", exc_info=True)
            return False
    
    def mark_dismissed(
        self,
        enterprise_id: str,
        alert_id: str
    ) -> bool:
        """
        Mark an alert as dismissed by the user.
        
        Args:
            enterprise_id: Enterprise identifier
            alert_id: Alert identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            dismissed_timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Update alert status
            self.dynamodb.update_item(
                TableName=self.alerts_table,
                Key={
                    "PK": f"ENTERPRISE#{enterprise_id}",
                    "SK": f"ALERT#{alert_id}"
                },
                UpdateExpression="SET #status = :status, #alert_status = :status, dismissed_timestamp = :timestamp",
                ExpressionAttributeNames={
                    "#status": "status",
                    "#alert_status": "alert_status"
                },
                ExpressionAttributeValues={
                    ":status": "DISMISSED",
                    ":timestamp": dismissed_timestamp
                }
            )
            
            logger.info(f"Marked alert {alert_id} as dismissed for enterprise {enterprise_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking alert as dismissed: {str(e)}", exc_info=True)
            return False
    
    def get_pending_alerts(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all pending alerts across all enterprises using GSI1.
        
        This is useful for batch processing alerts for delivery.
        
        Args:
            limit: Maximum number of alerts to return (default: 100)
            
        Returns:
            List of pending alert dictionaries
        """
        try:
            # Query GSI1 for all pending alerts
            response = self.dynamodb.query(
                TableName=self.alerts_table,
                IndexName="GSI1-AlertsByStatus",
                KeyConditionExpression="alert_status = :status",
                ExpressionAttributeValues={
                    ":status": "PENDING"
                },
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            alerts = response.get("Items", [])
            
            logger.info(f"Retrieved {len(alerts)} pending alerts across all enterprises")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error retrieving pending alerts: {str(e)}", exc_info=True)
            return []
    
    def get_alerts_by_type(
        self,
        enterprise_id: str,
        alert_type: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get alerts of a specific type for an enterprise.
        
        Args:
            enterprise_id: Enterprise identifier
            alert_type: Alert type (PRICE, SCHEME, DEADLINE, INVENTORY, PLAN_DEVIATION)
            limit: Maximum number of alerts to return (default: 20)
            
        Returns:
            List of alert dictionaries
        """
        return self.get_alerts(
            enterprise_id=enterprise_id,
            alert_type=alert_type,
            limit=limit
        )
    
    def get_alerts_by_status(
        self,
        enterprise_id: str,
        status: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get alerts with a specific status for an enterprise.
        
        Args:
            enterprise_id: Enterprise identifier
            status: Alert status (PENDING, DELIVERED, ACKNOWLEDGED, DISMISSED)
            limit: Maximum number of alerts to return (default: 20)
            
        Returns:
            List of alert dictionaries
        """
        return self.get_alerts(
            enterprise_id=enterprise_id,
            status=status,
            limit=limit
        )
    
    def delete_alert(
        self,
        enterprise_id: str,
        alert_id: str
    ) -> bool:
        """
        Delete an alert (for testing or admin purposes).
        
        Note: Alerts are automatically deleted after 30 days via TTL.
        
        Args:
            enterprise_id: Enterprise identifier
            alert_id: Alert identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.dynamodb.delete_item(
                TableName=self.alerts_table,
                Key={
                    "PK": f"ENTERPRISE#{enterprise_id}",
                    "SK": f"ALERT#{alert_id}"
                }
            )
            
            logger.info(f"Deleted alert {alert_id} for enterprise {enterprise_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting alert: {str(e)}", exc_info=True)
            return False


# Global service instance
alert_service = AlertService()
