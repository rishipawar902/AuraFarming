"""
Debug weather data formatting to identify why fields are returning None.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_weather_service import EnhancedWeatherService
import json

async def debug_weather_service():
    """Debug the weather service to see raw and formatted data."""
    service = EnhancedWeatherService()
    
    # Test coordinates for Ranchi
    lat, lon = 23.3441, 85.3096
    district = "Ranchi"
    
    print("🔍 DEBUGGING WEATHER SERVICE")
    print("=" * 50)
    
    # Test WeatherAPI directly
    print("\n1. Testing WeatherAPI directly...")
    raw_weather_data = await service._try_weatherapi(lat, lon)
    if raw_weather_data:
        print("✅ WeatherAPI Raw Data:")
        print(json.dumps(raw_weather_data, indent=2))
        
        # Test formatting
        print("\n2. Testing WeatherAPI formatting...")
        formatted_data = service._format_weather_response(raw_weather_data, "weatherapi", district)
        print("✅ Formatted Data:")
        print(json.dumps(formatted_data, indent=2))
        
        # Check specific fields
        print("\n3. Checking specific fields...")
        current = formatted_data.get("current", {})
        print(f"Temperature: {current.get('temperature')} (type: {type(current.get('temperature'))})")
        print(f"Humidity: {current.get('humidity')} (type: {type(current.get('humidity'))})")
        print(f"Description: {current.get('description')} (type: {type(current.get('description'))})")
    else:
        print("❌ WeatherAPI failed, trying OpenWeatherMap...")
        
        # Test OpenWeatherMap
        raw_weather_data = await service._try_openweather(lat, lon)
        if raw_weather_data:
            print("✅ OpenWeatherMap Raw Data:")
            print(json.dumps(raw_weather_data, indent=2))
            
            formatted_data = service._format_weather_response(raw_weather_data, "openweathermap", district)
            print("✅ Formatted Data:")
            print(json.dumps(formatted_data, indent=2))
        else:
            print("❌ Both APIs failed, using fallback...")
            fallback_data = service._get_enhanced_fallback_weather(lat, lon, district)
            print("✅ Fallback Data:")
            print(json.dumps(fallback_data, indent=2))
    
    # Test the full service
    print("\n4. Testing full service...")
    weather_response = await service.get_current_weather(lat, lon, district)
    print("✅ Full Service Response:")
    print(json.dumps(weather_response, indent=2))
    
    # Check final API response format
    print("\n5. Final API Response Check...")
    current = weather_response.get("current", {})
    print(f"Final Temperature: {current.get('temperature')}")
    print(f"Final Humidity: {current.get('humidity')}")
    print(f"Final Description: '{current.get('description')}'")

if __name__ == "__main__":
    asyncio.run(debug_weather_service())
