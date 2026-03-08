"""Test script for voice interaction API endpoints.

This script demonstrates the voice API endpoints with sample requests.
"""

import base64
import requests
import json
from datetime import datetime


# API base URL
BASE_URL = "http://localhost:8000"


def test_start_session():
    """Test POST /api/v1/voice/session/start"""
    print("\n=== Testing Voice Session Start ===")
    
    url = f"{BASE_URL}/api/v1/voice/session/start"
    payload = {
        "user_id": "test_user_123",
        "language_code": "hi"
    }
    
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()["session_id"]
    return None


def test_transcribe(session_id: str):
    """Test POST /api/v1/voice/transcribe"""
    print("\n=== Testing Audio Transcription ===")
    
    # Create mock audio data (just some bytes for testing)
    mock_audio = b"mock audio data for testing transcription"
    audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
    
    url = f"{BASE_URL}/api/v1/voice/transcribe"
    payload = {
        "session_id": session_id,
        "audio_data": audio_base64,
        "language_code": "hi"
    }
    
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json() if response.status_code == 200 else None


def test_synthesize():
    """Test POST /api/v1/voice/synthesize"""
    print("\n=== Testing Speech Synthesis ===")
    
    url = f"{BASE_URL}/api/v1/voice/synthesize"
    payload = {
        "text": "नमस्ते, मैं आपकी कैसे मदद कर सकता हूं",
        "language_code": "hi",
        "voice_profile": "female_default"
    }
    
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Duration: {result['duration']} seconds")
        print(f"Language: {result['language']}")
        print(f"Audio data length: {len(result['audio_data'])} characters (base64)")
        return result
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return None


def test_voice_query(session_id: str):
    """Test POST /api/v1/voice/query"""
    print("\n=== Testing End-to-End Voice Query ===")
    
    # Create mock audio data with a specific pattern for market query
    # The hash will map to a market-related transcription
    mock_audio = b"\x00\x01\x02\x03" * 100  # Hash starts with '0'
    audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
    
    url = f"{BASE_URL}/api/v1/voice/query"
    payload = {
        "session_id": session_id,
        "audio_data": audio_base64
    }
    
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response Text: {result['response_text']}")
        print(f"Agent Used: {result['agent_used']}")
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Response Audio Length: {len(result['response_audio'])} characters (base64)")
        return result
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return None


def test_terminate_session(session_id: str):
    """Test DELETE /api/v1/voice/session/{session_id}"""
    print("\n=== Testing Session Termination ===")
    
    url = f"{BASE_URL}/api/v1/voice/session/{session_id}"
    
    response = requests.delete(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json() if response.status_code == 200 else None


def test_invalid_session():
    """Test with invalid session ID"""
    print("\n=== Testing Invalid Session Handling ===")
    
    url = f"{BASE_URL}/api/v1/voice/transcribe"
    payload = {
        "session_id": "invalid_session_id",
        "audio_data": base64.b64encode(b"test").decode('utf-8'),
        "language_code": "hi"
    }
    
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_unsupported_language():
    """Test with unsupported language"""
    print("\n=== Testing Unsupported Language Handling ===")
    
    url = f"{BASE_URL}/api/v1/voice/session/start"
    payload = {
        "user_id": "test_user",
        "language_code": "fr"  # French - not supported
    }
    
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def main():
    """Run all voice endpoint tests."""
    print("=" * 60)
    print("Voice Interaction API Endpoint Tests")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    
    try:
        # Test 1: Start a session
        session_id = test_start_session()
        
        if not session_id:
            print("\n❌ Failed to create session. Stopping tests.")
            return
        
        # Test 2: Transcribe audio
        test_transcribe(session_id)
        
        # Test 3: Synthesize speech
        test_synthesize()
        
        # Test 4: End-to-end voice query
        test_voice_query(session_id)
        
        # Test 5: Terminate session
        test_terminate_session(session_id)
        
        # Test 6: Error handling - invalid session
        test_invalid_session()
        
        # Test 7: Error handling - unsupported language
        test_unsupported_language()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server.")
        print(f"Make sure the server is running at {BASE_URL}")
        print("Run: python -m src.api.app")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
