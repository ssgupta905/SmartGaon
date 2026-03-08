"""Enterprise profile API routes."""

from typing import Dict, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse

from src.api.models import (
    EnterpriseCreateRequest,
    EnterpriseUpdateRequest,
    EnterpriseResponse,
    ErrorResponse,
    DeleteResponse,
)
from src.models.enterprise_profile import EnterpriseProfile
from src.services.enterprise_profile_service import (
    EnterpriseProfileService,
    ProfileNotFoundError,
    ProfileServiceError,
    ProfileVersionConflictError,
)


router = APIRouter(prefix="/api/v1/enterprises", tags=["enterprises"])


def create_error_response(
    error_type: str,
    message: str,
    details: Dict[str, Any] = None,
    request_id: str = None,
) -> ErrorResponse:
    """Create a standardized error response."""
    return ErrorResponse(
        error=error_type,
        message=message,
        details=details,
        request_id=request_id,
    )


@router.post(
    "",
    response_model=EnterpriseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new enterprise",
    description="Create a new enterprise profile with validation",
    responses={
        201: {"description": "Enterprise successfully created"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_enterprise(
    request: Request,
    enterprise_data: EnterpriseCreateRequest,
) -> EnterpriseResponse:
    """
    Register a new enterprise profile.
    
    Creates a new enterprise with the provided information. The enterprise_id
    is automatically generated and returned in the response.
    
    Args:
        request: FastAPI request object
        enterprise_data: Enterprise profile data
        
    Returns:
        Created enterprise profile with generated enterprise_id
        
    Raises:
        HTTPException: If creation fails
    """
    request_id = str(uuid4())
    
    try:
        # Create profile from request data
        profile = EnterpriseProfile(
            type=enterprise_data.type,
            name=enterprise_data.name,
            products=enterprise_data.products,
            location=enterprise_data.location,
            contact=enterprise_data.contact,
            metadata=enterprise_data.metadata,
        )
        
        # Save to database
        service = EnterpriseProfileService()
        enterprise_id = service.create_profile(profile)
        
        # Return created profile
        return EnterpriseResponse(
            enterprise_id=profile.enterprise_id,
            type=profile.type,
            name=profile.name,
            products=profile.products,
            location=profile.location,
            contact=profile.contact,
            registration_date=profile.registration_date,
            last_updated=profile.last_updated,
            metadata=profile.metadata,
            version=profile.version,
        )
    except ValueError as e:
        # Validation error
        error = create_error_response(
            error_type="VALIDATION_ERROR",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.model_dump(),
        )
    except ProfileServiceError as e:
        # Service error
        error = create_error_response(
            error_type="SERVICE_ERROR",
            message=f"Failed to create enterprise profile: {str(e)}",
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )
    except Exception as e:
        # Unexpected error
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


@router.get(
    "/{enterprise_id}",
    response_model=EnterpriseResponse,
    summary="Get enterprise profile",
    description="Retrieve an enterprise profile by ID",
    responses={
        200: {"description": "Enterprise profile retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Enterprise not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_enterprise(
    request: Request,
    enterprise_id: str,
) -> EnterpriseResponse:
    """
    Retrieve an enterprise profile by ID.
    
    Fetches the complete enterprise profile for the given enterprise_id.
    Optimized for <500ms latency.
    
    Args:
        request: FastAPI request object
        enterprise_id: Unique enterprise identifier
        
    Returns:
        Enterprise profile
        
    Raises:
        HTTPException: If profile not found or retrieval fails
    """
    request_id = str(uuid4())
    
    try:
        service = EnterpriseProfileService()
        profile = service.get_profile(enterprise_id)
        
        return EnterpriseResponse(
            enterprise_id=profile.enterprise_id,
            type=profile.type,
            name=profile.name,
            products=profile.products,
            location=profile.location,
            contact=profile.contact,
            registration_date=profile.registration_date,
            last_updated=profile.last_updated,
            metadata=profile.metadata,
            version=profile.version,
        )
    except ProfileNotFoundError as e:
        error = create_error_response(
            error_type="NOT_FOUND",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.model_dump(),
        )
    except ProfileServiceError as e:
        error = create_error_response(
            error_type="SERVICE_ERROR",
            message=f"Failed to retrieve enterprise profile: {str(e)}",
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )
    except Exception as e:
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


@router.put(
    "/{enterprise_id}",
    response_model=EnterpriseResponse,
    summary="Update enterprise profile",
    description="Update an existing enterprise profile",
    responses={
        200: {"description": "Enterprise profile updated successfully"},
        404: {"model": ErrorResponse, "description": "Enterprise not found"},
        409: {"model": ErrorResponse, "description": "Version conflict"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def update_enterprise(
    request: Request,
    enterprise_id: str,
    updates: EnterpriseUpdateRequest,
) -> EnterpriseResponse:
    """
    Update an enterprise profile.
    
    Updates the specified fields of an enterprise profile. Uses optimistic
    locking to prevent concurrent update conflicts. Only provided fields
    are updated; omitted fields remain unchanged.
    
    Args:
        request: FastAPI request object
        enterprise_id: Unique enterprise identifier
        updates: Fields to update
        
    Returns:
        Updated enterprise profile
        
    Raises:
        HTTPException: If update fails
    """
    request_id = str(uuid4())
    
    try:
        # Convert request to dict, excluding None values
        update_dict = updates.model_dump(exclude_none=True)
        
        if not update_dict:
            error = create_error_response(
                error_type="VALIDATION_ERROR",
                message="No fields provided for update",
                request_id=request_id,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.model_dump(),
            )
        
        # Update profile
        service = EnterpriseProfileService()
        updated_profile = service.update_profile(enterprise_id, update_dict)
        
        return EnterpriseResponse(
            enterprise_id=updated_profile.enterprise_id,
            type=updated_profile.type,
            name=updated_profile.name,
            products=updated_profile.products,
            location=updated_profile.location,
            contact=updated_profile.contact,
            registration_date=updated_profile.registration_date,
            last_updated=updated_profile.last_updated,
            metadata=updated_profile.metadata,
            version=updated_profile.version,
        )
    except ProfileNotFoundError as e:
        error = create_error_response(
            error_type="NOT_FOUND",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.model_dump(),
        )
    except ProfileVersionConflictError as e:
        error = create_error_response(
            error_type="VERSION_CONFLICT",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error.model_dump(),
        )
    except ValueError as e:
        error = create_error_response(
            error_type="VALIDATION_ERROR",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.model_dump(),
        )
    except ProfileServiceError as e:
        error = create_error_response(
            error_type="SERVICE_ERROR",
            message=f"Failed to update enterprise profile: {str(e)}",
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )
    except Exception as e:
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


@router.delete(
    "/{enterprise_id}",
    response_model=DeleteResponse,
    summary="Delete enterprise profile",
    description="Delete an enterprise profile and all associated data",
    responses={
        200: {"description": "Enterprise profile deleted successfully"},
        404: {"model": ErrorResponse, "description": "Enterprise not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_enterprise(
    request: Request,
    enterprise_id: str,
) -> DeleteResponse:
    """
    Delete an enterprise profile.
    
    Permanently deletes the enterprise profile. This operation cannot be undone.
    
    Args:
        request: FastAPI request object
        enterprise_id: Unique enterprise identifier
        
    Returns:
        Deletion confirmation
        
    Raises:
        HTTPException: If deletion fails
    """
    request_id = str(uuid4())
    
    try:
        service = EnterpriseProfileService()
        service.delete_profile(enterprise_id)
        
        return DeleteResponse(
            message="Enterprise profile deleted successfully",
            enterprise_id=enterprise_id,
        )
    except ProfileNotFoundError as e:
        error = create_error_response(
            error_type="NOT_FOUND",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.model_dump(),
        )
    except ProfileServiceError as e:
        error = create_error_response(
            error_type="SERVICE_ERROR",
            message=f"Failed to delete enterprise profile: {str(e)}",
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )
    except Exception as e:
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )
