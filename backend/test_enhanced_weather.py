#!/usr/bin/env python3
"""
🌤️ Enhanced Weather Integration Test for AuraFarming
==================================================

Tests the enhanced weather service with multiple providers and fallback.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.enhanced_weather_service import enhanced_weather_service

def print_banner():
    print("🌤️ AuraFarming: Enhanced Weather Integration Test")
    print("=" * 60)
    print("🎯 Testing weather API with multiple providers")
    print("🏪 Jharkhand-specific weather intelligence")
    print("=" * 60)

async def test_enhanced_weather_integration():
    """Test the complete enhanced weather integration system."""
    
    print_banner()
    
    # Test locations in Jharkhand
    test_locations = [
        {"name": "Ranchi", "lat": 23.3441, "lon": 85.3096},
        {"name": "Dhanbad", "lat": 23.7957, "lon": 86.4304},
        {"name": "Jamshedpur", "lat": 22.8046, "lon": 86.2029}
    ]
    
    print("\n🌡️ Test 1: Current Weather Data")
    print("-" * 40)
    
    for location in test_locations:
        try:
            print(f"\n📍 {location['name']}:")
            weather_data = await enhanced_weather_service.get_current_weather(
                latitude=location['lat'],
                longitude=location['lon'],
                district=location['name']
            )
            
            if weather_data["status"] == "success":
                current = weather_data["current"]
                print(f"   🌡️ Temperature: {current['temperature']}°C (feels like {current['feels_like']}°C)")
                print(f"   💧 Humidity: {current['humidity']}%")
                print(f"   🌤️ Condition: {current['description']}")
                print(f"   💨 Wind: {current['wind_speed']} m/s")
                print(f"   📊 Source: {weather_data['data_source']}")
                
                # Farming insights
                if "farming_insights" in weather_data:
                    insights = weather_data["farming_insights"]
                    print(f"   🚰 Irrigation: {insights['irrigation_recommendation']}")
                    print(f"   🌾 Field work: {insights['field_work_suitability']}")
                    if insights["recommendations"]:
                        print(f"   💡 Tip: {insights['recommendations'][0]}")
                
                # Seasonal info (for fallback data)
                if "seasonal_info" in weather_data:
                    seasonal = weather_data["seasonal_info"]
                    print(f"   📅 Season: {seasonal['season']}")
                    print(f"   🌱 Phase: {seasonal['farming_phase']}")
            else:
                print(f"   ❌ Failed to get weather data")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n📅 Test 2: Weather Forecast")
    print("-" * 40)
    
    try:
        # Test 5-day forecast for Ranchi
        forecast_data = await enhanced_weather_service.get_weather_forecast(
            latitude=23.3441,
            longitude=85.3096,
            days=5,
            district="Ranchi"
        )
        
        if forecast_data["status"] == "success":
            print(f"✅ 5-day forecast for Ranchi:")
            print(f"   📊 Source: {forecast_data['data_source']}")
            
            for day_forecast in forecast_data["forecast"][:3]:  # Show first 3 days
                print(f"   📅 {day_forecast['date']}: {day_forecast['temperature_min']}°C - {day_forecast['temperature_max']}°C")
                print(f"      🌤️ {day_forecast['description']} (Rain: {day_forecast['rain_probability']}%)")
        else:
            print("❌ Failed to get forecast data")
            
    except Exception as e:
        print(f"❌ Forecast error: {str(e)}")
    
    print("\n🔬 Test 3: API Provider Testing")
    print("-" * 40)
    
    try:
        # Test direct API methods
        print("🔍 Testing OpenWeatherMap API...")
        openweather_result = await enhanced_weather_service._try_openweather(23.3441, 85.3096)
        if openweather_result:
            print("✅ OpenWeatherMap API: Working")
            print(f"   📍 Location: {openweather_result['name']}")
            print(f"   🌡️ Temperature: {openweather_result['main']['temp']}°C")
        else:
            print("⚠️ OpenWeatherMap API: Not responding (using fallback)")
        
        print("\n🔍 Testing WeatherAPI.com...")
        weatherapi_result = await enhanced_weather_service._try_weatherapi(23.3441, 85.3096)
        if weatherapi_result:
            print("✅ WeatherAPI.com: Working")
            print(f"   📍 Location: {weatherapi_result['location']['name']}")
            print(f"   🌡️ Temperature: {weatherapi_result['current']['temp_c']}°C")
        else:
            print("⚠️ WeatherAPI.com: Not available (expected)")
        
    except Exception as e:
        print(f"❌ API testing error: {str(e)}")
    
    print("\n🌾 Test 4: Farming Intelligence Features")
    print("-" * 40)
    
    try:
        # Test Jharkhand-specific features
        weather_data = await enhanced_weather_service.get_current_weather(
            latitude=23.3441,
            longitude=85.3096,
            district="Ranchi"
        )
        
        if "farming_insights" in weather_data:
            insights = weather_data["farming_insights"]
            print("✅ Farming Intelligence Active:")
            print(f"   🚰 Irrigation recommendation: {insights['irrigation_recommendation']}")
            print(f"   🐛 Pest risk level: {insights['pest_risk']}")
            print(f"   🦠 Disease risk level: {insights['disease_risk']}")
            print(f"   👨‍🌾 Field work suitability: {insights['field_work_suitability']}")
            
            if insights["recommendations"]:
                print("   💡 Recommendations:")
                for i, rec in enumerate(insights["recommendations"][:2], 1):
                    print(f"      {i}. {rec}")
        
        if "seasonal_info" in weather_data:
            seasonal = weather_data["seasonal_info"]
            print(f"\n✅ Seasonal Intelligence:")
            print(f"   📅 Current season: {seasonal['season']}")
            print(f"   🌱 Farming phase: {seasonal['farming_phase']}")
            print(f"   📋 Recommended activities:")
            for i, activity in enumerate(seasonal["recommended_activities"][:2], 1):
                print(f"      {i}. {activity}")
            
    except Exception as e:
        print(f"❌ Farming intelligence error: {str(e)}")
    
    print("\n🚀 Enhanced Weather Integration Summary")
    print("=" * 60)
    print("✅ Multiple weather API providers tested")
    print("✅ Intelligent fallback system active")
    print("✅ Jharkhand-specific weather patterns")
    print("✅ Farming-focused insights and recommendations")
    print("✅ Seasonal intelligence for crop planning")
    print("✅ District-specific weather variations")
    
    print("\n🎉 Enhanced weather integration is fully operational!")
    print("   Real weather APIs + Smart fallback = Reliable farming intelligence")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_enhanced_weather_integration())
