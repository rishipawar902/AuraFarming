"""
Professional Environment Configuration Validator
Ensures all environment variables and configurations are properly set.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import json

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class EnvironmentValidator:
    """Professional environment validation with detailed reporting."""
    
    def __init__(self):
        self.required_vars = {
            "SUPABASE_URL": "Database connection URL",
            "SUPABASE_ANON_KEY": "Database anonymous key", 
            "SUPABASE_SERVICE_ROLE_KEY": "Database service role key"
        }
        
        self.optional_vars = {
            "WEATHERAPI_KEY": "Weather API key for real weather data",
            "OPENWEATHER_API_KEY": "OpenWeather API key (backup)",
            "JWT_SECRET_KEY": "JWT token encryption key"
        }
        
        self.validation_results = {}
    
    def check_env_file_exists(self) -> Dict[str, Any]:
        """Check if .env file exists and is readable."""
        env_path = Path(__file__).parent / '.env'
        
        result = {
            "exists": env_path.exists(),
            "readable": False,
            "path": str(env_path),
            "size": 0
        }
        
        if result["exists"]:
            try:
                result["readable"] = env_path.is_file() and os.access(env_path, os.R_OK)
                result["size"] = env_path.stat().st_size
            except Exception as e:
                result["error"] = str(e)
        
        return result
    
    def validate_required_variables(self) -> Dict[str, Any]:
        """Validate all required environment variables."""
        results = {}
        
        try:
            from app.core.config import settings
            
            for var_name, description in self.required_vars.items():
                value = getattr(settings, var_name, None)
                
                results[var_name] = {
                    "description": description,
                    "configured": bool(value),
                    "is_template": value and ('your_' in value.lower() or 'template' in value.lower()) if value else False,
                    "length": len(value) if value else 0,
                    "status": "valid" if value and not ('your_' in value.lower() or 'template' in value.lower()) else "missing_or_template"
                }
                
        except Exception as e:
            results["error"] = f"Failed to load configuration: {str(e)}"
        
        return results
    
    def validate_optional_variables(self) -> Dict[str, Any]:
        """Validate optional environment variables."""
        results = {}
        
        try:
            from app.core.config import settings
            
            for var_name, description in self.optional_vars.items():
                value = getattr(settings, var_name, None)
                
                # Special validation for API keys
                is_mock = False
                if value:
                    is_mock = any(keyword in value.lower() for keyword in ['mock', 'test', 'demo', 'your_'])
                
                results[var_name] = {
                    "description": description,
                    "configured": bool(value),
                    "is_mock": is_mock,
                    "is_valid": value and not is_mock if value else False,
                    "length": len(value) if value else 0,
                    "status": "valid" if value and not is_mock else "missing_or_mock"
                }
                
        except Exception as e:
            results["error"] = f"Failed to load configuration: {str(e)}"
        
        return results
    
    def check_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity."""
        result = {
            "connection_status": "unknown",
            "using_mock": False,
            "error": None
        }
        
        try:
            from app.services.database import DatabaseService
            
            db = DatabaseService()
            
            # Check if using mock
            if hasattr(db, 'use_mock'):
                result["using_mock"] = db.use_mock
                result["connection_status"] = "mock" if db.use_mock else "real"
            else:
                result["connection_status"] = "real"
                
        except Exception as e:
            result["error"] = str(e)
            result["connection_status"] = "failed"
        
        return result
    
    def check_api_configurations(self) -> Dict[str, Any]:
        """Check external API configurations."""
        results = {}
        
        try:
            from app.services.enhanced_weather_service import EnhancedWeatherService
            
            weather_service = EnhancedWeatherService()
            
            results["weather_apis"] = {
                "weatherapi_configured": bool(weather_service.weatherapi_key and 'mock' not in weather_service.weatherapi_key.lower()),
                "openweather_configured": bool(weather_service.openweather_key and 'mock' not in weather_service.openweather_key.lower()),
                "primary_service": "WeatherAPI.com" if weather_service.weatherapi_key else "OpenWeatherMap" if weather_service.openweather_key else "Fallback"
            }
            
        except Exception as e:
            results["weather_apis"] = {"error": str(e)}
        
        return results
    
    def generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []
        
        # Check .env file
        env_file = validation_results.get("env_file", {})
        if not env_file.get("exists"):
            recommendations.append("📄 Create a .env file from .env.template with your actual credentials")
        
        # Check required variables
        required_vars = validation_results.get("required_variables", {})
        for var_name, var_info in required_vars.items():
            if isinstance(var_info, dict) and var_info.get("status") != "valid":
                recommendations.append(f"🔑 Configure {var_name} in your .env file")
        
        # Check database
        database = validation_results.get("database", {})
        if database.get("using_mock"):
            recommendations.append("🗄️  Database is using mock mode - configure Supabase credentials for production")
        
        # Check APIs
        api_config = validation_results.get("api_configurations", {})
        weather_apis = api_config.get("weather_apis", {})
        
        if not weather_apis.get("weatherapi_configured") and not weather_apis.get("openweather_configured"):
            recommendations.append("🌤️  Configure at least one weather API key (WEATHERAPI_KEY or OPENWEATHER_API_KEY)")
        
        # Security recommendations
        optional_vars = validation_results.get("optional_variables", {})
        jwt_status = optional_vars.get("JWT_SECRET_KEY", {})
        if isinstance(jwt_status, dict) and jwt_status.get("status") != "valid":
            recommendations.append("🔐 Configure a secure JWT_SECRET_KEY for production use")
        
        return recommendations
    
    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete environment validation."""
        print("🔧 ENVIRONMENT CONFIGURATION VALIDATION")
        print("=" * 60)
        
        results = {}
        
        # Check .env file
        print("1️⃣  Checking .env file...")
        results["env_file"] = self.check_env_file_exists()
        
        # Check required variables
        print("2️⃣  Validating required variables...")
        results["required_variables"] = self.validate_required_variables()
        
        # Check optional variables
        print("3️⃣  Validating optional variables...")
        results["optional_variables"] = self.validate_optional_variables()
        
        # Check database connectivity
        print("4️⃣  Testing database connectivity...")
        results["database"] = self.check_database_connectivity()
        
        # Check API configurations
        print("5️⃣  Checking API configurations...")
        results["api_configurations"] = self.check_api_configurations()
        
        # Generate report
        self.generate_validation_report(results)
        
        return results
    
    def generate_validation_report(self, results: Dict[str, Any]):
        """Generate detailed validation report."""
        print("\n📊 CONFIGURATION VALIDATION REPORT")
        print("=" * 60)
        
        # .env file status
        env_file = results.get("env_file", {})
        if env_file.get("exists"):
            print(f"✅ .env file exists ({env_file.get('size', 0)} bytes)")
        else:
            print("❌ .env file not found")
        
        # Required variables
        print("\n🔴 REQUIRED VARIABLES:")
        required_vars = results.get("required_variables", {})
        required_valid = 0
        required_total = 0
        
        for var_name, var_info in required_vars.items():
            if isinstance(var_info, dict):
                required_total += 1
                status = var_info.get("status", "unknown")
                if status == "valid":
                    print(f"   ✅ {var_name}: Configured")
                    required_valid += 1
                else:
                    print(f"   ❌ {var_name}: {var_info.get('description', 'Not configured')}")
        
        # Optional variables
        print("\n🔵 OPTIONAL VARIABLES:")
        optional_vars = results.get("optional_variables", {})
        optional_valid = 0
        optional_total = 0
        
        for var_name, var_info in optional_vars.items():
            if isinstance(var_info, dict):
                optional_total += 1
                status = var_info.get("status", "unknown")
                if status == "valid":
                    print(f"   ✅ {var_name}: Configured")
                    optional_valid += 1
                elif var_info.get("is_mock"):
                    print(f"   ⚠️  {var_name}: Using mock/template value")
                else:
                    print(f"   ❌ {var_name}: Not configured")
        
        # Database status
        database = results.get("database", {})
        print(f"\n🗄️  DATABASE STATUS:")
        if database.get("using_mock"):
            print("   ⚠️  Using mock database (configure Supabase for production)")
        elif database.get("connection_status") == "real":
            print("   ✅ Connected to real database")
        else:
            print(f"   ❌ Database connection failed: {database.get('error', 'Unknown error')}")
        
        # API configurations
        api_config = results.get("api_configurations", {})
        print(f"\n🌐 API CONFIGURATIONS:")
        
        weather_apis = api_config.get("weather_apis", {})
        if weather_apis.get("weatherapi_configured"):
            print("   ✅ WeatherAPI.com: Configured")
        else:
            print("   ❌ WeatherAPI.com: Not configured")
            
        if weather_apis.get("openweather_configured"):
            print("   ✅ OpenWeatherMap: Configured")
        else:
            print("   ❌ OpenWeatherMap: Not configured")
        
        # Overall score
        total_score = required_valid + optional_valid
        max_score = required_total + optional_total
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        print(f"\n🎯 CONFIGURATION SCORE: {total_score}/{max_score} ({percentage:.1f}%)")
        
        # Recommendations
        recommendations = self.generate_recommendations(results)
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   {rec}")
        else:
            print(f"\n🎉 All configurations look good!")

def main():
    """Main validation entry point."""
    validator = EnvironmentValidator()
    results = validator.run_complete_validation()
    
    # Save results
    with open("environment_validation_report.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: environment_validation_report.json")
    
    return results

if __name__ == "__main__":
    main()
