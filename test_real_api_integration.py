"""
Real API Integration Test Script
Tests all three government data sources with real API capabilities
"""

import asyncio
import os
from pathlib import Path
import sys

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.multi_source_market_service import MultiSourceMarketService

class RealAPITester:
    def __init__(self):
        self.service = MultiSourceMarketService()
        
    async def test_all_sources(self):
        """Test all three data sources for real API integration."""
        print("🧪 Testing Real API Integration for AuraFarming")
        print("=" * 60)
        
        # Test data
        test_districts = ["Ranchi", "Dhanbad", "Jamshedpur"]
        test_commodities = ["Rice", "Wheat", "Maize"]
        
        results = {}
        
        for district in test_districts:
            for commodity in test_commodities:
                print(f"\n📍 Testing: {district} - {commodity}")
                print("-" * 40)
                
                try:
                    # Get multi-source data
                    data = await self.service.get_market_data(district, commodity)
                    
                    # Analyze results
                    if data.get('status') == 'success':
                        sources = data.get('sources', {})
                        
                        print(f"✅ Multi-source data retrieved successfully")
                        print(f"📊 Sources active: {len(sources)}")
                        
                        # Check each source
                        for source_name, source_data in sources.items():
                            status = source_data.get('status', 'unknown')
                            has_note = 'note' in source_data
                            
                            if status == 'success' and not has_note:
                                print(f"  🌟 {source_name}: REAL API DATA ✅")
                            elif status == 'success' and has_note:
                                print(f"  🔄 {source_name}: Fallback data (API not accessible)")
                            else:
                                print(f"  ❌ {source_name}: Error - {status}")
                        
                        # Overall confidence
                        confidence = data.get('confidence_score', 0)
                        print(f"🎯 Confidence Score: {confidence}%")
                        
                        results[f"{district}_{commodity}"] = {
                            'status': 'success',
                            'sources': len(sources),
                            'confidence': confidence
                        }
                        
                    else:
                        print(f"❌ Failed to get data: {data.get('error', 'Unknown error')}")
                        results[f"{district}_{commodity}"] = {'status': 'failed'}
                        
                except Exception as e:
                    print(f"💥 Exception: {e}")
                    results[f"{district}_{commodity}"] = {'status': 'exception', 'error': str(e)}
        
        # Summary
        await self._print_summary(results)
        
    async def _print_summary(self, results):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📋 REAL API INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        successful_tests = len([r for r in results.values() if r.get('status') == 'success'])
        
        print(f"🧪 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {total_tests - successful_tests}")
        print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Check API credentials
        print(f"\n🔑 API Credentials Status:")
        print(f"  DATA_GOV_IN_API_KEY: {'✅ Set' if os.getenv('DATA_GOV_IN_API_KEY') else '❌ Not set'}")
        print(f"  ENAM_API_KEY: {'✅ Set' if os.getenv('ENAM_API_KEY') else '❌ Not set'}")
        print(f"  ENAM_API_SECRET: {'✅ Set' if os.getenv('ENAM_API_SECRET') else '❌ Not set'}")
        
        if not any([os.getenv('DATA_GOV_IN_API_KEY'), os.getenv('ENAM_API_KEY')]):
            print(f"\n💡 To enable REAL API data:")
            print(f"   1. Get API credentials from government portals")
            print(f"   2. Add them to your .env file") 
            print(f"   3. Re-run this test")
            print(f"   📖 See: API_CREDENTIALS_SETUP.md")
        else:
            print(f"\n🎉 Real API integration is ACTIVE!")
            
    async def test_individual_sources(self):
        """Test each source individually."""
        print("\n🔍 Testing Individual Sources")
        print("=" * 60)
        
        district = "Ranchi"
        commodity = "Rice"
        
        # Test AGMARKNET (should work without credentials)
        print(f"\n1️⃣ Testing AGMARKNET Scraper")
        try:
            agmarknet_data = await self.service._get_enhanced_agmarknet_data(district, commodity)
            if agmarknet_data.get('status') == 'success':
                has_note = 'note' in agmarknet_data
                if has_note:
                    print(f"   🔄 AGMARKNET: Using fallback data")
                else:
                    print(f"   🌟 AGMARKNET: Real scraping active ✅")
            else:
                print(f"   ❌ AGMARKNET: Failed - {agmarknet_data.get('status')}")
        except Exception as e:
            print(f"   💥 AGMARKNET: Exception - {e}")
            
        # Test Government Portal
        print(f"\n2️⃣ Testing Government Portal")
        try:
            gov_data = await self.service._get_government_portal_data(district, commodity)
            if gov_data.get('status') == 'success':
                has_note = 'note' in gov_data
                if has_note:
                    print(f"   🔄 Government Portal: Using fallback data")
                else:
                    print(f"   🌟 Government Portal: Real API active ✅")
            else:
                print(f"   ❌ Government Portal: Failed - {gov_data.get('status')}")
        except Exception as e:
            print(f"   💥 Government Portal: Exception - {e}")
            
        # Test eNAM
        print(f"\n3️⃣ Testing eNAM Integration")
        try:
            enam_data = await self.service._get_enam_data(district, commodity)
            if enam_data.get('status') == 'success':
                has_note = 'note' in enam_data
                if has_note:
                    print(f"   🔄 eNAM: Using fallback data")
                else:
                    print(f"   🌟 eNAM: Real API active ✅")
            else:
                print(f"   ❌ eNAM: Failed - {enam_data.get('status')}")
        except Exception as e:
            print(f"   💥 eNAM: Exception - {e}")

async def main():
    """Main test function."""
    tester = RealAPITester()
    
    print("🚀 AuraFarming Real API Integration Test")
    print("🎯 Testing all government data sources...")
    print()
    
    # Test all combinations
    await tester.test_all_sources()
    
    # Test individual sources
    await tester.test_individual_sources()
    
    print(f"\n🎉 Test completed!")
    print(f"📖 For API setup instructions, see: API_CREDENTIALS_SETUP.md")

if __name__ == "__main__":
    asyncio.run(main())
