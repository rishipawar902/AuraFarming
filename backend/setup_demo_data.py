#!/usr/bin/env python3
"""
Pre-populate Supabase database with demo farmer and farm profile data
"""

import asyncio
import sys
import os
import uuid

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.database import DatabaseService
from app.models.schemas import SoilTypeEnum, IrrigationMethodEnum

async def setup_demo_data():
    """Set up demo farmer and farm data in the database"""
    
    print("🚀 Setting up demo data in Supabase database...")
    print("=" * 60)
    
    # Demo farmer data - Use a fixed UUID for consistency
    demo_farmer_id = "12345678-1234-5678-9012-123456789012"  # Fixed demo UUID
    demo_phone = "9876543210"
    
    try:
        db = DatabaseService()
        print(f"✓ DatabaseService created, using mock: {db.use_mock}")
        
        if db.use_mock:
            print("⚠️  Using mock database - demo data will be in memory only")
        
        # Step 1: Create demo farmer
        print(f"\n1. Creating demo farmer...")
        print(f"   Farmer ID: {demo_farmer_id}")
        print(f"   Phone: {demo_phone}")
        
        # Check if farmer already exists
        existing_farmer = await db.get_farmer_by_id(demo_farmer_id)
        if existing_farmer:
            print("   ✓ Demo farmer already exists - skipping creation")
        else:
            farmer_data = {
                "id": demo_farmer_id,
                "name": "Demo Farmer",
                "phone": demo_phone,
                "password": "demo123",  # In production, this should be hashed
                "language": "english"
            }
            
            created_farmer = await db.create_farmer(farmer_data)
            print(f"   ✅ Created demo farmer: {created_farmer['id']}")
        
        # Step 2: Create demo farm profile
        print(f"\n2. Creating demo farm profile...")
        
        # Check if farm already exists
        existing_farm = await db.get_farm_by_farmer_id(demo_farmer_id)
        if existing_farm:
            print("   ✓ Demo farm already exists - skipping creation")
            print(f"   ✓ Existing farm ID: {existing_farm['id']}")
        else:
            demo_farm_data = {
                "id": str(uuid.uuid4()),
                "farmer_id": demo_farmer_id,
                "location": {
                    "latitude": 23.3441,  # Ranchi coordinates
                    "longitude": 85.3096,
                    "district": "Ranchi",
                    "village": "Demo Village"
                },
                "soil_type": SoilTypeEnum.RED_SOIL.value,
                "irrigation_method": IrrigationMethodEnum.TUBE_WELL.value,
                "field_size": 2.5
            }
            
            created_farm = await db.create_farm(demo_farm_data)
            print(f"   ✅ Created demo farm: {created_farm['id']}")
            print(f"   📍 Location: {demo_farm_data['location']['district']}, {demo_farm_data['location']['village']}")
            print(f"   🌱 Soil: {demo_farm_data['soil_type']}")
            print(f"   💧 Irrigation: {demo_farm_data['irrigation_method']}")
            print(f"   📏 Size: {demo_farm_data['field_size']} acres")
        
        # Step 3: Verify data can be retrieved
        print(f"\n3. Verifying demo data...")
        
        # Test farmer retrieval
        farmer = await db.get_farmer_by_id(demo_farmer_id)
        if farmer:
            print(f"   ✅ Can retrieve farmer: {farmer['name']} ({farmer['phone']})")
        else:
            print("   ❌ Cannot retrieve farmer")
            return False
        
        # Test farm retrieval
        farm = await db.get_farm_by_farmer_id(demo_farmer_id)
        if farm:
            print(f"   ✅ Can retrieve farm: {farm['location']['district']}")
            print(f"   ✅ Farm ID: {farm['id']}")
        else:
            print("   ❌ Cannot retrieve farm")
            return False
        
        print(f"\n🎉 Demo data setup complete!")
        print(f"📱 Demo phone number: {demo_phone}")
        print(f"🔑 Demo password: demo123")
        print(f"👤 Demo farmer ID: {demo_farmer_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up demo data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏗️  DEMO DATA SETUP")
    print("Setting up demo farmer and farm profile in Supabase...")
    
    success = asyncio.run(setup_demo_data())
    
    if success:
        print("\n✅ SUCCESS! Demo data is ready.")
        print("🧪 You can now test login with:")
        print("   Phone: 9876543210")
        print("   Password: demo123")
    else:
        print("\n❌ FAILED! Check the errors above.")