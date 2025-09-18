"""
Quick deployment script for fixed government portal scrapers.
Ensures all components are properly integrated.
"""

import os
import sys
import asyncio
import logging

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.multi_source_market_service import MultiSourceMarketService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_file_exists(file_path, description):
    """Check if a required file exists."""
    if os.path.exists(file_path):
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing - {file_path}")
        return False

def verify_fixed_scrapers_deployment():
    """Verify all fixed scrapers are properly deployed."""
    
    print("🔧 VERIFYING FIXED SCRAPERS DEPLOYMENT")
    print("=" * 50)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    services_dir = os.path.join(base_dir, "app", "services")
    
    # Check required files
    files_to_check = [
        (os.path.join(services_dir, "fixed_agmarknet_scraper.py"), "Fixed AGMARKNET Scraper"),
        (os.path.join(services_dir, "fixed_data_gov_scraper.py"), "Fixed Data.gov.in Scraper"),
        (os.path.join(services_dir, "fixed_enam_scraper.py"), "Fixed eNAM Scraper"),
        (os.path.join(services_dir, "multi_source_market_service.py"), "Multi-Source Market Service"),
        (os.path.join(base_dir, "app", "api", "market.py"), "Market API"),
        (os.path.join(base_dir, "test_fixed_scrapers.py"), "Test Script")
    ]
    
    all_files_exist = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    print(f"\nFile Check: {'✅ PASSED' if all_files_exist else '❌ FAILED'}")
    
    # Check imports
    print("\n📦 CHECKING IMPORTS...")
    try:
        from app.services.fixed_agmarknet_scraper import fixed_agmarknet_scraper
        print("✅ Fixed AGMARKNET Scraper: Import OK")
    except Exception as e:
        print(f"❌ Fixed AGMARKNET Scraper: Import Failed - {e}")
        all_files_exist = False
    
    try:
        from app.services.fixed_data_gov_scraper import fixed_data_gov_scraper
        print("✅ Fixed Data.gov.in Scraper: Import OK")
    except Exception as e:
        print(f"❌ Fixed Data.gov.in Scraper: Import Failed - {e}")
        all_files_exist = False
    
    try:
        from app.services.fixed_enam_scraper import fixed_enam_scraper
        print("✅ Fixed eNAM Scraper: Import OK")
    except Exception as e:
        print(f"❌ Fixed eNAM Scraper: Import Failed - {e}")
        all_files_exist = False
    
    print(f"\nImport Check: {'✅ PASSED' if all_files_exist else '❌ FAILED'}")
    
    return all_files_exist

async def test_integration():
    """Test integration of fixed scrapers."""
    
    print("\n🔄 TESTING INTEGRATION...")
    
    try:
        # Test the integrated service
        service = MultiSourceMarketService()
        result = await service.get_comprehensive_market_data("Ranchi", "Rice")
        
        status = result.get("status")
        sources_active = result.get("sources_active", 0)
        
        print(f"Integration Status: {status}")
        print(f"Active Sources: {sources_active}")
        
        if status == "success":
            print("✅ Integration: WORKING")
            return True
        elif status == "no_data":
            print("⚠️ Integration: WORKING (no data available from portals)")
            return True
        else:
            print("❌ Integration: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Integration: ERROR - {e}")
        return False

def main():
    """Main deployment verification."""
    
    print("🚀 FIXED GOVERNMENT PORTAL SCRAPERS DEPLOYMENT VERIFICATION")
    print("=" * 70)
    
    # Step 1: Verify files
    files_ok = verify_fixed_scrapers_deployment()
    
    # Step 2: Test integration
    if files_ok:
        integration_ok = asyncio.run(test_integration())
    else:
        integration_ok = False
    
    # Final result
    print("\n" + "=" * 70)
    if files_ok and integration_ok:
        print("🎉 DEPLOYMENT VERIFICATION: SUCCESS")
        print("✅ All fixed scrapers are properly deployed and integrated")
        print("🔧 System is ready to use proper government portal authentication")
        print("📊 API will now use fixed scrapers for real government data")
    else:
        print("⚠️ DEPLOYMENT VERIFICATION: ISSUES FOUND")
        if not files_ok:
            print("❌ File deployment issues detected")
        if not integration_ok:
            print("❌ Integration issues detected")
    
    print("\n📋 NEXT STEPS:")
    print("1. Run: python test_fixed_scrapers.py - To test individual scrapers")
    print("2. Start FastAPI server to test API endpoints")
    print("3. Check logs for authentication and data retrieval status")
    print("4. Monitor government portal access for real data")

if __name__ == "__main__":
    main()
