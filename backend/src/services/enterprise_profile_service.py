"""Enterprise profile service for CRUD operations with DynamoDB."""

from datetime import datetime
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError

from src.models.enterprise_profile import EnterpriseProfile
from src.aws_client import aws_client


class ProfileNotFoundError(Exception):
    """Raised when a profile is not found."""
    pass


class ProfileServiceError(Exception):
    """Raised when a profile service operation fails."""
    pass


class ProfileVersionConflictError(Exception):
    """Raised when a profile update conflicts with current version."""
    pass


class EnterpriseProfileService:
    """Service for managing enterprise profiles in DynamoDB.
    
    Optimized for <500ms latency on profile retrieval through:
    - Direct key-based access (no scans)
    - Consistent reads for latest data
    - Connection pooling via aws_client
    - Adaptive retry configuration
    """
    
    def __init__(self):
        """Initialize the profile service."""
        self.table = aws_client.get_table("EnterpriseProfiles")
    
    def create_profile(self, profile: EnterpriseProfile) -> str:
        """
        Create a new enterprise profile.
        
        Args:
            profile: EnterpriseProfile instance to create
            
        Returns:
            enterprise_id of the created profile
            
        Raises:
            ProfileServiceError: If creation fails
        """
        try:
            item = profile.to_dynamodb_item()
            self.table.put_item(Item=item)
            return profile.enterprise_id
        except ClientError as e:
            raise ProfileServiceError(
                f"Failed to create profile: {e.response['Error']['Message']}"
            ) from e
        except Exception as e:
            raise ProfileServiceError(f"Failed to create profile: {str(e)}") from e
    
    def get_profile(self, enterprise_id: str) -> EnterpriseProfile:
        """
        Retrieve an enterprise profile by ID.
        
        Optimized for <500ms latency using:
        - ConsistentRead=True for immediate consistency
        - Direct key-based access (no query/scan)
        
        Args:
            enterprise_id: Unique enterprise identifier
            
        Returns:
            EnterpriseProfile instance
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
            ProfileServiceError: If retrieval fails
        """
        try:
            response = self.table.get_item(
                Key={
                    "PK": f"ENTERPRISE#{enterprise_id}",
                    "SK": "PROFILE"
                },
                ConsistentRead=True  # Ensure latest data, typically <10ms
            )
            
            if "Item" not in response:
                raise ProfileNotFoundError(
                    f"Profile not found for enterprise_id: {enterprise_id}"
                )
            
            return EnterpriseProfile.from_dynamodb_item(response["Item"])
        except ProfileNotFoundError:
            raise
        except ClientError as e:
            raise ProfileServiceError(
                f"Failed to retrieve profile: {e.response['Error']['Message']}"
            ) from e
        except Exception as e:
            raise ProfileServiceError(f"Failed to retrieve profile: {str(e)}") from e
    
    def update_profile(
        self,
        enterprise_id: str,
        updates: Dict[str, Any]
    ) -> EnterpriseProfile:
        """
        Update an enterprise profile with optimistic locking.
        
        Uses version-based optimistic locking to prevent concurrent update conflicts.
        The version is automatically incremented on successful update.
        
        Args:
            enterprise_id: Unique enterprise identifier
            updates: Dictionary of fields to update
            
        Returns:
            Updated EnterpriseProfile instance
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
            ProfileVersionConflictError: If version conflict detected
            ProfileServiceError: If update fails
        """
        # First, get the existing profile to ensure it exists
        existing_profile = self.get_profile(enterprise_id)
        current_version = existing_profile.version
        
        # Update the profile with new values
        profile_dict = existing_profile.model_dump()
        
        # Handle nested updates
        for key, value in updates.items():
            if key in ["location", "contact", "metadata"]:
                # For nested objects, merge with existing values
                if key in profile_dict and profile_dict[key]:
                    if isinstance(value, dict):
                        profile_dict[key].update(value)
                    else:
                        profile_dict[key] = value
                else:
                    profile_dict[key] = value
            elif key != "version":  # Don't allow manual version updates
                profile_dict[key] = value
        
        # Update the last_updated timestamp and increment version
        profile_dict["last_updated"] = datetime.utcnow()
        profile_dict["version"] = current_version + 1
        
        # Create updated profile and validate
        updated_profile = EnterpriseProfile(**profile_dict)
        
        # Save to DynamoDB with conditional write (optimistic locking)
        try:
            item = updated_profile.to_dynamodb_item()
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_exists(PK) AND #v = :current_version",
                ExpressionAttributeNames={"#v": "version"},
                ExpressionAttributeValues={":current_version": current_version}
            )
            return updated_profile
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ProfileVersionConflictError(
                    f"Profile was modified by another process. Please retry with latest version."
                ) from e
            raise ProfileServiceError(
                f"Failed to update profile: {e.response['Error']['Message']}"
            ) from e
        except Exception as e:
            raise ProfileServiceError(f"Failed to update profile: {str(e)}") from e
    
    def delete_profile(self, enterprise_id: str) -> None:
        """
        Delete an enterprise profile.
        
        Args:
            enterprise_id: Unique enterprise identifier
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
            ProfileServiceError: If deletion fails
        """
        # First verify the profile exists
        self.get_profile(enterprise_id)
        
        try:
            self.table.delete_item(
                Key={
                    "PK": f"ENTERPRISE#{enterprise_id}",
                    "SK": "PROFILE"
                }
            )
        except ClientError as e:
            raise ProfileServiceError(
                f"Failed to delete profile: {e.response['Error']['Message']}"
            ) from e
        except Exception as e:
            raise ProfileServiceError(f"Failed to delete profile: {str(e)}") from e
    
    def profile_exists(self, enterprise_id: str) -> bool:
        """
        Check if a profile exists.
        
        Args:
            enterprise_id: Unique enterprise identifier
            
        Returns:
            True if profile exists, False otherwise
        """
        try:
            self.get_profile(enterprise_id)
            return True
        except ProfileNotFoundError:
            return False
        except ProfileServiceError:
            # If there's a service error, we can't determine existence
            return False
    
    def get_profile_fields(
        self,
        enterprise_id: str,
        fields: list[str]
    ) -> Dict[str, Any]:
        """
        Retrieve specific fields from a profile for optimized queries.
        
        This method uses DynamoDB projection to retrieve only requested fields,
        reducing data transfer and improving latency for partial profile reads.
        
        Args:
            enterprise_id: Unique enterprise identifier
            fields: List of field names to retrieve
            
        Returns:
            Dictionary with requested fields
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
            ProfileServiceError: If retrieval fails
        """
        try:
            # Build projection expression
            projection_expr = ", ".join(f"#{f}" for f in fields)
            expr_attr_names = {f"#{f}": f for f in fields}
            
            response = self.table.get_item(
                Key={
                    "PK": f"ENTERPRISE#{enterprise_id}",
                    "SK": "PROFILE"
                },
                ProjectionExpression=projection_expr,
                ExpressionAttributeNames=expr_attr_names,
                ConsistentRead=True
            )
            
            if "Item" not in response:
                raise ProfileNotFoundError(
                    f"Profile not found for enterprise_id: {enterprise_id}"
                )
            
            return response["Item"]
        except ProfileNotFoundError:
            raise
        except ClientError as e:
            raise ProfileServiceError(
                f"Failed to retrieve profile fields: {e.response['Error']['Message']}"
            ) from e
        except Exception as e:
            raise ProfileServiceError(
                f"Failed to retrieve profile fields: {str(e)}"
            ) from e
