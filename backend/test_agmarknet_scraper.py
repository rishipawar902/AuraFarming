#!/usr/bin/env python3
"""
Test the AGMARKNET scraper directly.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.agmarknet_scraper import agmarknet_scraper

async def test_agmarknet_scraper():
    """Test the AGMARKNET scraper functionality."""
    
    print("🌾 Testing AGMARKNET Scraper for Jharkhand Market Data")
    print("=" * 60)
    
    # Test 1: Get data for Ranchi district
    print("\n📍 Test 1: Getting market data for Ranchi district...")
    try:
        ranchi_data = await agmarknet_scraper.get_market_data("Ranchi", days=7)
        
        print(f"Status: {ranchi_data.get('status')}")
        print(f"District: {ranchi_data.get('district')}")
        
        if ranchi_data.get('data'):
            print(f"✅ Found {len(ranchi_data['data'])} market entries")
            
            # Show first entry as example
            if ranchi_data['data']:
                first_entry = ranchi_data['data'][0]
                print(f"   Sample: {first_entry['commodity']} - ₹{first_entry['modal_price']}/qtl")
                print(f"   Market: {first_entry['market']}")
                print(f"   Date: {first_entry['date']}")
                print(f"   Trend: {first_entry['trend']}")
        else:
            print("ℹ️ Using fallback data (AGMARKNET site may be inaccessible)")
            
    except Exception as e:
        print(f"❌ Error testing Ranchi data: {e}")
    
    # Test 2: Get data for specific crop (Rice)
    print("\n🌾 Test 2: Getting Rice prices across districts...")
    try:
        rice_data = await agmarknet_scraper.get_market_data("Dhanbad", "Rice", days=7)
        
        print(f"Status: {rice_data.get('status')}")
        if rice_data.get('data'):
            print(f"✅ Found {len(rice_data['data'])} rice entries")
            
            for entry in rice_data['data'][:3]:  # Show first 3 entries
                print(f"   {entry['commodity']} ({entry['variety']}) - ₹{entry['modal_price']}/qtl")
        else:
            print("ℹ️ Using fallback rice data")
            
    except Exception as e:
        print(f"❌ Error testing Rice data: {e}")
    
    # Test 3: Get data for multiple districts
    print("\n🗺️ Test 3: Getting data for multiple major districts...")
    try:
        all_districts_data = await agmarknet_scraper.get_all_districts_data("Wheat")
        
        print(f"Status: {all_districts_data.get('status')}")
        print(f"Total districts: {all_districts_data.get('total_districts')}")
        
        if all_districts_data.get('data'):
            for district, data in all_districts_data['data'].items():
                status = data.get('status', 'unknown')
                crop_count = len(data.get('data', [])) if data.get('data') else 0
                print(f"   {district}: {status} ({crop_count} entries)")
        
    except Exception as e:
        print(f"❌ Error testing multiple districts: {e}")
    
    print("\n🎉 AGMARKNET Scraper testing completed!")
    print("\nNOTE: If you see 'fallback data' messages, it means:")
    print("1. The AGMARKNET website might be temporarily inaccessible")
    print("2. The website structure might have changed")
    print("3. The scraper will use realistic mock data as backup")

if __name__ == "__main__":
    asyncio.run(test_agmarknet_scraper())
