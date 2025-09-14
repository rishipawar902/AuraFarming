"""
Temporary development configuration for testing without real Supabase credentials.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_supabase_config():
    """Check if Supabase is properly configured."""
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
    
    # Check if we have real credentials (not the placeholder ones)
    has_real_credentials = (
        supabase_url and 
        supabase_key and 
        not supabase_url.startswith("https://your-project-ref") and
        supabase_key != "your_supabase_anon_key_here"
    )
    
    return has_real_credentials

def create_mock_database_service():
    """Create a mock database service for development."""
    
    class MockDatabaseService:
        def __init__(self):
            # Mock data storage
            self.farmers = {}
            self.farms = {}
            self.recommendations = {}
            
            # Add demo data
            demo_farmer_id = "demo-farmer-123"
            demo_farm_id = "demo-farm-456"
            
            self.farmers[demo_farmer_id] = {
                "id": demo_farmer_id,
                "name": "Demo Farmer",
                "phone": "9876543210",
                "password": "hashed_password_demo",
                "language": "english",
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            self.farms[demo_farm_id] = {
                "id": demo_farm_id,
                "farmer_id": demo_farmer_id,
                "location": {
                    "latitude": 23.3441,
                    "longitude": 85.3096,
                    "district": "Ranchi",
                    "village": "Demo Village"
                },
                "soil_type": "loam",
                "irrigation_method": "drip",
                "field_size": 2.5,
                "created_at": "2024-01-01T00:00:00Z"
            }
        
        async def get_farmer_by_phone(self, phone: str):
            for farmer in self.farmers.values():
                if farmer.get("phone") == phone:
                    return farmer
            return None
        
        async def create_farmer(self, farmer_data):
            farmer_id = f"farmer-{len(self.farmers) + 1}"
            farmer_data["id"] = farmer_id
            self.farmers[farmer_id] = farmer_data
            return farmer_data
        
        async def get_farm_by_farmer_id(self, farmer_id: str):
            for farm in self.farms.values():
                if farm.get("farmer_id") == farmer_id:
                    return farm
            return None
        
        async def create_farm(self, farm_data):
            farm_id = f"farm-{len(self.farms) + 1}"
            farm_data["id"] = farm_id
            self.farms[farm_id] = farm_data
            return farm_data
        
        async def update_farm(self, farm_id: str, farm_data):
            if farm_id in self.farms:
                self.farms[farm_id].update(farm_data)
                return self.farms[farm_id]
            return farm_data
        
        async def create_recommendation(self, recommendation_data):
            rec_id = f"rec-{len(self.recommendations) + 1}"
            recommendation_data["id"] = rec_id
            self.recommendations[rec_id] = recommendation_data
            return recommendation_data
        
        async def get_recommendations_by_farm_id(self, farm_id: str):
            return [rec for rec in self.recommendations.values() if rec.get("farm_id") == farm_id]
    
    return MockDatabaseService()

# Export the function to check config
__all__ = ["check_supabase_config", "create_mock_database_service"]