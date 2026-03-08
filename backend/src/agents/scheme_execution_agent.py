"""Scheme Execution Agent for government scheme discovery and action planning."""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from src.services.scheme_matching_service import scheme_matching_service
from src.models.orchestration import UserContext
from src.db.table_schemas import get_table_name
from src.aws_client import get_dynamodb_client

logger = logging.getLogger(__name__)


class ActionPlan:
    """Action plan for scheme application."""
    
    def __init__(
        self,
        plan_id: str,
        enterprise_id: str,
        scheme_id: str,
        scheme_name: str,
        steps: List[Dict[str, Any]],
        contact_info: Dict[str, Any],
        created_date: str,
        status: str = "IN_PROGRESS"
    ):
        """Initialize action plan."""
        self.plan_id = plan_id
        self.enterprise_id = enterprise_id
        self.scheme_id = scheme_id
        self.scheme_name = scheme_name
        self.steps = steps
        self.contact_info = contact_info
        self.created_date = created_date
        self.status = status
        self.progress_percentage = 0.0


class PlanProgress:
    """Progress tracking for action plan."""
    
    def __init__(
        self,
        plan_id: str,
        total_steps: int,
        completed_steps: int,
        current_step: Optional[Dict[str, Any]],
        progress_percentage: float,
        status: str
    ):
        """Initialize plan progress."""
        self.plan_id = plan_id
        self.total_steps = total_steps
        self.completed_steps = completed_steps
        self.current_step = current_step
        self.progress_percentage = progress_percentage
        self.status = status


