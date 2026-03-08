"""API routes for scheme execution functionality."""

import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Path, Body
from pydantic import BaseModel, Field

from src.agents.scheme_execution_agent import scheme_execution_agent

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/schemes",
    tags=["schemes"],
)


# Request/Response models
class ActionPlanRequest(BaseModel):
    """Request to generate action plan."""
    
    enterprise_id: str = Field(..., description="Enterprise identifier")
    scheme_id: str = Field(..., description="Scheme identifier")


class StepStatusUpdate(BaseModel):
    """Request to update step status."""
    
    status: str = Field(..., description="New status (PENDING, IN_PROGRESS, COMPLETED)")
    notes: str = Field(default="", description="Optional notes about step completion")


class SchemeDiscoveryResponse(BaseModel):
    """Response for scheme discovery."""
    
    schemes: List[Dict[str, Any]] = Field(..., description="List of eligible schemes")
    count: int = Field(..., description="Number of schemes found")


class ActionPlanResponse(BaseModel):
    """Response for action plan generation."""
    
    action_plan_id: str = Field(..., description="Action plan identifier")
    scheme_name: str = Field(..., description="Scheme name")
    steps: List[Dict[str, Any]] = Field(..., description="Action steps")
    contact_info: Dict[str, Any] = Field(..., description="Contact information")
    created_date: str = Field(..., description="Creation timestamp")


class PlanProgressResponse(BaseModel):
    """Response for plan progress."""
    
    plan_id: str = Field(..., description="Action plan identifier")
    total_steps: int = Field(..., description="Total number of steps")
    completed_steps: int = Field(..., description="Number of completed steps")
    current_step: Optional[Dict[str, Any]] = Field(None, description="Current active step")
    progress_percentage: float = Field(..., description="Progress percentage")
    status: str = Field(..., description="Overall plan status")


class StepUpdateResponse(BaseModel):
    """Response for step status update."""
    
    success: bool = Field(..., description="Whether update succeeded")
    message: str = Field(..., description="Status message")
    progress_percentage: float = Field(..., description="Updated progress percentage")


# API Endpoints

@router.get(
    "/discover/{enterprise_id}",
    response_model=SchemeDiscoveryResponse,
    summary="Discover eligible schemes",
    description="Find government schemes that match the enterprise's eligibility criteria"
)
async def discover_schemes(
    enterprise_id: str = Path(..., description="Enterprise identifier")
) -> SchemeDiscoveryResponse:
    """
    Discover eligible schemes for an enterprise.
    
    This endpoint:
    1. Fetches the enterprise profile
    2. Matches against all available schemes
    3. Ranks schemes by relevance and benefit
    4. Returns top 3 most relevant schemes
    
    Args:
        enterprise_id: Enterprise identifier
        
    Returns:
        SchemeDiscoveryResponse with list of eligible schemes
        
    Raises:
        HTTPException: If enterprise not found or error occurs
    """
    try:
        # Fetch enterprise profile
        from src.services.enterprise_profile_service import enterprise_profile_service
        
        profile = enterprise_profile_service.get_profile(enterprise_id)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Enterprise not found: {enterprise_id}"
            )
        
        # Convert profile to dict format
        profile_dict = profile.dict() if hasattr(profile, 'dict') else profile
        
        # Discover schemes
        schemes = scheme_execution_agent.discover_schemes(profile_dict)
        
        return SchemeDiscoveryResponse(
            schemes=schemes,
            count=len(schemes)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error discovering schemes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error discovering schemes: {str(e)}"
        )


