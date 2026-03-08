"""Unit tests for EnterpriseProfile data model and validation."""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.models import (
    EnterpriseProfile,
    Location,
    Contact,
    Coordinates,
    EnterpriseMetadata,
    EnterpriseType,
)


class TestCoordinates:
    """Test Coordinates model validation."""
    
    def test_valid_coordinates(self):
        """Test valid coordinate values."""
        coords = Coordinates(lat=28.6139, lon=77.2090)  # Delhi
        assert coords.lat == 28.6139
        assert coords.lon == 77.2090
    
    def test_latitude_bounds(self):
        """Test latitude boundary validation."""
        # Valid boundaries
        Coordinates(lat=-90, lon=0)
        Coordinates(lat=90, lon=0)
        
        # Invalid boundaries
        with pytest.raises(ValidationError):
            Coordinates(lat=-91, lon=0)
        
        with pytest.raises(ValidationError):
            Coordinates(lat=91, lon=0)
    
    def test_longitude_bounds(self):
        """Test longitude boundary validation."""
        # Valid boundaries
        Coordinates(lat=0, lon=-180)
        Coordinates(lat=0, lon=180)
        
        # Invalid boundaries
        with pytest.raises(ValidationError):
            Coordinates(lat=0, lon=-181)
        
        with pytest.raises(ValidationError):
            Coordinates(lat=0, lon=181)


