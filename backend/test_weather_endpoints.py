#!/usr/bin/env python3
"""
🌤️ Weather API Endpoint Test
=============================

Tests the weather API endpoints to check for display issues.
"""

import requests
import json
import sys

def print_banner():
    print("🌤️ AuraFarming: Weather API Endpoint Test")
    print("=" * 55)
    print("🎯 Testing weather endpoints for display issues")
    print("🔍 Checking API responses and data format")
    print("=" * 55)

def test_weather_endpoints():
    """Test weather API endpoints."""
    
    print_banner()
    
    base_url = "http://localhost:8000"
    issues_found = []
    
    print("\n🏥 Step 1: Server Health Check")
    print("-" * 35)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server issue: {response.status_code}")
            return
    except requests.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    print("\n🌐 Step 2: API Documentation Check")
    print("-" * 35)
    
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get('paths', {})
            
            weather_endpoints = [path for path in paths.keys() if '/weather/' in path]
            print(f"✅ Found {len(weather_endpoints)} weather endpoints:")
            for endpoint in weather_endpoints:
                print(f"   🌐 {endpoint}")
        else:
            print(f"❌ Schema not accessible: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Schema check failed: {e}")
    
    print("\n🌤️ Step 3: Weather Endpoint Testing")
    print("-" * 40)
    
    # Test sample data without authentication for now
    weather_endpoints_test = [
        "/api/v1/weather/current/test-farm-id",
        "/api/v1/weather/forecast/test-farm-id",
        "/api/v1/weather/alerts/test-farm-id"
    ]
    
    for endpoint in weather_endpoints_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"\n🔍 Testing: {endpoint}")
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Valid JSON response")
                    
                    # Check response structure
                    if "data" in data:
                        weather_data = data["data"]
                        print(f"   📦 Data structure keys: {list(weather_data.keys()) if isinstance(weather_data, dict) else 'Not a dict'}")
                        
                        # Check for common weather fields
                        if isinstance(weather_data, dict):
                            expected_fields = ["temperature", "humidity", "description", "location"]
                            missing_fields = [field for field in expected_fields if field not in weather_data]
                            
                            if missing_fields:
                                print(f"   ⚠️ Missing fields: {missing_fields}")
                                issues_found.append(f"Missing fields in {endpoint}: {missing_fields}")
                            else:
                                print(f"   ✅ All expected fields present")
                                
                                # Display sample data
                                print(f"   🌡️ Temperature: {weather_data.get('temperature', 'N/A')}°C")
                                print(f"   💧 Humidity: {weather_data.get('humidity', 'N/A')}%")
                                print(f"   🌤️ Description: {weather_data.get('description', 'N/A')}")
                                
                                if 'location' in weather_data:
                                    location = weather_data['location']
                                    print(f"   📍 Location: {location.get('city', 'N/A')}, {location.get('region', 'N/A')}")
                    else:
                        print(f"   ❌ No 'data' field in response")
                        issues_found.append(f"No data field in {endpoint}")
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response")
                    issues_found.append(f"Invalid JSON in {endpoint}")
                    
            elif response.status_code == 401 or response.status_code == 403:
                print(f"   🔐 Authentication required (expected)")
                
            elif response.status_code == 404:
                print(f"   ❌ Endpoint not found")
                issues_found.append(f"Endpoint not found: {endpoint}")
                
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📋 Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   📋 Error: {response.text[:100]}...")
                    
        except requests.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            issues_found.append(f"Request failed for {endpoint}: {str(e)}")
    
    print("\n🧪 Step 4: Direct Weather Service Test")
    print("-" * 40)
    
    try:
        # Test the enhanced weather service directly
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__)))
        
        from app.services.enhanced_weather_service import enhanced_weather_service
        
        # Test current weather
        print("📍 Testing direct weather service call...")
        
        import asyncio
        
        async def test_weather_service():
            weather_data = await enhanced_weather_service.get_current_weather(
                latitude=23.3441,  # Ranchi coordinates
                longitude=85.3096,
                district="Ranchi"
            )
            
            print(f"✅ Direct weather service working:")
            print(f"   🌡️ Temperature: {weather_data.get('temperature', 'N/A')}°C")
            print(f"   💧 Humidity: {weather_data.get('humidity', 'N/A')}%")
            print(f"   🌤️ Description: {weather_data.get('description', 'N/A')}")
            print(f"   📊 Source: {weather_data.get('source', 'N/A')}")
            
            # Check for potential display issues
            if weather_data.get('temperature') is None:
                issues_found.append("Temperature is None in weather data")
                
            if weather_data.get('humidity') is None:
                issues_found.append("Humidity is None in weather data")
                
            if not weather_data.get('description'):
                issues_found.append("Description is empty in weather data")
        
        asyncio.run(test_weather_service())
        
    except Exception as e:
        print(f"❌ Direct weather service test failed: {e}")
        issues_found.append(f"Direct weather service failed: {str(e)}")
    
    print("\n📋 Issues Summary")
    print("=" * 55)
    
    if not issues_found:
        print("🎉 NO WEATHER ISSUES FOUND!")
        print("\n✅ All checks passed:")
        print("   🏥 Server health - OK")
        print("   🌐 Weather endpoints - Available")
        print("   📦 Data structure - Valid")
        print("   🧪 Weather service - Working")
        
        print("\n💡 Weather display should be working correctly!")
        print("   If you're seeing display issues, they might be:")
        print("   🔐 Authentication problems in the frontend")
        print("   📱 Frontend-backend API connection issues")
        print("   🎨 CSS/styling problems in the weather components")
        
    else:
        print(f"❌ {len(issues_found)} WEATHER ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 Recommended Actions:")
        for issue in issues_found:
            if "Missing fields" in issue:
                print(f"   📦 Check weather data formatting in API response")
            elif "Authentication" in issue:
                print(f"   🔐 Check authentication flow for weather endpoints")
            elif "not found" in issue.lower():
                print(f"   🌐 Check weather route registration")
    
    return issues_found

if __name__ == "__main__":
    test_weather_endpoints()
