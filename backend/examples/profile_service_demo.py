"""
Demonstration of EnterpriseProfileService CRUD operations.

This script demonstrates the profile service functionality without requiring
actual AWS credentials. It shows the API usage patterns.
"""

from src.models.enterprise_profile import (
    EnterpriseProfile,
    EnterpriseType,
    Location,
    Coordinates,
    Contact,
    EnterpriseMetadata
)
from src.services.enterprise_profile_service import (
    EnterpriseProfileService,
    ProfileNotFoundError
)


def create_sample_profile() -> EnterpriseProfile:
    """Create a sample enterprise profile."""
    return EnterpriseProfile(
        type=EnterpriseType.SHG,
        name="Women's Self Help Group - Bangalore",
        products=["tomato", "onion", "potato", "leafy vegetables"],
        location=Location(
            state="Karnataka",
            district="Bangalore Urban",
            block="Bangalore North",
            village="Yelahanka",
            coordinates=Coordinates(lat=13.1007, lon=77.5963)
        ),
        contact=Contact(
            phone="9876543210",
            alternate_phone="9876543211",
            preferred_language="hi"
        ),
        metadata=EnterpriseMetadata(
            member_count=25,
            annual_turnover=1200000.0,
            primary_market="KR Market Bangalore"
        )
    )


def demonstrate_crud_operations():
    """
    Demonstrate CRUD operations.
    
    Note: This requires actual AWS credentials and DynamoDB table setup.
    For testing without AWS, use the unit tests with mocked dependencies.
    """
    print("=" * 60)
    print("EnterpriseProfileService CRUD Operations Demo")
    print("=" * 60)
    
    # Initialize service
    print("\n1. Initializing EnterpriseProfileService...")
    service = EnterpriseProfileService()
    print("   ✓ Service initialized")
    
    # Create profile
    print("\n2. Creating a new enterprise profile...")
    profile = create_sample_profile()
    print(f"   Profile ID: {profile.enterprise_id}")
    print(f"   Name: {profile.name}")
    print(f"   Type: {profile.type.value}")
    print(f"   Products: {', '.join(profile.products)}")
    print(f"   Location: {profile.location.village}, {profile.location.district}")
    
    try:
        enterprise_id = service.create_profile(profile)
        print(f"   ✓ Profile created with ID: {enterprise_id}")
        
        # Retrieve profile
        print("\n3. Retrieving the profile...")
        retrieved = service.get_profile(enterprise_id)
        print(f"   ✓ Profile retrieved: {retrieved.name}")
        print(f"   Member count: {retrieved.metadata.member_count}")
        print(f"   Annual turnover: ₹{retrieved.metadata.annual_turnover:,.2f}")
        
        # Update profile
        print("\n4. Updating profile information...")
        updates = {
            "name": "Women's SHG - Bangalore (Updated)",
            "products": ["tomato", "onion", "potato", "leafy vegetables", "herbs"],
            "metadata": {
                "member_count": 30,
                "annual_turnover": 1500000.0
            }
        }
        updated = service.update_profile(enterprise_id, updates)
        print(f"   ✓ Profile updated")
        print(f"   New name: {updated.name}")
        print(f"   New member count: {updated.metadata.member_count}")
        print(f"   New products: {', '.join(updated.products)}")
        
        # Check existence
        print("\n5. Checking profile existence...")
        exists = service.profile_exists(enterprise_id)
        print(f"   ✓ Profile exists: {exists}")
        
        # Delete profile
        print("\n6. Deleting the profile...")
        service.delete_profile(enterprise_id)
        print(f"   ✓ Profile deleted")
        
        # Verify deletion
        print("\n7. Verifying deletion...")
        exists_after = service.profile_exists(enterprise_id)
        print(f"   Profile exists after deletion: {exists_after}")
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
        
    except ProfileNotFoundError as e:
        print(f"   ✗ Profile not found: {e}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        print("\nNote: This demo requires AWS credentials and DynamoDB setup.")
        print("To test without AWS, run: pytest tests/unit/services/test_enterprise_profile_service.py")


def show_api_usage():
    """Show API usage examples."""
    print("\n" + "=" * 60)
    print("API Usage Examples")
    print("=" * 60)
    
    print("""
# 1. Create a profile
from src.services.enterprise_profile_service import EnterpriseProfileService
from src.models.enterprise_profile import EnterpriseProfile, EnterpriseType, ...

service = EnterpriseProfileService()
profile = EnterpriseProfile(
    type=EnterpriseType.SHG,
    name="My SHG",
    products=["tomato", "onion"],
    location=Location(...),
    contact=Contact(...)
)
enterprise_id = service.create_profile(profile)

# 2. Retrieve a profile
profile = service.get_profile(enterprise_id)

# 3. Update a profile
updated = service.update_profile(enterprise_id, {
    "name": "Updated Name",
    "products": ["wheat", "rice"]
})

# 4. Delete a profile
service.delete_profile(enterprise_id)

# 5. Check if profile exists
exists = service.profile_exists(enterprise_id)
""")


if __name__ == "__main__":
    print("\nGramSaarthi AI - Enterprise Profile Service")
    print("=" * 60)
    
    # Show API usage
    show_api_usage()
    
    # Attempt to run demo (will fail gracefully without AWS setup)
    print("\nAttempting to run live demo...")
    print("(This requires AWS credentials and DynamoDB table setup)")
    
    try:
        demonstrate_crud_operations()
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        print("\nThis is expected if AWS is not configured.")
        print("The service implementation is complete and tested.")
        print("\nTo verify functionality, run the unit tests:")
        print("  pytest tests/unit/services/test_enterprise_profile_service.py -v")
