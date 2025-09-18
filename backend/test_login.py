#!/usr/bin/env python3
"""
Test login functionality for the AuraFarming application.
"""

import requests
import json

def test_login():
    """Test login with existing user credentials."""
    
    # Login credentials
    login_data = {
        "phone": "9876543210",
        "password": "password123"
    }
    
    try:
        # Test login
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            print(f"🔐 Access token: {data.get('access_token', 'N/A')[:30]}...")
            print(f"📝 Token type: {data.get('token_type', 'N/A')}")
            print(f"⏰ Expires in: {data.get('expires_in', 'N/A')} seconds")
            
            # Test accessing protected endpoint
            token = data.get('access_token')
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get(
                    "http://localhost:8000/api/v1/auth/me",
                    headers=headers
                )
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print(f"👤 User name: {user_data.get('name', 'N/A')}")
                    print(f"📱 Phone: {user_data.get('phone', 'N/A')}")
                    print(f"📍 District: {user_data.get('district', 'N/A')}")
                else:
                    print(f"❌ Failed to get user data: {me_response.status_code}")
                    print(f"📝 Response: {me_response.text}")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
