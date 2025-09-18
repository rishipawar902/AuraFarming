#!/usr/bin/env python3
"""
Test the exact frontend login flow.
"""

import requests
import json

def test_frontend_flow():
    """Test the exact same flow as the frontend."""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Step 1: Login (same as frontend)
    print("🔐 Step 1: Login flow...")
    login_data = {
        "phone": "9876543210",
        "password": "password123"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    print(f"Login response: {response.json()}")
    
    if response.status_code == 200:
        login_result = response.json()
        token = login_result.get('access_token')
        
        # Step 2: Get user data (same as frontend AuthService.getCurrentUser)
        print("\n👤 Step 2: Get user data...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # This simulates ApiService.getCurrentUser() which returns response.data
        me_response = requests.get(f"{base_url}/auth/me", headers=headers)
        api_service_result = me_response.json()  # This is what ApiService returns
        
        print(f"ApiService.getCurrentUser() returns: {json.dumps(api_service_result, indent=2)}")
        
        # This simulates AuthService.getCurrentUser() logic
        # The comment says: "So the user data is in response.data"
        if api_service_result and api_service_result.get('data'):
            user_data = api_service_result['data']
            print(f"\n✅ User data extracted: {json.dumps(user_data, indent=2)}")
            
            # Step 3: Test if this would work in the frontend
            print(f"\n📝 Test frontend expectations:")
            print(f"   Name: {user_data.get('name', 'N/A')}")
            print(f"   Phone: {user_data.get('phone', 'N/A')}")
            print(f"   District: {user_data.get('district', 'N/A')}")
            if 'farm' in user_data:
                farm = user_data['farm']
                print(f"   Farm: {farm.get('name', 'N/A')}")
                print(f"   Farm District: {farm.get('location', {}).get('district', 'N/A')}")
        else:
            print("❌ No user data found in response.data")
            
    else:
        print(f"❌ Login failed: {response.status_code}")

if __name__ == "__main__":
    test_frontend_flow()
