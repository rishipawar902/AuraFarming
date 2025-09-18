import requests
import json

def test_market_api_simple():
    """Simple test of market API without authentication."""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Skip health check and go straight to authentication
    print("🔐 Getting authentication token...")
    try:
        login_response = requests.get(f"{base_url}/auth/login", timeout=5)
        print(f"Login endpoint check: {login_response.status_code}")
        
        if login_response.status_code == 405:  # Method not allowed - good, endpoint exists
            print("✅ Backend server is running (login endpoint found)")
        elif login_response.status_code in [200, 422]:  # OK or validation error
            print("✅ Backend server is running")
        else:
            print(f"⚠️ Unexpected status: {login_response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Cannot connect to backend server: {e}")
        return
    
    # Get token for authentication
    print("\n🔐 Getting authentication token...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", json={
            "phone": "9876543210",
            "password": "password123"
        }, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        token = login_response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
    except requests.RequestException as e:
        print(f"❌ Login request failed: {e}")
        return
    
    # Test market prices endpoint
    print("\n📊 Testing market prices API...")
    try:
        response = requests.get(f"{base_url}/market/prices/Ranchi", headers=headers, timeout=15)
        print(f"Market API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Market prices API working!")
            print(f"   Data source: {data.get('data', {}).get('data_source', 'Unknown')}")
            
            prices = data.get('data', {}).get('prices', [])
            print(f"   Found {len(prices)} price entries")
            
            if prices:
                first_price = prices[0]
                print(f"   Example: {first_price.get('crop')} - ₹{first_price.get('modal_price', 'N/A')}/qtl")
                print(f"   Source: {first_price.get('source', 'Unknown')}")
        else:
            print(f"❌ Market API failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Market API request failed: {e}")

if __name__ == "__main__":
    test_market_api_simple()
