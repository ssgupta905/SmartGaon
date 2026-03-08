"""
Analytics service for logging agent interactions and platform events.

This module provides functionality to log all agent interactions to the
AnalyticsEvents DynamoDB table for monitoring, debugging, and analytics.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from src.aws_client import aws_client
from src.models.orchestration import AgentType, OrchestrationResult

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for logging analytics events to DynamoDB.
    
    Logs agent interactions including timestamp, agent used, intent,
    latency, success status, and additional metadata.
    """
    
    def __init__(self, table_name: str = "AnalyticsEvents"):
        """
        Initialize the analytics service.
        
        Args:
            table_name: Name of the DynamoDB table for analytics events
        """
        self.table_name = table_name
        self.dynamodb = aws_client.dynamodb
        self.table = self.dynamodb.Table(table_name)
    
    def log_agent_interaction(
        self,
        orchestration_result: OrchestrationResult,
        enterprise_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Log an agent interaction event.
        
        Args:
            orchestration_result: Result from orchestrator containing agent details
            enterprise_id: Optional enterprise identifier
            session_id: Optional session identifier
            
        Returns:
            Event ID of the logged event
        """
        event_id = str(uuid.uuid4())
        timestamp = orchestration_result.timestamp
        date_str = timestamp.strftime("%Y-%m-%d")
        timestamp_str = timestamp.isoformat()
        
        # Prepare agent information
        agents_used = [agent.value for agent in orchestration_result.agents_invoked]
        
        # Create event item
        event_item = {
            "PK": f"EVENT#{date_str}",
            "SK": f"{timestamp_str}#{event_id}",
            "event_id": event_id,
            "timestamp": timestamp_str,
            "event_type": "AGENT_INTERACTION",
            "intent": orchestration_result.intent,
            "agents_used": agents_used,
            "latency_ms": orchestration_result.total_execution_time_ms,
            "success": orchestration_result.success,
            "query": orchestration_result.query,
        }
        
        # Add optional fields
        if enterprise_id:
            event_item["enterprise_id"] = enterprise_id
        
        if session_id:
            event_item["session_id"] = session_id
        
        if not orchestration_result.success and orchestration_result.error_message:
            event_item["error_message"] = orchestration_result.error_message
        
        # Add metadata about individual agent responses
        agent_metadata = {}
        for agent_type, response in orchestration_result.agent_responses.items():
            agent_metadata[agent_type.value] = {
                "success": response.success,
                "latency_ms": response.execution_time_ms,
                "confidence": response.confidence
            }
            if not response.success and response.error_message:
                agent_metadata[agent_type.value]["error"] = response.error_message
        
        event_item["agent_metadata"] = agent_metadata
        
        # Set TTL for auto-deletion after 90 days
        ttl_timestamp = int((timestamp + timedelta(days=90)).timestamp())
        event_item["ttl"] = ttl_timestamp
        
        try:
            # Store event in DynamoDB
            self.table.put_item(Item=event_item)
            logger.info(f"Logged agent interaction event: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to log agent interaction: {str(e)}", exc_info=True)
            # Don't raise exception - logging failures shouldn't break the main flow
            return event_id
    
    def log_event(
        self,
        event_type: str,
        success: bool,
        latency_ms: Optional[float] = None,
        enterprise_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> str:
        """
        Log a generic platform event.
        
        Args:
            event_type: Type of event (e.g., REGISTRATION, QUERY, ALERT)
            success: Whether the event was successful
            latency_ms: Optional latency in milliseconds
            enterprise_id: Optional enterprise identifier
            session_id: Optional session identifier
            metadata: Optional additional metadata
            error_message: Optional error message if event failed
            
        Returns:
            Event ID of the logged event
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        date_str = timestamp.strftime("%Y-%m-%d")
        timestamp_str = timestamp.isoformat()
        
        # Create event item
        event_item = {
            "PK": f"EVENT#{date_str}",
            "SK": f"{timestamp_str}#{event_id}",
            "event_id": event_id,
            "timestamp": timestamp_str,
            "event_type": event_type,
            "success": success,
        }
        
        # Add optional fields
        if latency_ms is not None:
            event_item["latency_ms"] = latency_ms
        
        if enterprise_id:
            event_item["enterprise_id"] = enterprise_id
        
        if session_id:
            event_item["session_id"] = session_id
        
        if metadata:
            event_item["metadata"] = metadata
        
        if error_message:
            event_item["error_message"] = error_message
        
        # Set TTL for auto-deletion after 90 days
        ttl_timestamp = int((timestamp + timedelta(days=90)).timestamp())
        event_item["ttl"] = ttl_timestamp
        
        try:
            # Store event in DynamoDB
            self.table.put_item(Item=event_item)
            logger.info(f"Logged event: {event_type} ({event_id})")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to log event: {str(e)}", exc_info=True)
            # Don't raise exception - logging failures shouldn't break the main flow
            return event_id
    
    def get_events_by_date(
        self,
        date: datetime,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve events for a specific date.
        
        Args:
            date: Date to retrieve events for
            event_type: Optional filter by event type
            
        Returns:
            List of event items
        """
        date_str = date.strftime("%Y-%m-%d")
        
        try:
            response = self.table.query(
                KeyConditionExpression="PK = :pk",
                ExpressionAttributeValues={
                    ":pk": f"EVENT#{date_str}"
                }
            )
            
            events = response.get("Items", [])
            
            # Filter by event type if specified
            if event_type:
                events = [e for e in events if e.get("event_type") == event_type]
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve events: {str(e)}", exc_info=True)
            return []
    
    def get_events_by_enterprise(
        self,
        enterprise_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve events for a specific enterprise.
        
        Note: This requires scanning the table as enterprise_id is not part of the key.
        For production, consider adding a GSI on enterprise_id.
        
        Args:
            enterprise_id: Enterprise identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of event items
        """
        try:
            # Use scan with filter (not optimal for large datasets)
            filter_expression = "enterprise_id = :eid"
            expression_values = {":eid": enterprise_id}
            
            response = self.table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeValues=expression_values
            )
            
            events = response.get("Items", [])
            
            # Apply date filters if specified
            if start_date or end_date:
                filtered_events = []
                for event in events:
                    event_time = datetime.fromisoformat(event["timestamp"])
                    if start_date and event_time < start_date:
                        continue
                    if end_date and event_time > end_date:
                        continue
                    filtered_events.append(event)
                events = filtered_events
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve enterprise events: {str(e)}", exc_info=True)
            return []
    
    def get_analytics_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get analytics summary for a date range.
        
        Args:
            start_date: Start date for summary
            end_date: End date for summary
            
        Returns:
            Dictionary with analytics metrics
        """
        all_events = []
        current_date = start_date
        
        # Query events for each day in range
        while current_date <= end_date:
            daily_events = self.get_events_by_date(current_date)
            all_events.extend(daily_events)
            current_date += timedelta(days=1)
        
        # Calculate summary metrics
        total_events = len(all_events)
        successful_events = sum(1 for e in all_events if e.get("success", False))
        failed_events = total_events - successful_events
        
        # Agent interaction metrics
        agent_interactions = [e for e in all_events if e.get("event_type") == "AGENT_INTERACTION"]
        total_queries = len(agent_interactions)
        
        # Calculate average latency
        latencies = [e.get("latency_ms", 0) for e in all_events if "latency_ms" in e]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        # Count by intent
        intent_counts = {}
        for event in agent_interactions:
            intent = event.get("intent", "UNKNOWN")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        # Count by agent type
        agent_counts = {}
        for event in agent_interactions:
            agents = event.get("agents_used", [])
            for agent in agents:
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        # Count unique enterprises
        unique_enterprises = len(set(
            e.get("enterprise_id") 
            for e in all_events 
            if e.get("enterprise_id")
        ))
        
        return {
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": successful_events / total_events if total_events > 0 else 0,
            "total_queries": total_queries,
            "average_latency_ms": avg_latency,
            "intent_distribution": intent_counts,
            "agent_usage": agent_counts,
            "unique_enterprises": unique_enterprises,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