@router.post(
    "/action-plan",
    response_model=ActionPlanResponse,
    summary="Generate action plan",
    description="Generate step-by-step action plan for applying to a scheme"
)
async def generate_action_plan(
    request: ActionPlanRequest = Body(..., description="Action plan request")
) -> ActionPlanResponse:
    """
    Generate action plan for scheme application.
    
    This endpoint:
    1. Fetches scheme details
    2. Generates step-by-step action plan
    3. Stores plan in DynamoDB
    4. Returns plan with steps, documents, deadlines
    
    Args:
        request: ActionPlanRequest with enterprise_id and scheme_id
        
    Returns:
        ActionPlanResponse with action plan details
        
    Raises:
        HTTPException: If scheme not found or error occurs
    """
    try:
        # Generate action plan
        action_plan = scheme_execution_agent.generate_action_plan(
            scheme_id=request.scheme_id,
            enterprise_id=request.enterprise_id
        )
        
        return ActionPlanResponse(
            action_plan_id=action_plan.plan_id,
            scheme_name=action_plan.scheme_name,
            steps=action_plan.steps,
            contact_info=action_plan.contact_info,
            created_date=action_plan.created_date
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating action plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating action plan: {str(e)}"
        )


@router.get(
    "/action-plan/{plan_id}",
    response_model=PlanProgressResponse,
    summary="Get action plan progress",
    description="Get current progress and status of an action plan"
)
async def get_plan_progress(
    plan_id: str = Path(..., description="Action plan identifier")
) -> PlanProgressResponse:
    """
    Get action plan progress.
    
    This endpoint:
    1. Fetches action plan from DynamoDB
    2. Calculates progress percentage
    3. Identifies current active step
    4. Returns progress details
    
    Args:
        plan_id: Action plan identifier
        
    Returns:
        PlanProgressResponse with progress details
        
    Raises:
        HTTPException: If plan not found or error occurs
    """
    try:
        # Track progress
        progress = scheme_execution_agent.track_progress(plan_id)
        
        return PlanProgressResponse(
            plan_id=progress.plan_id,
            total_steps=progress.total_steps,
            completed_steps=progress.completed_steps,
            current_step=progress.current_step,
            progress_percentage=progress.progress_percentage,
            status=progress.status
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error tracking plan progress: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error tracking plan progress: {str(e)}"
        )


@router.put(
    "/action-plan/{plan_id}/step/{step_id}",
    response_model=StepUpdateResponse,
    summary="Update step status",
    description="Mark a step as completed or update its status"
)
async def update_step_status(
    plan_id: str = Path(..., description="Action plan identifier"),
    step_id: str = Path(..., description="Step identifier"),
    update: StepStatusUpdate = Body(..., description="Step status update")
) -> StepUpdateResponse:
    """
    Update step status in action plan.
    
    This endpoint:
    1. Fetches action plan from DynamoDB
    2. Updates step status and completion date
    3. Recalculates progress percentage
    4. Updates plan status if all steps completed
    
    Args:
        plan_id: Action plan identifier
        step_id: Step identifier
        update: StepStatusUpdate with new status and notes
        
    Returns:
        StepUpdateResponse with success status and updated progress
        
    Raises:
        HTTPException: If plan or step not found or error occurs
    """
    try:
        # Validate status
        valid_statuses = ["PENDING", "IN_PROGRESS", "COMPLETED"]
        if update.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Update step status
        scheme_execution_agent.update_step_status(
            action_plan_id=plan_id,
            step_id=step_id,
            status=update.status,
            notes=update.notes
        )
        
        # Get updated progress
        progress = scheme_execution_agent.track_progress(plan_id)
        
        return StepUpdateResponse(
            success=True,
            message=f"Step {step_id} updated to {update.status}",
            progress_percentage=progress.progress_percentage
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating step status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error updating step status: {str(e)}"
        )


# Health check for scheme routes
@router.get(
    "/health",
    summary="Scheme routes health check",
    description="Check if scheme routes are operational"
)
async def scheme_routes_health():
    """Health check for scheme routes."""
    return {
        "status": "healthy",
        "service": "scheme_routes",
        "endpoints": [
            "GET /api/v1/schemes/discover/{enterprise_id}",
            "POST /api/v1/schemes/action-plan",
            "GET /api/v1/schemes/action-plan/{plan_id}",
            "PUT /api/v1/schemes/action-plan/{plan_id}/step/{step_id}"
        ]
    }
