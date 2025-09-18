"""
Test API endpoints to verify real data usage
"""

import requests
import json
from datetime import datetime

def test_health_check():
    """Test health endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("❤️  Health Check: ✅ Working")
            return True
        else:
            print(f"❤️  Health Check: ❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❤️  Health Check: ❌ Error: {str(e)}")
        return False

def test_weather_api():
    """Test weather endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/weather/current/1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            weather_data = data.get('data', {})
            source = weather_data.get('data_source', 'unknown')
            
            print(f"🌤️  Weather API: ✅ Working (Source: {source})")
            if 'weatherapi' in source or 'openweathermap' in source:
                print("   ✅ Using real weather API")
                return True
            else:
                print(f"   ⚠️  Using fallback data: {source}")
                return False
        else:
            print(f"🌤️  Weather API: ❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"🌤️  Weather API: ❌ Error: {str(e)}")
        return False

def test_market_api():
    """Test market endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/market/prices/Ranchi?crop=Wheat", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("📈 Market API: ✅ Working")
            return True
        else:
            print(f"📈 Market API: ❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"📈 Market API: ❌ Error: {str(e)}")
        return False

def test_finance_api():
    """Test finance endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/finance/loans/products", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("💰 Finance API: ✅ Working")
            return True
        else:
            print(f"💰 Finance API: ❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"💰 Finance API: ❌ Error: {str(e)}")
        return False

def main():
    print("🔍 API ENDPOINT TESTING")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    results['health'] = test_health_check()
    results['weather'] = test_weather_api()
    results['market'] = test_market_api()
    results['finance'] = test_finance_api()
    
    print("\n📊 TEST SUMMARY:")
    print("=" * 20)
    
    passing = sum(1 for result in results.values() if result)
    total = len(results)
    
    for service, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {service.upper()}: {'PASS' if status else 'FAIL'}")
    
    print(f"\nOverall: {passing}/{total} endpoints working")
    
    if passing == total:
        print("🎉 All APIs are working with real data!")
    else:
        print("⚠️  Some APIs may need attention")

if __name__ == "__main__":
    main()
