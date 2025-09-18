#!/usr/bin/env python3
"""
Detailed test of the authentication flow.
"""

import requests
import json

def detailed_auth_test():
    """Test authentication flow in detail."""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Step 1: Login
    print("🔐 Step 1: Testing login...")
    login_data = {
        "phone": "9876543210",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code != 200:
            print("❌ Login failed")
            return
            
        login_result = response.json()
        token = login_result.get('access_token')
        
        if not token:
            print("❌ No access token received")
            return
            
        print(f"✅ Login successful, token: {token[:30]}...")
        
        # Step 2: Test /auth/me endpoint
        print("\n👤 Step 2: Testing /auth/me endpoint...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        me_response = requests.get(f"{base_url}/auth/me", headers=headers)
        print(f"   Status: {me_response.status_code}")
        print(f"   Response: {me_response.text}")
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print("✅ User data retrieved successfully")
            
            # Check the structure
            if isinstance(user_data, dict):
                if 'data' in user_data:
                    print(f"   User info: {user_data['data']}")
                else:
                    print(f"   Raw response: {user_data}")
            else:
                print(f"   Unexpected response type: {type(user_data)}")
        else:
            print("❌ Failed to get user data")
            
        # Step 3: Test a protected crop endpoint
        print("\n🌾 Step 3: Testing crop recommendations endpoint...")
        crop_data = {
            "soil_type": "Loam",
            "soil_ph": 6.5,
            "rainfall": 1200,
            "temperature": 25.0,
            "nitrogen": 50,
            "phosphorus": 30,
            "potassium": 40,
            "field_size": 2.5
        }
        
        crop_response = requests.post(
            f"{base_url}/crops/ml/recommend",
            json=crop_data,
            headers=headers
        )
        
        print(f"   Status: {crop_response.status_code}")
        if crop_response.status_code == 200:
            print("✅ ML recommendations working")
        else:
            print(f"   Error: {crop_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    detailed_auth_test()
