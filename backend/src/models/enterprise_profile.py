"""Enterprise profile data models with validation."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class EnterpriseType(str, Enum):
    """Valid enterprise types."""
    
    SHG = "SHG"
    FPO = "FPO"
    COOPERATIVE = "COOPERATIVE"
    MSME = "MSME"


class Coordinates(BaseModel):
    """Geographic coordinates."""
    
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    
    @field_validator("lat", "lon")
    @classmethod
    def validate_coordinates(cls, v: float) -> float:
        """Validate coordinate values are finite."""
        if not isinstance(v, (int, float)):
            raise ValueError("Coordinate must be a number")
        if not (-180 <= v <= 180):
            raise ValueError("Coordinate out of valid range")
        return float(v)


class Location(BaseModel):
    """Enterprise location information."""
    
    state: str = Field(..., min_length=1, description="State name")
    district: str = Field(..., min_length=1, description="District name")
    block: str = Field(..., min_length=1, description="Block name")
    village: str = Field(..., min_length=1, description="Village name")
    coordinates: Coordinates = Field(..., description="Geographic coordinates")
    
    @field_validator("state", "district", "block", "village")
    @classmethod
    def validate_location_fields(cls, v: str) -> str:
        """Validate location fields are non-empty strings."""
        if not v or not v.strip():
            raise ValueError("Location field cannot be empty")
        return v.strip()


class Contact(BaseModel):
    """Enterprise contact information."""
    
    phone: str = Field(..., min_length=10, max_length=15, description="Primary phone number")
    alternate_phone: Optional[str] = Field(
        None, min_length=10, max_length=15, description="Alternate phone number"
    )
    preferred_language: str = Field(
        ..., pattern="^(hi|ta|te)$", description="Preferred language code (hi, ta, te)"
    )
    
    @field_validator("phone", "alternate_phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is None:
            return v
        
        # Remove common separators
        cleaned = v.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        
        # Check if it contains only digits and optional + prefix
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]
        
        if not cleaned.isdigit():
            raise ValueError("Phone number must contain only digits")
        
        if not (10 <= len(cleaned) <= 15):
            raise ValueError("Phone number must be between 10 and 15 digits")
        
        return v


class EnterpriseMetadata(BaseModel):
    """Additional enterprise metadata."""
    
    member_count: Optional[int] = Field(None, ge=1, description="Number of members")
    annual_turnover: Optional[float] = Field(None, ge=0, description="Annual turnover")
    primary_market: Optional[str] = Field(None, description="Primary market location")
    
    @field_validator("member_count")
    @classmethod
    def validate_member_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate member count is positive."""
        if v is not None and v < 1:
            raise ValueError("Member count must be at least 1")
        return v
    
    @field_validator("annual_turnover")
    @classmethod
    def validate_annual_turnover(cls, v: Optional[float]) -> Optional[float]:
        """Validate annual turnover is non-negative."""
        if v is not None and v < 0:
            raise ValueError("Annual turnover cannot be negative")
        return v


class EnterpriseProfile(BaseModel):
    """Complete enterprise profile with validation."""
    
    enterprise_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique enterprise identifier"
    )
    type: EnterpriseType = Field(..., description="Enterprise type")
    name: str = Field(..., min_length=1, description="Enterprise name")
    products: List[str] = Field(
        ..., min_length=1, description="List of products/commodities"
    )
    location: Location = Field(..., description="Enterprise location")
    contact: Contact = Field(..., description="Contact information")
    registration_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Registration timestamp"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    metadata: Optional[EnterpriseMetadata] = Field(
        None, description="Additional metadata"
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Profile version for optimistic locking"
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate enterprise name is non-empty."""
        if not v or not v.strip():
            raise ValueError("Enterprise name cannot be empty")
        return v.strip()
    
    @field_validator("products")
    @classmethod
    def validate_products(cls, v: List[str]) -> List[str]:
        """Validate product list is non-empty and contains valid products."""
        if not v:
            raise ValueError("Products list cannot be empty")
        
        # Remove empty strings and strip whitespace
        cleaned = [p.strip() for p in v if p and p.strip()]
        
        if not cleaned:
            raise ValueError("Products list must contain at least one valid product")
        
        # Check for duplicates
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("Products list contains duplicates")
        
        return cleaned
    
    @model_validator(mode="after")
    def validate_timestamps(self) -> "EnterpriseProfile":
        """Validate timestamp consistency."""
        if self.last_updated < self.registration_date:
            raise ValueError("Last updated cannot be before registration date")
        return self
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format."""
        return {
            "PK": f"ENTERPRISE#{self.enterprise_id}",
            "SK": "PROFILE",
            "enterprise_id": self.enterprise_id,
            "type": self.type.value,
            "name": self.name,
            "products": self.products,
            "location": {
                "state": self.location.state,
                "district": self.location.district,
                "block": self.location.block,
                "village": self.location.village,
                "coordinates": {
                    "lat": Decimal(str(self.location.coordinates.lat)),
                    "lon": Decimal(str(self.location.coordinates.lon)),
                },
            },
            "contact": {
                "phone": self.contact.phone,
                "alternate_phone": self.contact.alternate_phone,
                "preferred_language": self.contact.preferred_language,
            },
            "registration_date": self.registration_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "version": self.version,
            "metadata": (
                {
                    "member_count": self.metadata.member_count,
                    "annual_turnover": Decimal(str(self.metadata.annual_turnover)) if self.metadata.annual_turnover is not None else None,
                    "primary_market": self.metadata.primary_market,
                }
                if self.metadata
                else None
            ),
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> "EnterpriseProfile":
        """Create from DynamoDB item format."""
        return cls(
            enterprise_id=item["enterprise_id"],
            type=EnterpriseType(item["type"]),
            name=item["name"],
            products=item["products"],
            location=Location(
                state=item["location"]["state"],
                district=item["location"]["district"],
                block=item["location"]["block"],
                village=item["location"]["village"],
                coordinates=Coordinates(
                    lat=float(item["location"]["coordinates"]["lat"]),
                    lon=float(item["location"]["coordinates"]["lon"]),
                ),
            ),
            contact=Contact(
                phone=item["contact"]["phone"],
                alternate_phone=item["contact"].get("alternate_phone"),
                preferred_language=item["contact"]["preferred_language"],
            ),
            registration_date=datetime.fromisoformat(item["registration_date"]),
            last_updated=datetime.fromisoformat(item["last_updated"]),
            version=item.get("version", 1),  # Default to 1 for backward compatibility
            metadata=(
                EnterpriseMetadata(
                    member_count=item["metadata"].get("member_count"),
                    annual_turnover=float(item["metadata"]["annual_turnover"]) if item["metadata"].get("annual_turnover") is not None else None,
                    primary_market=item["metadata"].get("primary_market"),
                )
                if item.get("metadata")
                else None
            ),
        )
