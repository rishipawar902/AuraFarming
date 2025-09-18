#!/usr/bin/env python3
"""
🔍 AuraFarming API Issues Diagnostic Tool
=========================================

Diagnoses and identifies any issues with the API endpoints.
"""

import requests
import json
import asyncio

def print_banner():
    print("🔍 AuraFarming: API Issues Diagnostic Tool")
    print("=" * 55)
    print("🎯 Identifying and diagnosing API issues")
    print("🏥 Health check and endpoint validation")
    print("=" * 55)

async def diagnose_api_issues():
    """Diagnose API issues systematically."""
    
    print_banner()
    
    base_url = "http://localhost:8000"
    issues_found = []
    
    print("\n🏥 Step 1: Server Health Check")
    print("-" * 35)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Server is healthy and running")
            print(f"   📊 Status: {health_data['status']}")
            print(f"   🌐 Environment: {health_data['environment']}")
            print(f"   🐛 Debug mode: {health_data['debug']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            issues_found.append(f"Health check failed with status {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        issues_found.append("Server connection failed")
        return issues_found
    
    print("\n📖 Step 2: API Documentation Check")
    print("-" * 35)
    
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API documentation is accessible")
            print(f"   🌐 URL: {base_url}/docs")
        else:
            print(f"❌ Documentation not accessible: {response.status_code}")
            issues_found.append("API documentation not accessible")
    except requests.RequestException as e:
        print(f"❌ Documentation check failed: {e}")
        issues_found.append("Documentation access failed")
    
    print("\n🌐 Step 3: API Schema Validation")
    print("-" * 35)
    
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get('paths', {})
            
            finance_endpoints = [path for path in paths.keys() if '/finance/' in path]
            auth_endpoints = [path for path in paths.keys() if '/auth/' in path]
            
            print(f"✅ OpenAPI schema loaded successfully")
            print(f"   📊 Total endpoints: {len(paths)}")
            print(f"   💰 Finance endpoints: {len(finance_endpoints)}")
            print(f"   🔐 Auth endpoints: {len(auth_endpoints)}")
            
            if not finance_endpoints:
                print("❌ No finance endpoints found in schema")
                issues_found.append("Finance endpoints missing from schema")
            else:
                print("✅ Finance endpoints found in schema:")
                for endpoint in finance_endpoints[:3]:  # Show first 3
                    print(f"      🌐 {endpoint}")
                if len(finance_endpoints) > 3:
                    print(f"      ... and {len(finance_endpoints) - 3} more")
                    
        else:
            print(f"❌ Schema not accessible: {response.status_code}")
            issues_found.append("OpenAPI schema not accessible")
    except requests.RequestException as e:
        print(f"❌ Schema check failed: {e}")
        issues_found.append("Schema validation failed")
    
    print("\n🔐 Step 4: Authentication Check")
    print("-" * 30)
    
    # Test authentication endpoints
    auth_tests = [
        {"path": "/api/v1/auth/register", "method": "POST", "expect": [422, 400]},  # Validation error expected
        {"path": "/api/v1/auth/login", "method": "POST", "expect": [422, 400]},     # Validation error expected
    ]
    
    for test in auth_tests:
        try:
            if test["method"] == "POST":
                response = requests.post(f"{base_url}{test['path']}", json={}, timeout=5)
            else:
                response = requests.get(f"{base_url}{test['path']}", timeout=5)
                
            if response.status_code in test["expect"]:
                print(f"✅ {test['path']} - Endpoint exists (status: {response.status_code})")
            elif response.status_code == 404:
                print(f"❌ {test['path']} - Endpoint not found")
                issues_found.append(f"Auth endpoint {test['path']} not found")
            else:
                print(f"⚠️ {test['path']} - Unexpected status: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"❌ {test['path']} - Request failed: {e}")
            issues_found.append(f"Auth endpoint {test['path']} failed")
    
    print("\n💰 Step 5: Finance Endpoints Check")
    print("-" * 35)
    
    # Test finance endpoints (without auth - expect 403/401)
    finance_tests = [
        "/api/v1/finance/recommendations",
        "/api/v1/finance/profile/comprehensive", 
        "/api/v1/finance/pm-kisan/status",
        "/api/v1/finance/loans/products",
        "/api/v1/finance/health-score"
    ]
    
    for endpoint in finance_tests:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code in [401, 403]:
                print(f"✅ {endpoint} - Endpoint exists, auth required (status: {response.status_code})")
            elif response.status_code == 404:
                print(f"❌ {endpoint} - Endpoint not found")
                issues_found.append(f"Finance endpoint {endpoint} not found")
            elif response.status_code == 422:
                print(f"✅ {endpoint} - Endpoint exists, validation error (status: {response.status_code})")
            else:
                print(f"⚠️ {endpoint} - Unexpected status: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"❌ {endpoint} - Request failed: {e}")
            issues_found.append(f"Finance endpoint {endpoint} failed")
    
    print("\n📦 Step 6: Service Import Check")
    print("-" * 30)
    
    # Test if services can be imported
    import_tests = [
        ("Enhanced Finance Service", "from app.services.enhanced_finance_service import enhanced_finance_service"),
        ("Finance Router", "from app.api.finance import finance_router"),
        ("Database Service", "from app.services.database import DatabaseService"),
        ("Weather Service", "from app.services.weather_service import WeatherService"),
    ]
    
    for service_name, import_cmd in import_tests:
        try:
            exec(import_cmd)
            print(f"✅ {service_name} - Import successful")
        except Exception as e:
            print(f"❌ {service_name} - Import failed: {e}")
            issues_found.append(f"{service_name} import failed")
    
    print("\n🧪 Step 7: Enhanced Finance Service Test")
    print("-" * 40)
    
    try:
        # Import and test the enhanced finance service
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from app.services.enhanced_finance_service import enhanced_finance_service
        
        # Test sample data
        test_farmer = {
            "farmer_id": "TEST001",
            "name": "Test Farmer",
            "age": 35,
            "location": {"district": "Ranchi", "state": "Jharkhand"}
        }
        
        test_farm = {
            "farm_id": "TESTFM001",
            "total_area": 2.0,
            "crops": [{"crop_type": "Rice", "area": 2.0}]
        }
        
        # Test financial profile generation
        financial_profile = await enhanced_finance_service.get_comprehensive_financial_profile(
            test_farmer, test_farm
        )
        
        print("✅ Enhanced finance service working correctly")
        print(f"   📊 Financial health score: {financial_profile['financial_health_score']['score']}/100")
        print(f"   🏦 Loan products: {len(financial_profile['loan_products'])}")
        print(f"   💡 Investment opportunities: {len(financial_profile['investment_opportunities'])}")
        
    except Exception as e:
        print(f"❌ Enhanced finance service test failed: {e}")
        issues_found.append(f"Enhanced finance service test failed: {str(e)}")
    
    print("\n📋 Issues Summary")
    print("=" * 55)
    
    if not issues_found:
        print("🎉 NO ISSUES FOUND! All systems are working correctly!")
        print("\n✅ All checks passed:")
        print("   🏥 Server health - OK")
        print("   📖 API documentation - Accessible")
        print("   🌐 OpenAPI schema - Valid")
        print("   🔐 Authentication endpoints - Available")
        print("   💰 Finance endpoints - Available (auth required)")
        print("   📦 Service imports - Working")
        print("   🧪 Enhanced finance service - Functional")
        
        print(f"\n📚 API Documentation: {base_url}/docs")
        print(f"🏥 Health Check: {base_url}/health")
        
        print("\n💡 If you're experiencing issues, they might be:")
        print("   🔐 Authentication required for protected endpoints")
        print("   📱 Frontend-backend connection issues")
        print("   🌐 CORS configuration for frontend access")
        
    else:
        print(f"❌ {len(issues_found)} ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 Recommended Actions:")
        for issue in issues_found:
            if "not found" in issue.lower():
                print(f"   🔍 Check route registration for: {issue}")
            elif "import failed" in issue.lower():
                print(f"   📦 Check module dependencies for: {issue}")
            elif "connection" in issue.lower():
                print(f"   🌐 Check server startup for: {issue}")
    
    return issues_found

if __name__ == "__main__":
    asyncio.run(diagnose_api_issues())
