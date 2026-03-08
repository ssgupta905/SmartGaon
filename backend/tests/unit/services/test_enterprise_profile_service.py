"""Unit tests for EnterpriseProfileService."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError

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


@pytest.fixture
def sample_profile():
    """Create a sample enterprise profile for testing."""
    return EnterpriseProfile(
        enterprise_id="test-123",
        type=EnterpriseType.SHG,
        name="Test SHG",
        products=["tomato", "onion"],
        location=Location(
            state="Karnataka",
            district="Bangalore",
            block="North",
            village="Test Village",
            coordinates=Coordinates(lat=12.9716, lon=77.5946)
        ),
        contact=Contact(
            phone="9876543210",
            alternate_phone="9876543211",
            preferred_language="hi"
        ),
        metadata=EnterpriseMetadata(
            member_count=10,
            annual_turnover=500000.0,
            primary_market="Local Mandi"
        )
    )


@pytest.fixture
def mock_table():
    """Create a mock DynamoDB table."""
    return Mock()


@pytest.fixture
def profile_service(mock_table):
    """Create a profile service with mocked table."""
    with patch('src.services.enterprise_profile_service.aws_client') as mock_aws:
        mock_aws.get_table.return_value = mock_table
        service = EnterpriseProfileService()
        service.table = mock_table
        return service


class TestCreateProfile:
    """Tests for create_profile method."""
    
    def test_create_profile_success(self, profile_service, mock_table, sample_profile):
        """Test successful profile creation."""
        mock_table.put_item.return_value = {}
        
        enterprise_id = profile_service.create_profile(sample_profile)
        
        assert enterprise_id == sample_profile.enterprise_id
        mock_table.put_item.assert_called_once()
        
        # Verify the item structure
        call_args = mock_table.put_item.call_args
        item = call_args.kwargs['Item']
        assert item['PK'] == f"ENTERPRISE#{sample_profile.enterprise_id}"
        assert item['SK'] == "PROFILE"
        assert item['type'] == "SHG"
        assert item['name'] == "Test SHG"
    
    def test_create_profile_dynamodb_error(self, profile_service, mock_table, sample_profile):
        """Test profile creation with DynamoDB error."""
        error_response = {'Error': {'Code': 'InternalServerError', 'Message': 'Internal error'}}
        mock_table.put_item.side_effect = ClientError(error_response, 'PutItem')
        
        with pytest.raises(ProfileServiceError) as exc_info:
            profile_service.create_profile(sample_profile)
        
        assert "Failed to create profile" in str(exc_info.value)
    
    def test_create_profile_generic_error(self, profile_service, mock_table, sample_profile):
        """Test profile creation with generic error."""
        mock_table.put_item.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ProfileServiceError) as exc_info:
            profile_service.create_profile(sample_profile)
        
        assert "Failed to create profile" in str(exc_info.value)


class TestGetProfile:
    """Tests for get_profile method."""
    
    def test_get_profile_success(self, profile_service, mock_table, sample_profile):
        """Test successful profile retrieval."""
        mock_table.get_item.return_value = {
            'Item': sample_profile.to_dynamodb_item()
        }
        
        retrieved = profile_service.get_profile(sample_profile.enterprise_id)
        
        assert retrieved.enterprise_id == sample_profile.enterprise_id
        assert retrieved.name == sample_profile.name
        assert retrieved.type == sample_profile.type
        assert retrieved.products == sample_profile.products
        
        mock_table.get_item.assert_called_once_with(
            Key={
                'PK': f"ENTERPRISE#{sample_profile.enterprise_id}",
                'SK': 'PROFILE'
            }
        )
    
    def test_get_profile_not_found(self, profile_service, mock_table):
        """Test profile retrieval when profile doesn't exist."""
        mock_table.get_item.return_value = {}
        
        with pytest.raises(ProfileNotFoundError) as exc_info:
            profile_service.get_profile("nonexistent-id")
        
        assert "Profile not found" in str(exc_info.value)
    
    def test_get_profile_dynamodb_error(self, profile_service, mock_table):
        """Test profile retrieval with DynamoDB error."""
        error_response = {'Error': {'Code': 'InternalServerError', 'Message': 'Internal error'}}
        mock_table.get_item.side_effect = ClientError(error_response, 'GetItem')
        
        with pytest.raises(ProfileServiceError) as exc_info:
            profile_service.get_profile("test-id")
        
        assert "Failed to retrieve profile" in str(exc_info.value)


