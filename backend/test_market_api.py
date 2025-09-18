#!/usr/bin/env python3
"""
Test the market API endpoints.
"""

import requests
import json

def test_market_api():
    """Test all market API endpoints."""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Get token first
    print("🔐 Getting authentication token...")
    login_response = requests.post(f"{base_url}/auth/login", json={
        "phone": "9876543210",
        "password": "password123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication successful")
    
    # Test 1: Get market prices for Ranchi
    print("\n📊 Testing market prices API...")
    try:
        response = requests.get(f"{base_url}/market/prices/Ranchi", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Market prices API working")
            if data.get('data', {}).get('prices'):
                print(f"   Found {len(data['data']['prices'])} crops")
                # Show first crop as example
                first_crop = data['data']['prices'][0]
                print(f"   Example: {first_crop['crop']} - ₹{first_crop['modal_price']}/qtl")
            else:
                print("   No price data returned")
        else:
            print(f"❌ Market prices API failed: {response.text}")
    except Exception as e:
        print(f"❌ Market prices API error: {e}")
    
    # Test 2: Get prices for specific crop
    print("\n🌾 Testing crop-specific prices API...")
    try:
        response = requests.get(f"{base_url}/market/prices/Ranchi?crop=Rice", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Crop-specific prices API working")
            if data.get('data', {}).get('prices'):
                rice_price = data['data']['prices'][0]
                print(f"   Rice price: ₹{rice_price['modal_price']}/qtl")
                print(f"   Trend: {rice_price['trend']}")
        else:
            print(f"❌ Crop-specific prices API failed: {response.text}")
    except Exception as e:
        print(f"❌ Crop-specific prices API error: {e}")
    
    # Test 3: Get price trends
    print("\n📈 Testing price trends API...")
    try:
        response = requests.get(f"{base_url}/market/trends/Rice?days=30", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Price trends API working")
            if data.get('data', {}).get('trend_analysis'):
                analysis = data['data']['trend_analysis']
                print(f"   Current price: ₹{analysis['current_price']}")
                print(f"   Trend: {analysis['direction']} ({analysis['percentage_change']}%)")
                print(f"   30-day range: ₹{analysis['lowest_price']} - ₹{analysis['highest_price']}")
        else:
            print(f"❌ Price trends API failed: {response.text}")
    except Exception as e:
        print(f"❌ Price trends API error: {e}")
    
    # Test 4: Get price forecast
    print("\n🔮 Testing price forecast API...")
    try:
        response = requests.get(f"{base_url}/market/forecast/Wheat", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Price forecast API working")
            print(f"   Forecast data available: {bool(data.get('data'))}")
        else:
            print(f"❌ Price forecast API failed: {response.text}")
    except Exception as e:
        print(f"❌ Price forecast API error: {e}")
    
    # Test 5: Get best markets
    print("\n🎯 Testing best markets API...")
    try:
        response = requests.get(f"{base_url}/market/best-markets/Rice?origin_district=Ranchi", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Best markets API working")
            print(f"   Market recommendations available: {bool(data.get('data'))}")
        else:
            print(f"❌ Best markets API failed: {response.text}")
    except Exception as e:
        print(f"❌ Best markets API error: {e}")
    
    print("\n🎉 Market API testing completed!")

if __name__ == "__main__":
    test_market_api()
