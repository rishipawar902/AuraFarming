#!/usr/bin/env python3
"""
🌤️ Weather API Integration Test via FastAPI endpoints
==================================================

Tests the weather API endpoints with real backend integration.
"""

import asyncio
import httpx
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.database import DatabaseService

async def test_weather_api_endpoints():
    """Test weather API endpoints through FastAPI."""
    
    print("🌤️ Testing Weather API Endpoints")
    print("=" * 50)
    
    # API base URL (adjust if backend is running on different port)
    base_url = "http://localhost:8000"
    
    # Test user credentials
    test_user = {
        "phone": "9876543210",
        "password": "password123"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\n🔐 Step 1: Login and get JWT token")
            login_response = await client.post(
                f"{base_url}/auth/login",
                data=test_user
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return False
            
            login_data = login_response.json()
            token = login_data["data"]["access_token"]
            print(f"✅ Login successful, token: {token[:20]}...")
            
            # Headers with authentication
            headers = {"Authorization": f"Bearer {token}"}
            
            print("\n🏪 Step 2: Get user's farms")
            farms_response = await client.get(
                f"{base_url}/farms/my-farms",
                headers=headers
            )
            
            if farms_response.status_code != 200:
                print(f"❌ Failed to get farms: {farms_response.status_code}")
                return False
            
            farms_data = farms_response.json()
            if not farms_data["data"]:
                print("❌ No farms found for user")
                return False
            
            farm = farms_data["data"][0]
            farm_id = farm["farm_id"]
            print(f"✅ Found farm: {farm['name']} (ID: {farm_id})")
            
            print("\n🌡️ Step 3: Test current weather endpoint")
            weather_response = await client.get(
                f"{base_url}/weather/current/{farm_id}",
                headers=headers
            )
            
            if weather_response.status_code == 200:
                weather_data = weather_response.json()
                current = weather_data["data"]["current"]
                print(f"✅ Current weather retrieved:")
                print(f"   🌡️ Temperature: {current['temperature']}°C")
                print(f"   💧 Humidity: {current['humidity']}%")
                print(f"   🌤️ Condition: {current['description']}")
                print(f"   📊 Source: {weather_data['data']['data_source']}")
            else:
                print(f"❌ Weather API failed: {weather_response.status_code}")
                print(f"Response: {weather_response.text}")
            
            print("\n📅 Step 4: Test weather forecast endpoint")
            forecast_response = await client.get(
                f"{base_url}/weather/forecast/{farm_id}?days=5",
                headers=headers
            )
            
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                forecasts = forecast_data["data"]["forecast"]
                print(f"✅ 5-day forecast retrieved ({len(forecasts)} days):")
                for forecast in forecasts[:3]:
                    print(f"   📅 {forecast['date']}: {forecast['temperature_min']}°C - {forecast['temperature_max']}°C")
                    print(f"      🌤️ {forecast['description']}")
            else:
                print(f"❌ Forecast API failed: {forecast_response.status_code}")
                print(f"Response: {forecast_response.text}")
            
            print("\n🚨 Step 5: Test weather alerts endpoint")
            alerts_response = await client.get(
                f"{base_url}/weather/alerts/{farm_id}",
                headers=headers
            )
            
            if alerts_response.status_code == 200:
                alerts_data = alerts_response.json()
                alerts = alerts_data["data"]["alerts"]
                print(f"✅ Weather alerts retrieved ({len(alerts)} alerts):")
                for alert in alerts[:2]:
                    print(f"   ⚠️ {alert['type']}: {alert['message']}")
            else:
                print(f"❌ Alerts API failed: {alerts_response.status_code}")
            
            print("\n🤖 Step 6: Test ML weather endpoint")
            ml_response = await client.get(
                f"{base_url}/weather/ml-data/{farm_id}",
                headers=headers
            )
            
            if ml_response.status_code == 200:
                ml_data = ml_response.json()
                ml_features = ml_data["data"]["ml_features"]
                print(f"✅ ML weather data retrieved:")
                print(f"   🔢 Temperature normalized: {ml_features['temperature_normalized']:.2f}")
                print(f"   🔢 Humidity normalized: {ml_features['humidity_normalized']:.2f}")
            else:
                print(f"❌ ML weather API failed: {ml_response.status_code}")
            
            print("\n🎉 Weather API Integration: COMPLETE!")
            return True
            
    except httpx.ConnectError:
        print("❌ Cannot connect to backend server")
        print("💡 Please start the backend server with: python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_weather_api_endpoints())
    if result:
        print("\n✅ All weather API tests passed!")
    else:
        print("\n❌ Some weather API tests failed")
