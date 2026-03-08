#!/usr/bin/env python3
"""
Test script for enterprise profile API endpoints.

This script demonstrates how to use the API endpoints programmatically.
"""

import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from src.api.app import app


def print_response(title: str, response):
    """Print formatted response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2, default=str))


def main():
    """Test the API endpoints."""
    client = TestClient(app)
    
    print("Testing GramSaarthi AI Enterprise Profile API")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing health check endpoint...")
    response = client.get("/health")
    print_response("Health Check", response)
    
    # Test 2: Create enterprise
    print("\n2. Testing create enterprise endpoint...")
    enterprise_data = {
        "type": "SHG",
        "name": "Women Farmers Collective",
        "products": ["tomato", "onion", "potato"],
        "location": {
            "state": "Karnataka",
            "district": "Bangalore Rural",
            "block": "Devanahalli",
            "village": "Sadahalli",
            "coordinates": {
                "lat": 13.2443,
                "lon": 77.7074
            }
        },
        "contact": {
            "phone": "+919876543210",
            "preferred_language": "hi"
        },
        "metadata": {
            "member_count": 15,
            "annual_turnover": 500000.0,
            "primary_market": "Bangalore"
        }
    }
    
    response = client.post("/api/v1/enterprises", json=enterprise_data)
    print_response("Create Enterprise", response)
    
    if response.status_code == 201:
        enterprise_id = response.json()["enterprise_id"]
        print(f"\n✓ Enterprise created with ID: {enterprise_id}")
        
        # Test 3: Get enterprise
        print("\n3. Testing get enterprise endpoint...")
        response = client.get(f"/api/v1/enterprises/{enterprise_id}")
        print_response("Get Enterprise", response)
        
        # Test 4: Update enterprise
        print("\n4. Testing update enterprise endpoint...")
        update_data = {
            "name": "Women Farmers Collective - Updated",
            "products": ["tomato", "onion", "potato", "cabbage"]
        }
        response = client.put(f"/api/v1/enterprises/{enterprise_id}", json=update_data)
        print_response("Update Enterprise", response)
        
        # Test 5: Get updated enterprise
        print("\n5. Verifying update...")
        response = client.get(f"/api/v1/enterprises/{enterprise_id}")
        print_response("Get Updated Enterprise", response)
        
        # Test 6: Delete enterprise
        print("\n6. Testing delete enterprise endpoint...")
        response = client.delete(f"/api/v1/enterprises/{enterprise_id}")
        print_response("Delete Enterprise", response)
        
        # Test 7: Verify deletion
        print("\n7. Verifying deletion...")
        response = client.get(f"/api/v1/enterprises/{enterprise_id}")
        print_response("Get Deleted Enterprise (should be 404)", response)
    else:
        print("\n✗ Failed to create enterprise")
    
    # Test 8: Error handling - invalid data
    print("\n8. Testing error handling with invalid data...")
    invalid_data = {
        "type": "INVALID_TYPE",
        "name": "",
        "products": [],
    }
    response = client.post("/api/v1/enterprises", json=invalid_data)
    print_response("Create Enterprise with Invalid Data", response)
    
    # Test 9: Error handling - not found
    print("\n9. Testing error handling for non-existent enterprise...")
    response = client.get("/api/v1/enterprises/non-existent-id")
    print_response("Get Non-Existent Enterprise", response)
    
    print("\n" + "="*60)
    print("API Testing Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
