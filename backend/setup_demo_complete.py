#!/usr/bin/env python3
"""
Find existing demo farmer and set up farm profile if needed
"""

import asyncio
import sys
import os
import uuid

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.database import DatabaseService
from app.models.schemas import SoilTypeEnum, IrrigationMethodEnum

async def find_and_setup_demo_data():
    """Find existing demo farmer and set up farm if needed"""
    
    print("🔍 Finding existing demo farmer and setting up farm profile...")
    print("=" * 70)
    
    demo_phone = "9876543210"
    
    try:
        db = DatabaseService()
        print(f"✓ DatabaseService created, using mock: {db.use_mock}")
        
        # Step 1: Find existing farmer by phone
        print(f"\n1. Finding existing farmer with phone: {demo_phone}")
        
        # First get all farmers to find the one with our phone number
        try:
            result = db.supabase.table("farmers").select("*").eq("phone", demo_phone).execute()
            if result.data:
                existing_farmer = result.data[0]
                farmer_id = existing_farmer['id']
                print(f"   ✅ Found existing farmer!")
                print(f"   👤 Farmer ID: {farmer_id}")
                print(f"   📝 Name: {existing_farmer['name']}")
                print(f"   📱 Phone: {existing_farmer['phone']}")
            else:
                print("   ❌ No farmer found with this phone number")
                return False
        except Exception as e:
            print(f"   ❌ Error finding farmer: {e}")
            return False
        
        # Step 2: Check if farm exists for this farmer
        print(f"\n2. Checking if farm exists for farmer: {farmer_id}")
        
        existing_farm = await db.get_farm_by_farmer_id(farmer_id)
        if existing_farm:
            print("   ✅ Farm already exists!")
            print(f"   🏡 Farm ID: {existing_farm['id']}")
            print(f"   📍 Location: {existing_farm['location']['district']}")
            print(f"   🌱 Soil: {existing_farm['soil_type']}")
            print(f"   💧 Irrigation: {existing_farm['irrigation_method']}")
            print(f"   📏 Size: {existing_farm['field_size']} acres")
        else:
            print("   ❌ No farm found - creating one...")
            
            # Create farm profile
            demo_farm_data = {
                "id": str(uuid.uuid4()),
                "farmer_id": farmer_id,
                "location": {
                    "latitude": 23.3441,
                    "longitude": 85.3096,
                    "district": "Ranchi",
                    "village": "Demo Village"
                },
                "soil_type": SoilTypeEnum.RED_SOIL.value,
                "irrigation_method": IrrigationMethodEnum.TUBE_WELL.value,
                "field_size": 2.5
            }
            
            created_farm = await db.create_farm(demo_farm_data)
            print(f"   ✅ Created farm: {created_farm['id']}")
            print(f"   📍 Location: Ranchi, Demo Village")
            print(f"   🌱 Soil: {demo_farm_data['soil_type']}")
            print(f"   💧 Irrigation: {demo_farm_data['irrigation_method']}")
            print(f"   📏 Size: {demo_farm_data['field_size']} acres")
        
        # Step 3: Test the complete flow
        print(f"\n3. Testing complete flow...")
        
        # Test farm retrieval
        test_farm = await db.get_farm_by_farmer_id(farmer_id)
        if test_farm:
            print(f"   ✅ Farm retrieval works! Farm ID: {test_farm['id']}")
        else:
            print("   ❌ Farm retrieval failed!")
            return False
        
        print(f"\n🎉 Demo setup complete!")
        print(f"📱 Demo credentials:")
        print(f"   Phone: {demo_phone}")
        print(f"   Password: demo123")
        print(f"👤 Farmer ID: {farmer_id}")
        print(f"🏡 Farm ID: {test_farm['id']}")
        
        return farmer_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏗️  DEMO DATA VERIFICATION & SETUP")
    
    farmer_id = asyncio.run(find_and_setup_demo_data())
    
    if farmer_id:
        print(f"\n✅ SUCCESS! Demo farmer ready with ID: {farmer_id}")
        print("🧪 Now test login at: http://localhost:3000")
    else:
        print("\n❌ FAILED! Check the errors above.")