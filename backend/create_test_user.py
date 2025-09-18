#!/usr/bin/env python3
"""
Create a test user for the AuraFarming application.
"""

import requests
import json

def create_test_user():
    """Create a test user for login testing."""
    
    # Test user data
    user_data = {
        "name": "Test User",
        "phone": "9876543210",
        "password": "password123",
        "district": "Ranchi",
        "language": "en"
    }
    
    try:
        # Register the test user
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Test user created successfully!")
            print(f"📱 Phone: {user_data['phone']}")
            print(f"🔑 Password: {user_data['password']}")
            print(f"🎯 You can now login with these credentials")
            
            data = response.json()
            if 'access_token' in data:
                print(f"🔐 Access token received: {data['access_token'][:20]}...")
                
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_test_user()
