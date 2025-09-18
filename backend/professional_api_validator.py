"""
Professional API Validation Suite for AuraFarming
Comprehensive testing with proper authentication and error handling.
"""

import requests
import json
import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AuraFarmingAPIValidator:
    """Professional API validation class with authentication and comprehensive testing."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = {}
        
    def authenticate(self) -> bool:
        """Authenticate and get access token for protected endpoints."""
        try:
            # First, try to register a test user or use existing credentials
            test_user = {
                "username": "test_validator",
                "email": "validator@aurafarming.test",
                "password": "ValidationPass123!",
                "full_name": "API Validator",
                "phone": "9999999999"
            }
            
            # Try login first, if fails, try registration
            login_response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data={"username": test_user["username"], "password": test_user["password"]},
                timeout=10
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                self.auth_token = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                return True
            else:
                # Try registration
                register_response = self.session.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json=test_user,
                    timeout=10
                )
                
                if register_response.status_code in [200, 201]:
                    # Now login
                    login_response = self.session.post(
                        f"{self.base_url}/api/v1/auth/login",
                        data={"username": test_user["username"], "password": test_user["password"]},
                        timeout=10
                    )
                    
                    if login_response.status_code == 200:
                        token_data = login_response.json()
                        self.auth_token = token_data.get("access_token")
                        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                        return True
                        
        except Exception as e:
            print(f"⚠️  Authentication setup failed: {str(e)}")
            
        return False
    
    def test_health_endpoints(self) -> Dict[str, Any]:
        """Test health and status endpoints."""
        results = {}
        
        # Test root endpoint
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            results["root"] = {
                "status": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
            }
        except Exception as e:
            results["root"] = {"status": False, "response_time": 0, "error": str(e)}
        
        # Test health endpoint
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            results["health"] = {
                "status": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
            }
        except Exception as e:
            results["health"] = {"status": False, "response_time": 0, "error": str(e)}
        
        return results
    
    def test_weather_endpoints(self) -> Dict[str, Any]:
        """Test weather API endpoints with proper authentication."""
        results = {}
        
        # Test current weather endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/v1/weather/current/1", timeout=15)
            if response.status_code == 200:
                data = response.json()
                weather_data = data.get('data', {})
                source = weather_data.get('data_source', 'unknown')
                
                results["current_weather"] = {
                    "status": True,
                    "response_time": response.elapsed.total_seconds(),
                    "data_source": source,
                    "using_real_api": 'weatherapi' in source or 'openweathermap' in source,
                    "error": None
                }
            else:
                results["current_weather"] = {
                    "status": False,
                    "response_time": response.elapsed.total_seconds(),
                    "error": f"HTTP {response.status_code}",
                    "using_real_api": False
                }
        except Exception as e:
            results["current_weather"] = {
                "status": False,
                "response_time": 0,
                "error": str(e),
                "using_real_api": False
            }
        
        return results
    
    def test_market_endpoints(self) -> Dict[str, Any]:
        """Test market API endpoints."""
        results = {}
        
        # Test market prices endpoint
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/market/prices/Ranchi?crop=Wheat",
                timeout=15
            )
            
            results["market_prices"] = {
                "status": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
            }
            
            if response.status_code == 200:
                data = response.json()
                results["market_prices"]["has_data"] = bool(data.get('data'))
                
        except Exception as e:
            results["market_prices"] = {
                "status": False,
                "response_time": 0,
                "error": str(e),
                "has_data": False
            }
        
        return results
    
    def test_finance_endpoints(self) -> Dict[str, Any]:
        """Test finance API endpoints with authentication."""
        results = {}
        
        # Test loan products endpoint
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/finance/loans/products",
                timeout=15
            )
            
            results["loan_products"] = {
                "status": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}",
                "requires_auth": response.status_code == 401
            }
            
        except Exception as e:
            results["loan_products"] = {
                "status": False,
                "response_time": 0,
                "error": str(e),
                "requires_auth": True
            }
        
        return results
    
    def test_configuration(self) -> Dict[str, Any]:
        """Test configuration and environment setup."""
        results = {}
        
        try:
            from app.core.config import settings
            
            # Check database configuration
            db_config = {
                "supabase_url": bool(settings.SUPABASE_URL and 'your_' not in settings.SUPABASE_URL),
                "supabase_anon_key": bool(settings.SUPABASE_ANON_KEY and 'your_' not in settings.SUPABASE_ANON_KEY),
                "service_role_key": bool(settings.SUPABASE_SERVICE_ROLE_KEY and 'your_' not in settings.SUPABASE_SERVICE_ROLE_KEY)
            }
            
            # Check API keys
            api_config = {
                "weatherapi_key": bool(settings.WEATHERAPI_KEY and 'mock' not in settings.WEATHERAPI_KEY.lower()),
                "openweather_key": bool(settings.OPENWEATHER_API_KEY and 'mock' not in settings.OPENWEATHER_API_KEY.lower()) if settings.OPENWEATHER_API_KEY else False
            }
            
            results["configuration"] = {
                "database": db_config,
                "apis": api_config,
                "environment": settings.ENVIRONMENT,
                "debug": settings.DEBUG
            }
            
        except Exception as e:
            results["configuration"] = {
                "error": str(e),
                "status": False
            }
        
        return results
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete API validation suite."""
        print("🔍 AURAFARMING PROFESSIONAL API VALIDATION")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target: {self.base_url}")
        print()
        
        # Step 1: Test basic connectivity
        print("1️⃣  TESTING BASIC CONNECTIVITY...")
        health_results = self.test_health_endpoints()
        
        if not any(result["status"] for result in health_results.values()):
            print("❌ Server not responding. Please ensure the backend is running.")
            return {"error": "Server not responding", "results": health_results}
        
        print("✅ Server is responding")
        
        # Step 2: Test configuration
        print("\n2️⃣  TESTING CONFIGURATION...")
        config_results = self.test_configuration()
        
        # Step 3: Setup authentication
        print("\n3️⃣  SETTING UP AUTHENTICATION...")
        auth_success = self.authenticate()
        if auth_success:
            print("✅ Authentication successful")
        else:
            print("⚠️  Authentication setup failed - testing public endpoints only")
        
        # Step 4: Test weather endpoints
        print("\n4️⃣  TESTING WEATHER SERVICES...")
        weather_results = self.test_weather_endpoints()
        
        # Step 5: Test market endpoints
        print("\n5️⃣  TESTING MARKET SERVICES...")
        market_results = self.test_market_endpoints()
        
        # Step 6: Test finance endpoints
        print("\n6️⃣  TESTING FINANCE SERVICES...")
        finance_results = self.test_finance_endpoints()
        
        # Compile results
        all_results = {
            "health": health_results,
            "configuration": config_results,
            "authentication": {"success": auth_success},
            "weather": weather_results,
            "market": market_results,
            "finance": finance_results
        }
        
        # Generate report
        self.generate_validation_report(all_results)
        
        return all_results
    
    def generate_validation_report(self, results: Dict[str, Any]):
        """Generate a comprehensive validation report."""
        print("\n📊 VALIDATION REPORT")
        print("=" * 60)
        
        # Health check results
        health_results = results.get("health", {})
        health_passed = sum(1 for r in health_results.values() if r.get("status", False))
        print(f"🏥 Health Checks: {health_passed}/{len(health_results)} passed")
        
        for endpoint, result in health_results.items():
            status = "✅" if result.get("status") else "❌"
            time_ms = int(result.get("response_time", 0) * 1000)
            print(f"   {status} {endpoint}: {time_ms}ms")
        
        # Configuration results
        config = results.get("configuration", {})
        if "database" in config:
            db_config = config["database"]
            db_passed = sum(1 for v in db_config.values() if v)
            print(f"\n🗄️  Database Config: {db_passed}/{len(db_config)} configured")
            
            api_config = config["apis"]
            api_passed = sum(1 for v in api_config.values() if v)
            print(f"🔑 API Keys: {api_passed}/{len(api_config)} configured")
        
        # Service results
        service_categories = ["weather", "market", "finance"]
        total_services = 0
        passed_services = 0
        
        for category in service_categories:
            category_results = results.get(category, {})
            category_total = len(category_results)
            category_passed = sum(1 for r in category_results.values() if r.get("status", False))
            
            total_services += category_total
            passed_services += category_passed
            
            emoji = {"weather": "🌤️", "market": "📈", "finance": "💰"}.get(category, "🔧")
            print(f"{emoji} {category.title()} APIs: {category_passed}/{category_total} working")
            
            for endpoint, result in category_results.items():
                status = "✅" if result.get("status") else "❌"
                time_ms = int(result.get("response_time", 0) * 1000)
                error = result.get("error", "")
                print(f"   {status} {endpoint}: {time_ms}ms {error}")
        
        # Overall summary
        print(f"\n🎯 OVERALL SCORE: {passed_services}/{total_services} endpoints working")
        
        # Data quality assessment
        print("\n🔍 DATA QUALITY ASSESSMENT:")
        weather_results = results.get("weather", {})
        current_weather = weather_results.get("current_weather", {})
        
        if current_weather.get("using_real_api"):
            print("   ✅ Weather: Using real API data")
        elif current_weather.get("status"):
            print("   ⚠️  Weather: Using fallback data (check API keys)")
        else:
            print("   ❌ Weather: Not working")
        
        market_results = results.get("market", {})
        if market_results.get("market_prices", {}).get("status"):
            print("   ✅ Market: API working (uses intelligent fallback)")
        else:
            print("   ❌ Market: Not working")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        config = results.get("configuration", {})
        if config.get("apis", {}).get("weatherapi_key", False):
            print("   ✅ Weather API properly configured")
        else:
            print("   ⚠️  Configure WEATHERAPI_KEY for better weather data")
        
        if config.get("database", {}).get("supabase_url", False):
            print("   ✅ Database properly configured")
        else:
            print("   ❌ Configure Supabase credentials")
        
        if results.get("authentication", {}).get("success"):
            print("   ✅ Authentication system working")
        else:
            print("   ⚠️  Authentication may need attention for protected endpoints")

def main():
    """Main validation entry point."""
    validator = AuraFarmingAPIValidator()
    results = validator.run_comprehensive_validation()
    
    # Save results to file
    with open("api_validation_report.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: api_validation_report.json")
    
    return results

if __name__ == "__main__":
    main()
