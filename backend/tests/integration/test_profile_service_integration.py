"""Integration tests for EnterpriseProfileService with DynamoDB."""

import pytest
import boto3
from datetime import datetime

# Try to import moto, skip tests if not available
try:
    from moto import mock_aws
    MOTO_AVAILABLE = True
except ImportError:
    MOTO_AVAILABLE = False
    mock_aws = None

pytestmark = pytest.mark.skipif(
    not MOTO_AVAILABLE,
    reason="moto not installed - integration tests require moto for DynamoDB mocking"
)

from src.services.enterprise_profile_service import (
    EnterpriseProfileService,
    ProfileNotFoundError,
    ProfileServiceError
)
from src.models.enterprise_profile import (
    EnterpriseProfile,
    EnterpriseType,
    Location,
    Coordinates,
    Contact,
    EnterpriseMetadata
)
from src.config import settings


@pytest.fixture
def dynamodb_table():
    """Create a mock DynamoDB table for testing."""
    with mock_aws():
        # Create DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
        
        # Create table
        table_name = f"{settings.dynamodb_table_prefix}_EnterpriseProfiles"
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        yield table


@pytest.fixture
def profile_service(dynamodb_table):
    """Create a profile service with mocked DynamoDB."""
    service = EnterpriseProfileService()
    service.table = dynamodb_table
    return service


@pytest.fixture
def sample_profile():
    """Create a sample enterprise profile."""
    return EnterpriseProfile(
        type=EnterpriseType.SHG,
        name="Integration Test SHG",
        products=["tomato", "onion", "potato"],
        location=Location(
            state="Karnataka",
            district="Bangalore Urban",
            block="Bangalore North",
            village="Test Village",
            coordinates=Coordinates(lat=12.9716, lon=77.5946)
        ),
        contact=Contact(
            phone="9876543210",
            alternate_phone="9876543211",
            preferred_language="hi"
        ),
        metadata=EnterpriseMetadata(
            member_count=15,
            annual_turnover=750000.0,
            primary_market="Bangalore Mandi"
        )
    )


