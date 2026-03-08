"""API request and response models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.enterprise_profile import (
    EnterpriseType,
    Coordinates,
    Location,
    Contact,
    EnterpriseMetadata,
)


class EnterpriseCreateRequest(BaseModel):
    """Request model for creating a new enterprise profile."""
    
    type: EnterpriseType = Field(..., description="Enterprise type")
    name: str = Field(..., min_length=1, description="Enterprise name")
    products: List[str] = Field(
        ..., min_length=1, description="List of products/commodities"
    )
    location: Location = Field(..., description="Enterprise location")
    contact: Contact = Field(..., description="Contact information")
    metadata: Optional[EnterpriseMetadata] = Field(
        None, description="Additional metadata"
    )


class EnterpriseUpdateRequest(BaseModel):
    """Request model for updating an enterprise profile."""
    
    name: Optional[str] = Field(None, min_length=1, description="Enterprise name")
    products: Optional[List[str]] = Field(
        None, min_length=1, description="List of products/commodities"
    )
    location: Optional[Location] = Field(None, description="Enterprise location")
    contact: Optional[Contact] = Field(None, description="Contact information")
    metadata: Optional[EnterpriseMetadata] = Field(
        None, description="Additional metadata"
    )


class EnterpriseResponse(BaseModel):
    """Response model for enterprise profile."""
    
    enterprise_id: str = Field(..., description="Unique enterprise identifier")
    type: EnterpriseType = Field(..., description="Enterprise type")
    name: str = Field(..., description="Enterprise name")
    products: List[str] = Field(..., description="List of products/commodities")
    location: Location = Field(..., description="Enterprise location")
    contact: Contact = Field(..., description="Contact information")
    registration_date: datetime = Field(..., description="Registration timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")
    metadata: Optional[EnterpriseMetadata] = Field(
        None, description="Additional metadata"
    )
    version: int = Field(..., description="Profile version")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(), 
        description="Error timestamp in ISO 8601 format"
    )


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    
    message: str = Field(..., description="Success message")
    enterprise_id: str = Field(..., description="Deleted enterprise identifier")