class SchemeExecutionAgent:
    """
    Bedrock Agent for government scheme discovery and execution.
    
    This agent provides:
    - Scheme discovery based on eligibility
    - Action plan generation with steps
    - Progress tracking and reminders
    - Step completion management
    """
    
    def __init__(self):
        """Initialize the scheme execution agent."""
        self.matching_service = scheme_matching_service
        self.dynamodb = get_dynamodb_client()
        self.action_plans_table = get_table_name("ActionPlans")
        self.schemes_table = get_table_name("Schemes")
        # Import alert service here to avoid circular imports
        from src.services.alert_service import alert_service
        self.alert_service = alert_service
    
    def process(self, query: str, context: UserContext, intent: str) -> str:
        """
        Process scheme execution query.
        
        Args:
            query: User query text
            context: User context with enterprise profile and entities
            intent: Classified intent
            
        Returns:
            Response text in simple language
        """
        try:
            if intent == "SCHEME_DISCOVERY":
                # Discover eligible schemes
                if not context.enterprise_profile:
                    return "कृपया पहले अपना प्रोफाइल पूरा करें।"
                
                matches = self.discover_schemes(context.enterprise_profile)
                return self._format_scheme_discovery_response(matches)
            
            elif intent == "SCHEME_APPLICATION":
                # Generate action plan for selected scheme
                scheme_name = context.entities.get("scheme_name")
                if not scheme_name:
                    return "कृपया बताएं कि आप किस योजना के लिए आवेदन करना चाहते हैं।"
                
                # Find scheme by name (simplified for MVP)
                scheme = self._find_scheme_by_name(scheme_name)
                if not scheme:
                    return f"{scheme_name} योजना नहीं मिली। कृपया सही नाम बताएं।"
                
                action_plan = self.generate_action_plan(
                    scheme_id=scheme["scheme_id"],
                    enterprise_id=context.enterprise_id
                )
                
                return self._format_action_plan_response(action_plan)
            
            else:
                return self._get_help_message()
                
        except Exception as e:
            logger.error(f"Scheme execution agent error: {str(e)}", exc_info=True)
            return "मुझे योजना की जानकारी प्राप्त करने में समस्या हो रही है। कृपया बाद में पुनः प्रयास करें।"
    
    def discover_schemes(
        self,
        enterprise_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find eligible schemes based on enterprise profile.
        
        Args:
            enterprise_profile: Enterprise profile data
            
        Returns:
            List of schemes ranked by relevance (top 3)
        """
        # Fetch all schemes from DynamoDB
        schemes = self._fetch_all_schemes()
        
        if not schemes:
            logger.warning("No schemes found in database")
            return []
        
        # Match eligibility for each scheme
        eligibility_results = []
        for scheme in schemes:
            result = self.matching_service.match_eligibility(
                profile=enterprise_profile,
                scheme=scheme
            )
            eligibility_results.append(result)
        
        # Rank schemes by relevance
        ranked_matches = self.matching_service.rank_schemes(
            matches=eligibility_results,
            schemes=schemes
        )
        
        # Convert to response format
        scheme_matches = []
        for match in ranked_matches:
            scheme = next(
                (s for s in schemes if s.get("scheme_id") == match.scheme_id),
                None
            )
            if scheme:
                scheme_matches.append({
                    "scheme_id": match.scheme_id,
                    "scheme_name": match.scheme_name,
                    "scheme_type": match.scheme_type,
                    "match_score": match.match_score,
                    "relevance_score": match.relevance_score,
                    "benefit_amount": match.benefit_amount,
                    "description": match.description,
                    "benefits": match.benefits,
                    "name_local": scheme.get("name_local", {}),
                    "description_local": scheme.get("description_local", {})
                })
        
        return scheme_matches
    
    def generate_action_plan(
        self,
        scheme_id: str,
        enterprise_id: str
    ) -> ActionPlan:
        """
        Generate step-by-step action plan for scheme application.
        
        Args:
            scheme_id: Scheme identifier
            enterprise_id: Enterprise identifier
            
        Returns:
            ActionPlan with steps, documents, deadlines, contacts
        """
        # Fetch scheme details
        scheme = self._fetch_scheme(scheme_id)
        
        if not scheme:
            raise ValueError(f"Scheme not found: {scheme_id}")
        
        # Generate action steps
        action_steps = self.matching_service.generate_plan_steps(scheme)
        
        # Convert steps to dict format
        steps_data = []
        for step in action_steps:
            steps_data.append({
                "step_id": step.step_id,
                "step_number": step.step_number,
                "description": step.description,
                "required_documents": step.required_documents,
                "deadline": step.deadline,
                "status": "PENDING",
                "completed_date": None,
                "notes": ""
            })
        
        # Create action plan
        plan_id = str(uuid.uuid4())
        created_date = datetime.utcnow().isoformat() + "Z"
        
        contact_info = scheme.get("application_process", {}).get("contact_info", {})
        
        action_plan = ActionPlan(
            plan_id=plan_id,
            enterprise_id=enterprise_id,
            scheme_id=scheme_id,
            scheme_name=scheme.get("name", ""),
            steps=steps_data,
            contact_info=contact_info,
            created_date=created_date,
            status="IN_PROGRESS"
        )
        
        # Store action plan in DynamoDB
        self._store_action_plan(action_plan)
        
        return action_plan
    
    def track_progress(
        self,
        action_plan_id: str
    ) -> PlanProgress:
        """
        Get current progress on action plan.
        
        Args:
            action_plan_id: Action plan identifier
            
        Returns:
            PlanProgress with completion status
        """
        # Fetch action plan from DynamoDB
        plan_data = self._fetch_action_plan(action_plan_id)
        
        if not plan_data:
            raise ValueError(f"Action plan not found: {action_plan_id}")
        
        steps = plan_data.get("steps", [])
        total_steps = len(steps)
        completed_steps = sum(1 for s in steps if s.get("status") == "COMPLETED")
        
        # Calculate progress percentage
        if total_steps > 0:
            progress_percentage = (completed_steps / total_steps) * 100
        else:
            progress_percentage = 0.0
        
        # Find current step (first pending step)
        current_step = None
        for step in steps:
            if step.get("status") == "PENDING":
                current_step = step
                break
        
        # Determine overall status
        if completed_steps == total_steps:
            status = "COMPLETED"
        elif completed_steps > 0:
            status = "IN_PROGRESS"
        else:
            status = "NOT_STARTED"
        
        return PlanProgress(
            plan_id=action_plan_id,
            total_steps=total_steps,
            completed_steps=completed_steps,
            current_step=current_step,
            progress_percentage=round(progress_percentage, 1),
            status=status
        )
    
    def update_step_status(
        self,
        action_plan_id: str,
        step_id: str,
        status: str,
        notes: str = ""
    ) -> None:
        """
        Mark step as complete and advance plan.
        
        Args:
            action_plan_id: Action plan identifier
            step_id: Step identifier
            status: New status (COMPLETED, IN_PROGRESS, PENDING)
            notes: Optional notes about step completion
        """
        # Fetch action plan
        plan_data = self._fetch_action_plan(action_plan_id)
        
        if not plan_data:
            raise ValueError(f"Action plan not found: {action_plan_id}")
        
        # Update step status
        steps = plan_data.get("steps", [])
        step_found = False
        
        for step in steps:
            if step.get("step_id") == step_id:
                step["status"] = status
                if status == "COMPLETED":
                    step["completed_date"] = datetime.utcnow().isoformat() + "Z"
                if notes:
                    step["notes"] = notes
                step_found = True
                break
        
        if not step_found:
            raise ValueError(f"Step not found: {step_id}")
        
        # Calculate progress
        total_steps = len(steps)
        completed_steps = sum(1 for s in steps if s.get("status") == "COMPLETED")
        progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
        
        # Update plan status
        if completed_steps == total_steps:
            plan_status = "COMPLETED"
        else:
            plan_status = "IN_PROGRESS"
        
        # Update in DynamoDB
        self._update_action_plan(
            action_plan_id=action_plan_id,
            enterprise_id=plan_data["enterprise_id"],
            steps=steps,
            progress_percentage=progress_percentage,
            status=plan_status
        )
    
    def check_deadline_reminders(
        self,
        enterprise_id: str
    ) -> List[str]:
        """
        Check for upcoming deadlines (within 3 days) and create reminder alerts.
        
        Args:
            enterprise_id: Enterprise identifier
            
        Returns:
            List of alert IDs created
        """
        alert_ids = []
        
        try:
            # Fetch all active action plans for the enterprise
            response = self.dynamodb.query(
                TableName=self.action_plans_table,
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
                ExpressionAttributeValues={
                    ":pk": f"ENTERPRISE#{enterprise_id}",
                    ":sk_prefix": "PLAN#"
                }
            )
            
            plans = response.get("Items", [])
            
            # Check each plan for upcoming deadlines
            for plan in plans:
                # Skip completed plans
                if plan.get("status") == "COMPLETED":
                    continue
                
                steps = plan.get("steps", [])
                scheme_name = plan.get("scheme_name", "Unknown Scheme")
                
                for step in steps:
                    # Only check pending steps
                    if step.get("status") != "PENDING":
                        continue
                    
                    deadline_str = step.get("deadline")
                    if not deadline_str:
                        continue
                    
                    # Parse deadline
                    try:
                        deadline = datetime.fromisoformat(deadline_str.replace("Z", ""))
                    except (ValueError, AttributeError):
                        continue
                    
                    # Calculate days until deadline
                    now = datetime.utcnow()
                    days_until = (deadline - now).days
                    
                    # Trigger alert if deadline is within 3 days
                    if 0 <= days_until <= 3:
                        step_desc = step.get("description", "Step")
                        
                        if days_until == 0:
                            severity = "CRITICAL"
                            message = (
                                f"आज {scheme_name} के लिए समय सीमा है! "
                                f"चरण: {step_desc}। "
                                f"कृपया तुरंत पूरा करें।"
                            )
                        elif days_until == 1:
                            severity = "WARNING"
                            message = (
                                f"{scheme_name} के लिए समय सीमा कल है। "
                                f"चरण: {step_desc}। "
                                f"कृपया जल्द पूरा करें।"
                            )
                        else:
                            severity = "INFO"
                            message = (
                                f"{scheme_name} के लिए समय सीमा {days_until} दिनों में है। "
                                f"चरण: {step_desc}। "
                                f"कृपया समय पर पूरा करें।"
                            )
                        
                        # Create alert using alert service
                        alert_id = self.alert_service.create_alert(
                            enterprise_id=enterprise_id,
                            alert_type="DEADLINE",
                            severity=severity,
                            title=f"Deadline Reminder: {scheme_name}",
                            message=message,
                            delivery_method="VOICE_CALL",
                            action_required=True,
                            related_entity_id=plan.get("plan_id")
                        )
                        
                        alert_ids.append(alert_id)
                        logger.info(
                            f"Created deadline reminder for enterprise {enterprise_id}: "
                            f"{scheme_name}, {days_until} days until deadline"
                        )
            
            return alert_ids
            
        except Exception as e:
            logger.error(f"Error checking deadline reminders: {str(e)}", exc_info=True)
            return alert_ids
    
    def notify_new_scheme(
        self,
        scheme_id: str,
        eligible_enterprise_ids: List[str]
    ) -> List[str]:
        """
        Create notifications for new schemes matching enterprise profiles.
        
        Args:
            scheme_id: New scheme identifier
            eligible_enterprise_ids: List of enterprise IDs that match eligibility
            
        Returns:
            List of alert IDs created
        """
        alert_ids = []
        
        try:
            # Fetch scheme details
            scheme = self._fetch_scheme(scheme_id)
            
            if not scheme:
                logger.warning(f"Scheme not found: {scheme_id}")
                return alert_ids
            
            scheme_name = scheme.get("name", "New Scheme")
            scheme_type = scheme.get("scheme_type", "")
            benefit_amount = scheme.get("benefits", {}).get("benefit_amount", 0)
            
            # Get Hindi name if available
            name_local = scheme.get("name_local", {})
            scheme_name_hi = name_local.get("hi", scheme_name)
            
            # Create alert for each eligible enterprise
            for enterprise_id in eligible_enterprise_ids:
                type_text = {
                    "LOAN": "ऋण",
                    "GRANT": "अनुदान",
                    "SUBSIDY": "सब्सिडी",
                    "TRAINING": "प्रशिक्षण"
                }.get(scheme_type, scheme_type)
                
                message = (
                    f"नई योजना उपलब्ध: {scheme_name_hi}। "
                    f"प्रकार: {type_text}। "
                )
                
                if benefit_amount > 0:
                    message += f"लाभ: ₹{benefit_amount:,.0f}। "
                
                message += "अधिक जानकारी के लिए पूछें।"
                
                # Create alert using alert service
                alert_id = self.alert_service.create_alert(
                    enterprise_id=enterprise_id,
                    alert_type="SCHEME",
                    severity="INFO",
                    title=f"New Scheme Available: {scheme_name}",
                    message=message,
                    delivery_method="VOICE_CALL",
                    action_required=False,
                    related_entity_id=scheme_id
                )
                
                alert_ids.append(alert_id)
                logger.info(
                    f"Created new scheme notification for enterprise {enterprise_id}: "
                    f"{scheme_name}"
                )
            
            return alert_ids
            
        except Exception as e:
            logger.error(f"Error notifying new scheme: {str(e)}", exc_info=True)
            return alert_ids
    
    def _fetch_all_schemes(self) -> List[Dict[str, Any]]:
        """Fetch all schemes from DynamoDB."""
        try:
            response = self.dynamodb.scan(
                TableName=self.schemes_table,
                FilterExpression="SK = :sk",
                ExpressionAttributeValues={
                    ":sk": "METADATA"
                }
            )
            return response.get("Items", [])
        except Exception as e:
            logger.error(f"Error fetching schemes: {str(e)}", exc_info=True)
            return []
    
    def _fetch_scheme(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single scheme from DynamoDB."""
        try:
            response = self.dynamodb.get_item(
                TableName=self.schemes_table,
                Key={
                    "PK": f"SCHEME#{scheme_id}",
                    "SK": "METADATA"
                }
            )
            return response.get("Item")
        except Exception as e:
            logger.error(f"Error fetching scheme {scheme_id}: {str(e)}", exc_info=True)
            return None
    
    def _find_scheme_by_name(self, scheme_name: str) -> Optional[Dict[str, Any]]:
        """Find scheme by name (simplified search)."""
        schemes = self._fetch_all_schemes()
        scheme_name_lower = scheme_name.lower()
        
        for scheme in schemes:
            if scheme_name_lower in scheme.get("name", "").lower():
                return scheme
        
        return None
    
    def _store_action_plan(self, action_plan: ActionPlan) -> None:
        """Store action plan in DynamoDB."""
        try:
            # Calculate next reminder date (3 days before first deadline)
            next_reminder_date = None
            for step in action_plan.steps:
                if step.get("deadline"):
                    deadline = datetime.fromisoformat(step["deadline"].replace("Z", ""))
                    reminder = deadline - timedelta(days=3)
                    next_reminder_date = reminder.isoformat() + "Z"
                    break
            
            item = {
                "PK": f"ENTERPRISE#{action_plan.enterprise_id}",
                "SK": f"PLAN#{action_plan.plan_id}",
                "plan_id": action_plan.plan_id,
                "enterprise_id": action_plan.enterprise_id,
                "scheme_id": action_plan.scheme_id,
                "scheme_name": action_plan.scheme_name,
                "created_date": action_plan.created_date,
                "status": action_plan.status,
                "steps": action_plan.steps,
                "progress_percentage": 0.0,
                "next_reminder_date": next_reminder_date,
                "contact_info": action_plan.contact_info
            }
            
            self.dynamodb.put_item(
                TableName=self.action_plans_table,
                Item=item
            )
            
            logger.info(f"Stored action plan {action_plan.plan_id} for enterprise {action_plan.enterprise_id}")
            
        except Exception as e:
            logger.error(f"Error storing action plan: {str(e)}", exc_info=True)
            raise
    
    def _fetch_action_plan(self, action_plan_id: str) -> Optional[Dict[str, Any]]:
        """Fetch action plan from DynamoDB."""
        try:
            # Need to scan since we don't have enterprise_id
            # In production, would use GSI or maintain plan_id index
            response = self.dynamodb.scan(
                TableName=self.action_plans_table,
                FilterExpression="plan_id = :plan_id",
                ExpressionAttributeValues={
                    ":plan_id": action_plan_id
                }
            )
            
            items = response.get("Items", [])
            return items[0] if items else None
            
        except Exception as e:
            logger.error(f"Error fetching action plan {action_plan_id}: {str(e)}", exc_info=True)
            return None
    
    def _update_action_plan(
        self,
        action_plan_id: str,
        enterprise_id: str,
        steps: List[Dict[str, Any]],
        progress_percentage: float,
        status: str
    ) -> None:
        """Update action plan in DynamoDB."""
        try:
            self.dynamodb.update_item(
                TableName=self.action_plans_table,
                Key={
                    "PK": f"ENTERPRISE#{enterprise_id}",
                    "SK": f"PLAN#{action_plan_id}"
                },
                UpdateExpression="SET steps = :steps, progress_percentage = :progress, #status = :status",
                ExpressionAttributeNames={
                    "#status": "status"
                },
                ExpressionAttributeValues={
                    ":steps": steps,
                    ":progress": progress_percentage,
                    ":status": status
                }
            )
            
            logger.info(f"Updated action plan {action_plan_id}")
            
        except Exception as e:
            logger.error(f"Error updating action plan: {str(e)}", exc_info=True)
            raise
    
    def _format_scheme_discovery_response(
        self,
        matches: List[Dict[str, Any]]
    ) -> str:
        """Format scheme discovery response in simple language."""
        if not matches:
            return (
                "आपके लिए कोई योजना नहीं मिली। "
                "कृपया अपना प्रोफाइल अपडेट करें या बाद में पुनः प्रयास करें।"
            )
        
        response = f"आपके लिए {len(matches)} योजनाएं मिलीं:\n\n"
        
        for i, match in enumerate(matches, 1):
            name_hi = match.get("name_local", {}).get("hi", match["scheme_name"])
            benefit = match["benefit_amount"]
            scheme_type = match["scheme_type"]
            
            type_text = {
                "LOAN": "ऋण",
                "GRANT": "अनुदान",
                "SUBSIDY": "सब्सिडी",
                "TRAINING": "प्रशिक्षण"
            }.get(scheme_type, scheme_type)
            
            response += f"{i}. {name_hi}\n"
            response += f"   प्रकार: {type_text}\n"
            response += f"   लाभ: ₹{benefit:,.0f}\n"
            response += f"   मैच स्कोर: {match['match_score']*100:.0f}%\n\n"
        
        response += "किसी योजना के लिए आवेदन करने के लिए, योजना का नाम बताएं।"
        
        return response
    
    def _format_action_plan_response(
        self,
        action_plan: ActionPlan
    ) -> str:
        """Format action plan response in simple language."""
        response = f"{action_plan.scheme_name} के लिए कार्य योजना:\n\n"
        
        for step in action_plan.steps:
            response += f"चरण {step['step_number']}: {step['description']}\n"
            
            if step['required_documents']:
                response += "   आवश्यक दस्तावेज:\n"
                for doc in step['required_documents']:
                    response += f"   - {doc}\n"
            
            if step.get('deadline'):
                response += f"   समय सीमा: {step['deadline']}\n"
            
            response += "\n"
        
        if action_plan.contact_info:
            response += "संपर्क जानकारी:\n"
            if action_plan.contact_info.get("office"):
                response += f"कार्यालय: {action_plan.contact_info['office']}\n"
            if action_plan.contact_info.get("phone"):
                response += f"फोन: {action_plan.contact_info['phone']}\n"
        
        response += f"\nयोजना ID: {action_plan.plan_id}"
        
        return response
    
    def _get_help_message(self) -> str:
        """Get help message for scheme queries."""
        return (
            "मैं आपको सरकारी योजनाओं के बारे में जानकारी दे सकता हूं। "
            "आप पूछ सकते हैं:\n"
            "- मेरे लिए कौन सी योजनाएं हैं?\n"
            "- [योजना का नाम] के लिए आवेदन कैसे करें?\n"
            "- मेरी योजना की प्रगति क्या है?"
        )


# Global agent instance
scheme_execution_agent = SchemeExecutionAgent()
