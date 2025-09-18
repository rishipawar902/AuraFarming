"""
Test script for fixed government portal scrapers.
Tests proper authentication and data retrieval.
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.fixed_agmarknet_scraper import fixed_agmarknet_scraper
from app.services.fixed_data_gov_scraper import fixed_data_gov_scraper  
from app.services.fixed_enam_scraper import fixed_enam_scraper
from app.services.multi_source_market_service import MultiSourceMarketService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_fixed_scrapers():
    """Test all fixed government portal scrapers."""
    
    print("🔧 TESTING FIXED GOVERNMENT PORTAL SCRAPERS")
    print("=" * 60)
    
    test_district = "Ranchi"
    test_commodity = "Rice"
    
    # Test 1: Fixed AGMARKNET Scraper
    print("\n🌾 Testing Fixed AGMARKNET Scraper...")
    try:
        agmarknet_result = await fixed_agmarknet_scraper.get_market_data(test_district, test_commodity)
        print(f"AGMARKNET Status: {agmarknet_result.get('status')}")
        if agmarknet_result.get('status') == 'success':
            data = agmarknet_result.get('data', [])
            print(f"AGMARKNET Data: {len(data)} records found")
            if data:
                print(f"Sample: {data[0]}")
        else:
            print(f"AGMARKNET Message: {agmarknet_result.get('message')}")
    except Exception as e:
        print(f"AGMARKNET Error: {e}")
    
    print("-" * 40)
    
    # Test 2: Fixed Data.gov.in Scraper
    print("\n🏛️ Testing Fixed Data.gov.in Scraper...")
    try:
        data_gov_result = await fixed_data_gov_scraper.get_market_data(test_district, test_commodity)
        print(f"Data.gov.in Status: {data_gov_result.get('status')}")
        if data_gov_result.get('status') == 'success':
            data = data_gov_result.get('data', [])
            print(f"Data.gov.in Data: {len(data)} records found")
            if data:
                print(f"Sample: {data[0]}")
        else:
            print(f"Data.gov.in Message: {data_gov_result.get('message')}")
    except Exception as e:
        print(f"Data.gov.in Error: {e}")
    
    print("-" * 40)
    
    # Test 3: Fixed eNAM Scraper
    print("\n🚜 Testing Fixed eNAM Scraper...")
    try:
        enam_result = await fixed_enam_scraper.get_market_data(test_district, test_commodity)
        print(f"eNAM Status: {enam_result.get('status')}")
        if enam_result.get('status') == 'success':
            data = enam_result.get('data', [])
            print(f"eNAM Data: {len(data)} records found")
            if data:
                print(f"Sample: {data[0]}")
        else:
            print(f"eNAM Message: {enam_result.get('message')}")
    except Exception as e:
        print(f"eNAM Error: {e}")
    
    print("-" * 40)
    
    # Test 4: Integrated Multi-Source Service
    print("\n🔄 Testing Integrated Multi-Source Service...")
    try:
        multi_service = MultiSourceMarketService()
        integrated_result = await multi_service.get_comprehensive_market_data(test_district, test_commodity)
        
        print(f"Integrated Status: {integrated_result.get('status')}")
        print(f"Total Prices: {integrated_result.get('total_prices_found', 0)}")
        print(f"Active Sources: {integrated_result.get('sources_active', 0)}")
        
        source_summary = integrated_result.get('source_summary', {})
        print(f"Source Summary:")
        for source, info in source_summary.items():
            status = info.get('status', 'unknown')
            count = info.get('count', 0)
            print(f"  - {source}: {status} ({count} records)")
        
        if integrated_result.get('status') == 'success':
            data = integrated_result.get('real_time_data', [])
            if data:
                print(f"Sample integrated data: {data[0]}")
        
    except Exception as e:
        print(f"Integrated Service Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 FIXED SCRAPERS TEST COMPLETE")

async def test_specific_fixes():
    """Test specific fixes in the scrapers."""
    
    print("\n🔍 TESTING SPECIFIC FIXES")
    print("=" * 40)
    
    # Test AGMARKNET form submission
    print("\n📝 Testing AGMARKNET form submission...")
    try:
        result = await fixed_agmarknet_scraper._try_form_submission("Ranchi", "Rice")
        print(f"Form submission result: {result.get('status')}")
    except Exception as e:
        print(f"Form submission error: {e}")
    
    # Test Data.gov.in API endpoints
    print("\n🔗 Testing Data.gov.in API endpoints...")
    try:
        result = await fixed_data_gov_scraper._try_catalog_api("Ranchi", "Rice")
        print(f"Catalog API result: {result.get('status')}")
    except Exception as e:
        print(f"Catalog API error: {e}")
    
    # Test eNAM dashboard API
    print("\n📊 Testing eNAM dashboard API...")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            result = await fixed_enam_scraper._try_dashboard_api(client, "Ranchi", "Rice")
            print(f"Dashboard API result: {result.get('status')}")
    except Exception as e:
        print(f"Dashboard API error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Fixed Government Portal Scrapers Test")
    
    # Run main tests
    asyncio.run(test_fixed_scrapers())
    
    # Run specific fix tests  
    asyncio.run(test_specific_fixes())
    
    print("\n✅ All tests completed!")