class TestUpdateProfile:
    """Tests for update_profile method."""
    
    def test_update_profile_simple_field(self, profile_service, mock_table, sample_profile):
        """Test updating a simple field."""
        # Mock get_profile to return existing profile
        mock_table.get_item.return_value = {
            'Item': sample_profile.to_dynamodb_item()
        }
        mock_table.put_item.return_value = {}
        
        updates = {"name": "Updated SHG Name"}
        updated = profile_service.update_profile(sample_profile.enterprise_id, updates)
        
        assert updated.name == "Updated SHG Name"
        assert updated.enterprise_id == sample_profile.enterprise_id
        assert updated.type == sample_profile.type
        
        # Verify put_item was called
        mock_table.put_item.assert_called_once()
    
    def test_update_profile_products(self, profile_service, mock_table, sample_profile):
        """Test updating products list."""
        mock_table.get_item.return_value = {
            'Item': sample_profile.to_dynamodb_item()
        }
        mock_table.put_item.return_value = {}
        
        updates = {"products": ["wheat", "rice", "corn"]}
        updated = profile_service.update_profile(sample_profile.enterprise_id, updates)
        
        assert updated.products == ["wheat", "rice", "corn"]
    
    def test_update_profile_nested_contact(self, profile_service, mock_table, sample_profile):
        """Test updating nested contact information."""
        mock_table.get_item.return_value = {
            'Item': sample_profile.to_dynamodb_item()
        }
        mock_table.put_item.return_value = {}
        
        updates = {
            "contact": {
                "phone": "9999999999",
                "preferred_language": "ta"
            }
        }
        updated = profile_service.update_profile(sample_profile.enterprise_id, updates)
        
        assert updated.contact.phone == "9999999999"
        assert updated.contact.preferred_language == "ta"
    
    def test_update_profile_not_found(self, profile_service, mock_table):
        """Test updating non-existent profile."""
        mock_table.get_item.return_value = {}
        
        with pytest.raises(ProfileNotFoundError):
            profile_service.update_profile("nonexistent-id", {"name": "New Name"})
    
    def test_update_profile_updates_timestamp(self, profile_service, mock_table, sample_profile):
        """Test that update_profile updates the last_updated timestamp."""
        original_time = sample_profile.last_updated
        
        mock_table.get_item.return_value = {
            'Item': sample_profile.to_dynamodb_item()
        }
        mock_table.put_item.return_value = {}
        
        updates = {"name": "Updated Name"}
        updated = profile_service.update_profile(sample_profile.enterprise_id, updates)
        
        # The timestamp should be updated (will be different)
        assert updated.last_updated >= original_time
    
    def test_update_profile_dynamodb_error(self, profile_service, mock_table, sample_profile):
        """Test update with DynamoDB error."""
        mock_table.get_item.return_value = {
            'Item': sample_profile.to_dynamodb_item()
        }
        error_response = {'Error': {'Code': 'InternalServerError', 'Message': 'Internal error'}}
        mock_table.put_item.side_effect = ClientError(error_response, 'PutItem')
        
        with pytest.raises(ProfileServiceError) as exc_info:
            profile_service.update_profile(sample_profile.enterprise_id, {"name": "New Name"})
        
        assert "Failed to update profile" in str(exc_info.value)


class TestDeleteProfile:
    """Tests for delete_profile method."""
    
    def test_delete_profile_success(self, profile_service, mock_table, sample_profile):
        """Test successful profile deletion."""
        mock_table.get_item.return_value = {
            'Item': sample_profile.to_dynamodb_item()
        }
        mock_table.delete_item.return_value = {}
        
        profile_service.delete_profile(sample_profile.enterprise_id)
        
        mock_table.delete_item.assert_called_once_with(
            Key={
                'PK': f"ENTERPRISE#{sample_profile.enterprise_id}",
                'SK': 'PROFILE'
            }
        )
    
    def test_delete_profile_not_found(self, profile_service, mock_table):
        """Test deleting non-existent profile."""
        mock_table.get_item.return_value = {}
        
        with pytest.raises(ProfileNotFoundError):
            profile_service.delete_profile("nonexistent-id")
        
        # delete_item should not be called
        mock_table.delete_item.assert_not_called()
    
    def test_delete_profile_dynamodb_error(self, profile_service, mock_table, sample_profile):
        """Test deletion with DynamoDB error."""
        mock_table.get_item.return_value = {
            'Item': sample_profile.to_dynamodb_item()
        }
        error_response = {'Error': {'Code': 'InternalServerError', 'Message': 'Internal error'}}
        mock_table.delete_item.side_effect = ClientError(error_response, 'DeleteItem')
        
        with pytest.raises(ProfileServiceError) as exc_info:
            profile_service.delete_profile(sample_profile.enterprise_id)
        
        assert "Failed to delete profile" in str(exc_info.value)


class TestProfileExists:
    """Tests for profile_exists method."""
    
    def test_profile_exists_true(self, profile_service, mock_table, sample_profile):
        """Test profile_exists returns True for existing profile."""
        mock_table.get_item.return_value = {
            'Item': sample_profile.to_dynamodb_item()
        }
        
        assert profile_service.profile_exists(sample_profile.enterprise_id) is True
    
    def test_profile_exists_false(self, profile_service, mock_table):
        """Test profile_exists returns False for non-existent profile."""
        mock_table.get_item.return_value = {}
        
        assert profile_service.profile_exists("nonexistent-id") is False
    
    def test_profile_exists_service_error(self, profile_service, mock_table):
        """Test profile_exists returns False on service error."""
        error_response = {'Error': {'Code': 'InternalServerError', 'Message': 'Internal error'}}
        mock_table.get_item.side_effect = ClientError(error_response, 'GetItem')
        
        assert profile_service.profile_exists("test-id") is False
