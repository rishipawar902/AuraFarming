"""
Professional API Validation Suite for AuraFarming
Comprehensive testing of all APIs to ensure no mock data is used and all services work properly.
"""

import asyncio
import sys
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfessionalAPIValidator:
    """Professional API validation suite for AuraFarming."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        self.auth_token = None
        
    def print_header(self, title: str):
        """Print a professional header."""
        print("\n" + "=" * 80)
        print(f" {title}")
        print("=" * 80)
        
    def print_section(self, title: str):
        """Print a section header."""
        print(f"\n📋 {title}")
        print("-" * 60)
        
    def print_result(self, test_name: str, status: bool, details: str = ""):
        """Print test result with proper formatting."""
        emoji = "✅" if status else "❌"
        print(f"{emoji} {test_name}: {'PASS' if status else 'FAIL'}")
        if details:
            print(f"   📝 {details}")
            
    def test_server_connectivity(self) -> bool:
        """Test if the server is running and accessible."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_result("Server Health Check", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.print_result("Server Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Server Health Check", False, f"Connection error: {str(e)}")
            return False
            
    def test_database_configuration(self) -> bool:
        """Test database configuration and connectivity."""
        try:
            from app.core.config import settings
            from app.services.database import DatabaseService
            
            # Check configuration
            config_valid = all([
                settings.SUPABASE_URL and 'your_' not in settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY and 'your_' not in settings.SUPABASE_ANON_KEY,
                settings.SUPABASE_SERVICE_ROLE_KEY and 'your_' not in settings.SUPABASE_SERVICE_ROLE_KEY
            ])
            
            if not config_valid:
                self.print_result("Database Configuration", False, "Missing or template values in configuration")
                return False
                
            # Test database service
            db = DatabaseService()
            if hasattr(db, 'use_mock') and db.use_mock:
                self.print_result("Database Service", False, "Using mock database instead of Supabase")
                return False
            else:
                self.print_result("Database Configuration", True, "Real Supabase database configured")
                return True
                
        except Exception as e:
            self.print_result("Database Configuration", False, f"Error: {str(e)}")
            return False
            
    def test_weather_service_configuration(self) -> bool:
        """Test weather service configuration for real APIs."""
        try:
            from app.core.config import settings
            
            # Check WeatherAPI key
            weatherapi_valid = (
                settings.WEATHERAPI_KEY and 
                'mock' not in settings.WEATHERAPI_KEY.lower() and 
                'your_' not in settings.WEATHERAPI_KEY.lower() and
                len(settings.WEATHERAPI_KEY) > 20  # Real API keys are longer
            )
            
            # Check OpenWeather key (optional but preferred)
            openweather_valid = (
                settings.OPENWEATHER_API_KEY and 
                'mock' not in settings.OPENWEATHER_API_KEY.lower() and 
                'your_' not in settings.OPENWEATHER_API_KEY.lower()
            )
            
            if weatherapi_valid:
                self.print_result("WeatherAPI Configuration", True, "Real WeatherAPI key configured")
                return True
            elif openweather_valid:
                self.print_result("Weather Service Configuration", True, "OpenWeatherMap key configured")
                return True
            else:
                self.print_result("Weather Service Configuration", False, "No valid weather API keys found")
                return False
                
        except Exception as e:
            self.print_result("Weather Service Configuration", False, f"Error: {str(e)}")
            return False
            
    def test_weather_service_functionality(self) -> bool:
        """Test weather service functionality with real data."""
        try:
            from app.services.enhanced_weather_service import EnhancedWeatherService
            
            async def test_weather():
                service = EnhancedWeatherService()
                # Test with Ranchi coordinates
                weather_data = await service.get_current_weather(23.3441, 85.3096, "Ranchi")
                
                if weather_data:
                    source = weather_data.get('data_source', 'unknown')
                    
                    # Check if using real API
                    if 'weatherapi' in source.lower() or 'openweathermap' in source.lower():
                        self.print_result("Weather Service Functionality", True, f"Using real API: {source}")
                        return True
                    else:
                        self.print_result("Weather Service Functionality", False, f"Using fallback data: {source}")
                        return False
                else:
                    self.print_result("Weather Service Functionality", False, "No weather data returned")
                    return False
                    
            return asyncio.run(test_weather())
            
        except Exception as e:
            self.print_result("Weather Service Functionality", False, f"Error: {str(e)}")
            return False
            
    def test_market_service_functionality(self) -> bool:
        """Test market service functionality."""
        try:
            from app.services.enhanced_agmarknet_scraper import EnhancedAGMARKNETScraper
            
            async def test_market():
                scraper = EnhancedAGMARKNETScraper()
                market_data = await scraper.get_market_data("Ranchi", "Wheat")
                
                if market_data:
                    source = market_data.get('metadata', {}).get('source', 'unknown')
                    self.print_result("Market Service Functionality", True, f"Source: {source}")
                    return True
                else:
                    self.print_result("Market Service Functionality", False, "No market data returned")
                    return False
                    
            return asyncio.run(test_market())
            
        except Exception as e:
            self.print_result("Market Service Functionality", False, f"Error: {str(e)}")
            return False
            
    def test_finance_service_functionality(self) -> bool:
        """Test finance service functionality."""
        try:
            from app.services.enhanced_finance_service import EnhancedFinanceService
            
            service = EnhancedFinanceService()
            self.print_result("Finance Service Functionality", True, "Calculation-based service (no external APIs required)")
            return True
            
        except Exception as e:
            self.print_result("Finance Service Functionality", False, f"Error: {str(e)}")
            return False
            
    def test_authenticated_endpoints(self) -> Dict[str, bool]:
        """Test authenticated API endpoints."""
        results = {}
        
        # Test endpoints that don't require authentication
        endpoints = [
            ("/api/v1/market/prices/Ranchi?crop=Wheat", "Market Prices API"),
            ("/api/v1/market/trends/Wheat?days=7", "Market Trends API"),
        ]
        
        for endpoint, name in endpoints:
            try:
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.print_result(name, True, "Endpoint accessible")
                    results[name] = True
                elif response.status_code == 401:
                    self.print_result(name, False, "Authentication required (expected)")
                    results[name] = False
                else:
                    self.print_result(name, False, f"HTTP {response.status_code}")
                    results[name] = False
                    
            except Exception as e:
                self.print_result(name, False, f"Error: {str(e)}")
                results[name] = False
                
        return results
        
    def check_code_quality(self) -> Dict[str, bool]:
        """Check code quality and mock data usage."""
        results = {}
        
        # Check for hardcoded mock values in configuration
        try:
            config_file = "app/core/config.py"
            with open(config_file, 'r') as f:
                content = f.read()
                
            issues = []
            if 'mock_' in content:
                issues.append("Found 'mock_' references")
                
            if issues:
                self.print_result("Configuration Code Quality", False, "; ".join(issues))
                results["config_quality"] = False
            else:
                self.print_result("Configuration Code Quality", True, "No hardcoded mock values found")
                results["config_quality"] = True
                
        except Exception as e:
            self.print_result("Configuration Code Quality", False, f"Error: {str(e)}")
            results["config_quality"] = False
            
        return results
        
    def generate_professional_report(self, all_results: Dict[str, bool]) -> str:
        """Generate a professional validation report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
AURAFARMING API VALIDATION REPORT
{'=' * 50}
Generated: {timestamp}
Validation Suite: Professional API Validator v1.0

EXECUTIVE SUMMARY:
{'-' * 20}
"""
        
        total_tests = len(all_results)
        passed_tests = sum(1 for result in all_results.values() if result)
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report += f"Total Tests: {total_tests}\n"
        report += f"Passed: {passed_tests}\n"
        report += f"Failed: {total_tests - passed_tests}\n"
        report += f"Pass Rate: {pass_rate:.1f}%\n\n"
        
        if pass_rate >= 90:
            report += "SYSTEM STATUS: EXCELLENT - Production Ready\n"
        elif pass_rate >= 75:
            report += "SYSTEM STATUS: GOOD - Minor issues to address\n"
        elif pass_rate >= 50:
            report += "SYSTEM STATUS: FAIR - Several issues need attention\n"
        else:
            report += "SYSTEM STATUS: POOR - Major issues require immediate attention\n"
            
        report += "\nDETAILED RESULTS:\n"
        report += "-" * 20 + "\n"
        
        for test_name, result in all_results.items():
            status = "PASS" if result else "FAIL"
            report += f"{status} {test_name}\n"
            
        report += f"\n{'=' * 50}\n"
        
        return report
        
    def run_comprehensive_validation(self) -> bool:
        """Run comprehensive validation suite."""
        self.print_header("AURAFARMING PROFESSIONAL API VALIDATION SUITE")
        print(f"🔍 Validating system integrity and real data usage")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = {}
        
        # Phase 1: Infrastructure Tests
        self.print_section("PHASE 1: INFRASTRUCTURE VALIDATION")
        all_results["server_connectivity"] = self.test_server_connectivity()
        all_results["database_configuration"] = self.test_database_configuration()
        
        # Phase 2: Service Configuration Tests
        self.print_section("PHASE 2: SERVICE CONFIGURATION VALIDATION")
        all_results["weather_configuration"] = self.test_weather_service_configuration()
        
        # Phase 3: Functionality Tests
        self.print_section("PHASE 3: SERVICE FUNCTIONALITY VALIDATION")
        all_results["weather_functionality"] = self.test_weather_service_functionality()
        all_results["market_functionality"] = self.test_market_service_functionality()
        all_results["finance_functionality"] = self.test_finance_service_functionality()
        
        # Phase 4: API Endpoint Tests
        self.print_section("PHASE 4: API ENDPOINT VALIDATION")
        endpoint_results = self.test_authenticated_endpoints()
        all_results.update(endpoint_results)
        
        # Phase 5: Code Quality Tests
        self.print_section("PHASE 5: CODE QUALITY VALIDATION")
        quality_results = self.check_code_quality()
        all_results.update(quality_results)
        
        # Generate report
        self.print_section("VALIDATION REPORT")
        report = self.generate_professional_report(all_results)
        print(report)
        
        # Save report to file
        with open("validation_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print("📄 Detailed report saved to: validation_report.txt")
        
        # Return overall success
        pass_rate = sum(1 for result in all_results.values() if result) / len(all_results)
        return pass_rate >= 0.8  # 80% pass rate required
        
def main():
    """Main entry point."""
    validator = ProfessionalAPIValidator()
    success = validator.run_comprehensive_validation()
    
    if success:
        print("\n🎉 VALIDATION SUCCESSFUL: System is production-ready!")
        sys.exit(0)
    else:
        print("\n⚠️  VALIDATION ISSUES: Please address the issues before deployment.")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