class TestLocation:
    """Test Location model validation."""
    
    def test_valid_location(self):
        """Test valid location data."""
        location = Location(
            state="Maharashtra",
            district="Pune",
            block="Haveli",
            village="Katraj",
            coordinates=Coordinates(lat=18.4496, lon=73.8579)
        )
        assert location.state == "Maharashtra"
        assert location.district == "Pune"
    
    def test_empty_location_fields(self):
        """Test that empty location fields are rejected."""
        with pytest.raises(ValidationError):
            Location(
                state="",
                district="Pune",
                block="Haveli",
                village="Katraj",
                coordinates=Coordinates(lat=18.4496, lon=73.8579)
            )
    
    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed from location fields."""
        location = Location(
            state="  Maharashtra  ",
            district=" Pune ",
            block="Haveli",
            village="Katraj",
            coordinates=Coordinates(lat=18.4496, lon=73.8579)
        )
        assert location.state == "Maharashtra"
        assert location.district == "Pune"


class TestContact:
    """Test Contact model validation."""
    
    def test_valid_contact(self):
        """Test valid contact information."""
        contact = Contact(
            phone="9876543210",
            alternate_phone="9123456789",
            preferred_language="hi"
        )
        assert contact.phone == "9876543210"
        assert contact.preferred_language == "hi"
    
    def test_phone_validation(self):
        """Test phone number validation."""
        # Valid phone numbers
        Contact(phone="9876543210", preferred_language="hi")
        Contact(phone="+919876543210", preferred_language="hi")
        Contact(phone="91-9876543210", preferred_language="hi")
        
        # Invalid phone numbers
        with pytest.raises(ValidationError):
            Contact(phone="123", preferred_language="hi")  # Too short
        
        with pytest.raises(ValidationError):
            Contact(phone="abcd1234567890", preferred_language="hi")  # Contains letters
    
    def test_language_validation(self):
        """Test preferred language validation."""
        # Valid languages
        Contact(phone="9876543210", preferred_language="hi")
        Contact(phone="9876543210", preferred_language="ta")
        Contact(phone="9876543210", preferred_language="te")
        
        # Invalid language
        with pytest.raises(ValidationError):
            Contact(phone="9876543210", preferred_language="en")
    
    def test_optional_alternate_phone(self):
        """Test that alternate phone is optional."""
        contact = Contact(
            phone="9876543210",
            preferred_language="hi"
        )
        assert contact.alternate_phone is None


class TestEnterpriseMetadata:
    """Test EnterpriseMetadata model validation."""
    
    def test_valid_metadata(self):
        """Test valid metadata."""
        metadata = EnterpriseMetadata(
            member_count=25,
            annual_turnover=500000.0,
            primary_market="Pune Mandi"
        )
        assert metadata.member_count == 25
        assert metadata.annual_turnover == 500000.0
    
    def test_member_count_validation(self):
        """Test member count must be positive."""
        with pytest.raises(ValidationError):
            EnterpriseMetadata(member_count=0)
        
        with pytest.raises(ValidationError):
            EnterpriseMetadata(member_count=-5)
    
    def test_annual_turnover_validation(self):
        """Test annual turnover must be non-negative."""
        EnterpriseMetadata(annual_turnover=0)  # Zero is valid
        
        with pytest.raises(ValidationError):
            EnterpriseMetadata(annual_turnover=-1000)
    
    def test_all_fields_optional(self):
        """Test that all metadata fields are optional."""
        metadata = EnterpriseMetadata()
        assert metadata.member_count is None
        assert metadata.annual_turnover is None
        assert metadata.primary_market is None


class TestEnterpriseProfile:
    """Test EnterpriseProfile model validation."""
    
    def test_valid_profile(self):
        """Test creating a valid enterprise profile."""
        profile = EnterpriseProfile(
            type=EnterpriseType.SHG,
            name="Mahila Bachat Gat",
            products=["tomato", "onion", "potato"],
            location=Location(
                state="Maharashtra",
                district="Pune",
                block="Haveli",
                village="Katraj",
                coordinates=Coordinates(lat=18.4496, lon=73.8579)
            ),
            contact=Contact(
                phone="9876543210",
                preferred_language="hi"
            )
        )
        assert profile.type == EnterpriseType.SHG
        assert profile.name == "Mahila Bachat Gat"
        assert len(profile.products) == 3
        assert profile.enterprise_id is not None
    
    def test_enterprise_types(self):
        """Test all valid enterprise types."""
        for etype in [EnterpriseType.SHG, EnterpriseType.FPO, 
                      EnterpriseType.COOPERATIVE, EnterpriseType.MSME]:
            profile = EnterpriseProfile(
                type=etype,
                name="Test Enterprise",
                products=["product1"],
                location=Location(
                    state="State",
                    district="District",
                    block="Block",
                    village="Village",
                    coordinates=Coordinates(lat=0, lon=0)
                ),
                contact=Contact(phone="9876543210", preferred_language="hi")
            )
            assert profile.type == etype
    
    def test_empty_name_rejected(self):
        """Test that empty enterprise name is rejected."""
        with pytest.raises(ValidationError):
            EnterpriseProfile(
                type=EnterpriseType.SHG,
                name="",
                products=["tomato"],
                location=Location(
                    state="State",
                    district="District",
                    block="Block",
                    village="Village",
                    coordinates=Coordinates(lat=0, lon=0)
                ),
                contact=Contact(phone="9876543210", preferred_language="hi")
            )
    
    def test_empty_products_rejected(self):
        """Test that empty products list is rejected."""
        with pytest.raises(ValidationError):
            EnterpriseProfile(
                type=EnterpriseType.SHG,
                name="Test Enterprise",
                products=[],
                location=Location(
                    state="State",
                    district="District",
                    block="Block",
                    village="Village",
                    coordinates=Coordinates(lat=0, lon=0)
                ),
                contact=Contact(phone="9876543210", preferred_language="hi")
            )
    
    def test_products_duplicate_rejection(self):
        """Test that duplicate products are rejected."""
        with pytest.raises(ValidationError):
            EnterpriseProfile(
                type=EnterpriseType.SHG,
                name="Test Enterprise",
                products=["tomato", "onion", "tomato"],
                location=Location(
                    state="State",
                    district="District",
                    block="Block",
                    village="Village",
                    coordinates=Coordinates(lat=0, lon=0)
                ),
                contact=Contact(phone="9876543210", preferred_language="hi")
            )
    
    def test_products_whitespace_cleaning(self):
        """Test that product whitespace is cleaned."""
        profile = EnterpriseProfile(
            type=EnterpriseType.SHG,
            name="Test Enterprise",
            products=["  tomato  ", " onion", "potato "],
            location=Location(
                state="State",
                district="District",
                block="Block",
                village="Village",
                coordinates=Coordinates(lat=0, lon=0)
            ),
            contact=Contact(phone="9876543210", preferred_language="hi")
        )
        assert profile.products == ["tomato", "onion", "potato"]
    
    def test_auto_generated_fields(self):
        """Test that enterprise_id and timestamps are auto-generated."""
        profile = EnterpriseProfile(
            type=EnterpriseType.SHG,
            name="Test Enterprise",
            products=["tomato"],
            location=Location(
                state="State",
                district="District",
                block="Block",
                village="Village",
                coordinates=Coordinates(lat=0, lon=0)
            ),
            contact=Contact(phone="9876543210", preferred_language="hi")
        )
        assert profile.enterprise_id is not None
        assert len(profile.enterprise_id) > 0
        assert profile.registration_date is not None
        assert profile.last_updated is not None
    
    def test_timestamp_validation(self):
        """Test that last_updated cannot be before registration_date."""
        now = datetime.utcnow()
        past = now - timedelta(days=1)
        
        with pytest.raises(ValidationError):
            EnterpriseProfile(
                type=EnterpriseType.SHG,
                name="Test Enterprise",
                products=["tomato"],
                location=Location(
                    state="State",
                    district="District",
                    block="Block",
                    village="Village",
                    coordinates=Coordinates(lat=0, lon=0)
                ),
                contact=Contact(phone="9876543210", preferred_language="hi"),
                registration_date=now,
                last_updated=past
            )


class TestDynamoDBConversion:
    """Test DynamoDB conversion methods."""
    
    def test_to_dynamodb_item(self):
        """Test conversion to DynamoDB item format."""
        profile = EnterpriseProfile(
            type=EnterpriseType.SHG,
            name="Test Enterprise",
            products=["tomato", "onion"],
            location=Location(
                state="Maharashtra",
                district="Pune",
                block="Haveli",
                village="Katraj",
                coordinates=Coordinates(lat=18.4496, lon=73.8579)
            ),
            contact=Contact(
                phone="9876543210",
                alternate_phone="9123456789",
                preferred_language="hi"
            ),
            metadata=EnterpriseMetadata(
                member_count=25,
                annual_turnover=500000.0
            )
        )
        
        item = profile.to_dynamodb_item()
        
        assert item["PK"] == f"ENTERPRISE#{profile.enterprise_id}"
        assert item["SK"] == "PROFILE"
        assert item["type"] == "SHG"
        assert item["name"] == "Test Enterprise"
        assert item["products"] == ["tomato", "onion"]
        assert item["location"]["state"] == "Maharashtra"
        assert item["contact"]["phone"] == "9876543210"
        assert item["metadata"]["member_count"] == 25
    
    def test_from_dynamodb_item(self):
        """Test conversion from DynamoDB item format."""
        item = {
            "PK": "ENTERPRISE#test-id",
            "SK": "PROFILE",
            "enterprise_id": "test-id",
            "type": "FPO",
            "name": "Farmer Producer Org",
            "products": ["wheat", "rice"],
            "location": {
                "state": "Punjab",
                "district": "Ludhiana",
                "block": "Block1",
                "village": "Village1",
                "coordinates": {
                    "lat": 30.9010,
                    "lon": 75.8573
                }
            },
            "contact": {
                "phone": "9876543210",
                "alternate_phone": None,
                "preferred_language": "hi"
            },
            "registration_date": "2024-01-01T00:00:00",
            "last_updated": "2024-01-02T00:00:00",
            "metadata": {
                "member_count": 50,
                "annual_turnover": 1000000.0,
                "primary_market": "Ludhiana Mandi"
            }
        }
        
        profile = EnterpriseProfile.from_dynamodb_item(item)
        
        assert profile.enterprise_id == "test-id"
        assert profile.type == EnterpriseType.FPO
        assert profile.name == "Farmer Producer Org"
        assert profile.products == ["wheat", "rice"]
        assert profile.location.state == "Punjab"
        assert profile.contact.phone == "9876543210"
        assert profile.metadata.member_count == 50
    
    def test_round_trip_conversion(self):
        """Test that to_dynamodb_item and from_dynamodb_item are inverses."""
        original = EnterpriseProfile(
            type=EnterpriseType.MSME,
            name="Food Processing Unit",
            products=["pickles", "jam"],
            location=Location(
                state="Karnataka",
                district="Bangalore",
                block="Block",
                village="Village",
                coordinates=Coordinates(lat=12.9716, lon=77.5946)
            ),
            contact=Contact(
                phone="9876543210",
                preferred_language="ta"
            )
        )
        
        item = original.to_dynamodb_item()
        restored = EnterpriseProfile.from_dynamodb_item(item)
        
        assert restored.type == original.type
        assert restored.name == original.name
        assert restored.products == original.products
        assert restored.location.state == original.location.state
        assert restored.contact.phone == original.contact.phone
