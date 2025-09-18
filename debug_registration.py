#!/usr/bin/env python3
"""
Debug test to verify registration endpoint is working correctly.
This will test the exact registration flow with detailed logging.
"""

import requests
import json
import time

# Backend URL
BASE_URL = "http://localhost:8000"

def test_registration_debug():
    """Test registration with different phone numbers to debug the issue"""
    
    # Generate a unique phone number for this test
    timestamp = str(int(time.time()))[-4:]  # Last 4 digits of timestamp
    phone_number = f"987654{timestamp}"
    
    registration_data = {
        "name": "Debug Test User",
        "phone": phone_number,
        "password": "debugtest123",
        "language": "en"
    }
    
    print("🔍 Debug Test: Registration Endpoint")
    print("=" * 50)
    print(f"📤 Testing registration with phone: {phone_number}")
    print(f"📤 Full data: {json.dumps(registration_data, indent=2)}")
    
    try:
        print("🌐 Making request to:", f"{BASE_URL}/api/v1/auth/register")
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📥 Response Body: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"📥 Response Body (raw): {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            
            # Test login with the new user
            print("\n🔄 Testing login with new user...")
            login_data = {
                "phone": phone_number,
                "password": "debugtest123"
            }
            
            login_response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📥 Login Status: {login_response.status_code}")
            if login_response.status_code == 200:
                print("✅ Login also successful!")
            else:
                print(f"❌ Login failed: {login_response.text}")
                
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print("💡 Check if backend is running on http://localhost:8000")

def check_backend_health():
    """Check if backend is responding"""
    print("🏥 Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Backend health check: {response.status_code}")
        print(f"📥 Health response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

if __name__ == "__main__":
    print("🐛 Debug Test: Frontend Registration Issue")
    print("=" * 60)
    
    # First check if backend is running
    if check_backend_health():
        print("\n")
        test_registration_debug()
    else:
        print("❌ Cannot proceed - backend is not responding")