class TestProfileServiceIntegration:
    """Integration tests for profile service."""
    
    def test_create_and_retrieve_profile(self, profile_service, sample_profile):
        """Test creating and retrieving a profile."""
        # Create profile
        enterprise_id = profile_service.create_profile(sample_profile)
        assert enterprise_id == sample_profile.enterprise_id
        
        # Retrieve profile
        retrieved = profile_service.get_profile(enterprise_id)
        
        # Verify all fields
        assert retrieved.enterprise_id == sample_profile.enterprise_id
        assert retrieved.type == sample_profile.type
        assert retrieved.name == sample_profile.name
        assert retrieved.products == sample_profile.products
        assert retrieved.location.state == sample_profile.location.state
        assert retrieved.location.district == sample_profile.location.district
        assert retrieved.contact.phone == sample_profile.contact.phone
        assert retrieved.contact.preferred_language == sample_profile.contact.preferred_language
        assert retrieved.metadata.member_count == sample_profile.metadata.member_count
    
    def test_update_profile_fields(self, profile_service, sample_profile):
        """Test updating profile fields."""
        # Create profile
        enterprise_id = profile_service.create_profile(sample_profile)
        
        # Update profile
        updates = {
            "name": "Updated SHG Name",
            "products": ["wheat", "rice"]
        }
        updated = profile_service.update_profile(enterprise_id, updates)
        
        # Verify updates
        assert updated.name == "Updated SHG Name"
        assert updated.products == ["wheat", "rice"]
        assert updated.type == sample_profile.type  # Unchanged
        
        # Retrieve and verify persistence
        retrieved = profile_service.get_profile(enterprise_id)
        assert retrieved.name == "Updated SHG Name"
        assert retrieved.products == ["wheat", "rice"]
    
    def test_update_nested_fields(self, profile_service, sample_profile):
        """Test updating nested fields."""
        # Create profile
        enterprise_id = profile_service.create_profile(sample_profile)
        
        # Update contact information
        updates = {
            "contact": {
                "phone": "9999999999",
                "preferred_language": "ta"
            }
        }
        updated = profile_service.update_profile(enterprise_id, updates)
        
        # Verify updates
        assert updated.contact.phone == "9999999999"
        assert updated.contact.preferred_language == "ta"
        
        # Retrieve and verify
        retrieved = profile_service.get_profile(enterprise_id)
        assert retrieved.contact.phone == "9999999999"
        assert retrieved.contact.preferred_language == "ta"
    
    def test_delete_profile(self, profile_service, sample_profile):
        """Test deleting a profile."""
        # Create profile
        enterprise_id = profile_service.create_profile(sample_profile)
        
        # Verify it exists
        assert profile_service.profile_exists(enterprise_id) is True
        
        # Delete profile
        profile_service.delete_profile(enterprise_id)
        
        # Verify it no longer exists
        assert profile_service.profile_exists(enterprise_id) is False
        
        # Verify retrieval raises error
        with pytest.raises(ProfileNotFoundError):
            profile_service.get_profile(enterprise_id)
    
    def test_profile_exists_check(self, profile_service, sample_profile):
        """Test profile_exists method."""
        # Check non-existent profile
        assert profile_service.profile_exists("nonexistent-id") is False
        
        # Create profile
        enterprise_id = profile_service.create_profile(sample_profile)
        
        # Check existing profile
        assert profile_service.profile_exists(enterprise_id) is True
    
    def test_retrieve_nonexistent_profile(self, profile_service):
        """Test retrieving a profile that doesn't exist."""
        with pytest.raises(ProfileNotFoundError) as exc_info:
            profile_service.get_profile("nonexistent-id")
        
        assert "Profile not found" in str(exc_info.value)
    
    def test_update_nonexistent_profile(self, profile_service):
        """Test updating a profile that doesn't exist."""
        with pytest.raises(ProfileNotFoundError):
            profile_service.update_profile("nonexistent-id", {"name": "New Name"})
    
    def test_delete_nonexistent_profile(self, profile_service):
        """Test deleting a profile that doesn't exist."""
        with pytest.raises(ProfileNotFoundError):
            profile_service.delete_profile("nonexistent-id")
    
    def test_multiple_profiles(self, profile_service):
        """Test creating and managing multiple profiles."""
        # Create multiple profiles
        profiles = []
        for i in range(3):
            profile = EnterpriseProfile(
                type=EnterpriseType.SHG,
                name=f"SHG {i}",
                products=[f"product{i}"],
                location=Location(
                    state="State",
                    district="District",
                    block="Block",
                    village=f"Village {i}",
                    coordinates=Coordinates(lat=12.0 + i, lon=77.0 + i)
                ),
                contact=Contact(
                    phone=f"987654321{i}",
                    preferred_language="hi"
                )
            )
            enterprise_id = profile_service.create_profile(profile)
            profiles.append((enterprise_id, profile))
        
        # Verify all profiles exist and are independent
        for enterprise_id, original in profiles:
            retrieved = profile_service.get_profile(enterprise_id)
            assert retrieved.enterprise_id == enterprise_id
            assert retrieved.name == original.name
            assert retrieved.location.village == original.location.village
    
    def test_profile_latency_optimization(self, profile_service, sample_profile):
        """Test that profile retrieval meets <500ms latency requirement."""
        import time
        
        # Create profile
        enterprise_id = profile_service.create_profile(sample_profile)
        
        # Measure retrieval time
        start_time = time.time()
        profile_service.get_profile(enterprise_id)
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        
        # Verify latency is under 500ms (should be much faster with moto)
        assert latency_ms < 500, f"Profile retrieval took {latency_ms}ms, exceeds 500ms requirement"
