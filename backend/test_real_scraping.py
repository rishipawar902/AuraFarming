"""
Test script for real government data scraping.
This tests the actual web scraping functionality.
"""

import asyncio
import sys
import os
sys.path.append(os.path.abspath('.'))

from app.services.real_government_scraper import real_government_scraper
from app.services.multi_source_market_service import MultiSourceMarketService

async def test_real_scraping():
    """Test real government data scraping."""
    
    print("🌐 Testing REAL Government Data Scraping")
    print("=" * 50)
    
    # Test district and commodity
    test_district = "Ranchi"
    test_commodity = "Rice"
    
    # Test 1: Direct real scraper
    print(f"\n1. Testing Real Government Scraper for {test_district}, {test_commodity}")
    try:
        real_data = await real_government_scraper.scrape_all_portals(test_district, test_commodity)
        
        print(f"Status: {real_data.get('status')}")
        print(f"Sources used: {real_data.get('sources_used', [])}")
        print(f"Total data points: {real_data.get('total_data_points', 0)}")
        print(f"Scraping method: {real_data.get('scraping_method')}")
        
        source_summary = real_data.get('source_summary', {})
        for source, info in source_summary.items():
            print(f"  - {source}: {info.get('status')} ({info.get('data_points', 0)} points, confidence: {info.get('confidence', 0.0)})")
        
        # Show sample data
        sample_data = real_data.get('data', [])
        if sample_data:
            print(f"\nSample Data (first 3 items):")
            for i, item in enumerate(sample_data[:3]):
                print(f"  {i+1}. {item.get('commodity')} - ₹{item.get('modal_price')} at {item.get('market')} ({item.get('source')})")
        
    except Exception as e:
        print(f"Error in real scraper: {e}")
    
    # Test 2: Multi-source service
    print(f"\n2. Testing Multi-Source Service for {test_district}")
    try:
        multi_service = MultiSourceMarketService()
        comprehensive_data = await multi_service.get_comprehensive_market_data(test_district, test_commodity)
        
        print(f"Status: {comprehensive_data.get('status')}")
        print(f"Data quality: {comprehensive_data.get('data_quality', 'Unknown')}")
        print(f"Scraping method: {comprehensive_data.get('scraping_method', 'Unknown')}")
        print(f"Sources: {comprehensive_data.get('sources', [])}")
        
        # Show comprehensive data
        market_data = comprehensive_data.get('data', [])
        if market_data:
            print(f"\nComprehensive Data ({len(market_data)} items):")
            for i, item in enumerate(market_data[:5]):
                print(f"  {i+1}. {item.get('commodity')} - ₹{item.get('modal_price')} at {item.get('market')} ({item.get('source')})")
        
    except Exception as e:
        print(f"Error in multi-source service: {e}")
    
    # Test 3: Test all districts
    print(f"\n3. Testing Multiple Districts")
    test_districts = ["Ranchi", "Dhanbad", "Jamshedpur"]
    
    for district in test_districts:
        try:
            print(f"\nTesting {district}...")
            data = await real_government_scraper.scrape_all_portals(district, None)
            
            status = data.get('status')
            data_points = data.get('total_data_points', 0)
            sources = data.get('sources_used', [])
            
            print(f"  {district}: {status} - {data_points} data points from {len(sources)} sources")
            
        except Exception as e:
            print(f"  {district}: Error - {e}")
    
    # Clean up
    await real_government_scraper.close()
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_real_scraping())
