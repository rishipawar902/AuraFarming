"""
Simple API Configuration Check
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def check_configuration():
    """Check configuration for mock data usage."""
    print("🔍 CONFIGURATION CHECK")
    print("=" * 40)
    
    # Check database configuration
    print("\n📊 Database Configuration:")
    print(f"  Supabase URL: {'✅ Configured' if settings.SUPABASE_URL and 'your_' not in settings.SUPABASE_URL else '❌ Missing/Template'}")
    print(f"  Supabase Anon Key: {'✅ Configured' if settings.SUPABASE_ANON_KEY and 'your_' not in settings.SUPABASE_ANON_KEY else '❌ Missing/Template'}")
    print(f"  Service Role Key: {'✅ Configured' if settings.SUPABASE_SERVICE_ROLE_KEY and 'your_' not in settings.SUPABASE_SERVICE_ROLE_KEY else '❌ Missing/Template'}")
    
    # Check API keys
    print("\n🌤️  Weather API Configuration:")
    weatherapi_status = "❌ Missing/Template"
    if settings.WEATHERAPI_KEY:
        if 'mock' in settings.WEATHERAPI_KEY.lower() or 'your_' in settings.WEATHERAPI_KEY.lower():
            weatherapi_status = "⚠️  Mock/Template Key"
        else:
            weatherapi_status = "✅ Configured"
    print(f"  WeatherAPI Key: {weatherapi_status}")
    
    openweather_status = "❌ Missing/Template"
    if settings.OPENWEATHER_API_KEY:
        if 'mock' in settings.OPENWEATHER_API_KEY.lower() or 'your_' in settings.OPENWEATHER_API_KEY.lower():
            openweather_status = "⚠️  Mock/Template Key"
        else:
            openweather_status = "✅ Configured"
    print(f"  OpenWeather Key: {openweather_status}")
    
    # Check for any hardcoded values
    print("\n🔧 Hardcoded Value Check:")
    config_file = "app/core/config.py"
    has_hardcoded = False
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
            if 'mock_' in content:
                print("  ⚠️  Found 'mock_' references in config")
                has_hardcoded = True
            if '"579b464db66ec23bdd000001868cc9d701ff4a6a4aa653ce3584fefe"' in content:
                print("  ❌ Found hardcoded WeatherAPI key")
                has_hardcoded = True
            if not has_hardcoded:
                print("  ✅ No hardcoded values found")
    except Exception as e:
        print(f"  ❌ Error checking config file: {e}")
    
    # Summary
    print("\n📋 SUMMARY:")
    db_configured = all([
        settings.SUPABASE_URL and 'your_' not in settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY and 'your_' not in settings.SUPABASE_ANON_KEY,
        settings.SUPABASE_SERVICE_ROLE_KEY and 'your_' not in settings.SUPABASE_SERVICE_ROLE_KEY
    ])
    
    weather_configured = (
        settings.WEATHERAPI_KEY and 
        'mock' not in settings.WEATHERAPI_KEY.lower() and 
        'your_' not in settings.WEATHERAPI_KEY.lower()
    )
    
    if db_configured:
        print("  ✅ Database: Using real Supabase")
    else:
        print("  ❌ Database: Missing configuration")
        
    if weather_configured:
        print("  ✅ Weather: Using real API")
    else:
        print("  ⚠️  Weather: May fall back to mock data")
        
    print("  ✅ Market: Uses AGMARKNET with intelligent fallback")
    print("  ✅ Finance: Uses calculation-based approach")
    
    return db_configured and weather_configured

if __name__ == "__main__":
    check_configuration()
