"""
Database service for Supabase integration.
"""

from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import json
import uuid
import os
from app.core.config import settings


class DatabaseService:
    """
    Database service for handling all database operations using Supabase.
    Falls back to mock service if Supabase credentials are not configured.
    """
    
    def __init__(self):
        """Initialize Supabase client or mock service."""
        # Check if we have real Supabase credentials
        has_real_credentials = (
            settings.SUPABASE_URL and 
            settings.SUPABASE_ANON_KEY and 
            not settings.SUPABASE_URL.startswith("https://your-project-ref") and
            settings.SUPABASE_ANON_KEY != "your_supabase_anon_key_here"
        )
        
        if has_real_credentials:
            try:
                from supabase import create_client, Client
                self.supabase: Client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
                self.use_mock = False
                print("✅ Using real Supabase connection")
            except Exception as e:
                print(f"❌ Supabase connection failed: {e}")
                print("🔄 Falling back to mock database")
                self._init_mock_service()
        else:
            print("⚠️  Supabase credentials not configured, using mock database")
            self._init_mock_service()
    
    def _init_mock_service(self):
        """Initialize mock database service."""
        self.use_mock = True
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
    
    # Farmer operations
    async def create_farmer(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new farmer record.
        
        Args:
            farmer_data: Farmer data including name, phone, password, etc.
            
        Returns:
            Created farmer record
        """
        result = self.supabase.table("farmers").insert(farmer_data).execute()
        return result.data[0] if result.data else None
    
    async def get_farmer_by_id(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get farmer by ID.
        
        Args:
            farmer_id: Farmer's unique ID
            
        Returns:
            Farmer record or None
        """
        result = self.supabase.table("farmers").select("*").eq("id", farmer_id).execute()
        return result.data[0] if result.data else None
    
    async def get_farmer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Get farmer by phone number.
        
        Args:
            phone: Farmer's phone number
            
        Returns:
            Farmer record or None
        """
        result = self.supabase.table("farmers").select("*").eq("phone", phone).execute()
        return result.data[0] if result.data else None
    
    async def update_farmer(self, farmer_id: str, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update farmer record.
        
        Args:
            farmer_id: Farmer's unique ID
            farmer_data: Updated farmer data
            
        Returns:
            Updated farmer record
        """
        result = self.supabase.table("farmers").update(farmer_data).eq("id", farmer_id).execute()
        return result.data[0] if result.data else None
    
    async def delete_farmer(self, farmer_id: str) -> bool:
        """
        Delete farmer record.
        
        Args:
            farmer_id: Farmer's unique ID
            
        Returns:
            True if successful
        """
        result = self.supabase.table("farmers").delete().eq("id", farmer_id).execute()
        return len(result.data) > 0
    
    # Farm operations
    async def create_farm(self, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new farm record.
        
        Args:
            farm_data: Farm data including farmer_id, location, soil_type, etc.
            
        Returns:
            Created farm record
        """
        try:
            result = self.supabase.table("farms").insert(farm_data).execute()
            if result.data:
                return result.data[0]
            else:
                raise Exception("No data returned from farm creation")
        except Exception as e:
            print(f"Error creating farm: {str(e)}")
            raise e
    
    async def get_farm_by_id(self, farm_id: str) -> Optional[Dict[str, Any]]:
        """
        Get farm by ID.
        
        Args:
            farm_id: Farm's unique ID
            
        Returns:
            Farm record or None
        """
        result = self.supabase.table("farms").select("*").eq("id", farm_id).execute()
        return result.data[0] if result.data else None
    
    async def get_farms_by_farmer_id(self, farmer_id: str) -> List[Dict[str, Any]]:
        """
        Get all farms belonging to a farmer.
        
        Args:
            farmer_id: Farmer's unique ID
            
        Returns:
            List of farm records
        """
        result = self.supabase.table("farms").select("*").eq("farmer_id", farmer_id).execute()
        return result.data if result.data else []
    
    async def get_farm_by_farmer_id(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get first farm belonging to a farmer.
        
        Args:
            farmer_id: Farmer's unique ID
            
        Returns:
            Farm record or None
        """
        result = self.supabase.table("farms").select("*").eq("farmer_id", farmer_id).execute()
        return result.data[0] if result.data else None
    
    async def update_farm(self, farm_id: str, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update farm record.
        
        Args:
            farm_id: Farm's unique ID
            farm_data: Updated farm data
            
        Returns:
            Updated farm record
        """
        result = self.supabase.table("farms").update(farm_data).eq("id", farm_id).execute()
        return result.data[0] if result.data else None
    
    async def delete_farm(self, farm_id: str) -> bool:
        """
        Delete farm record.
        
        Args:
            farm_id: Farm's unique ID
            
        Returns:
            True if successful
        """
        result = self.supabase.table("farms").delete().eq("id", farm_id).execute()
        return len(result.data) > 0
    
    # Recommendation operations
    async def create_recommendation(self, recommendation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new recommendation record.
        
        Args:
            recommendation_data: Recommendation data
            
        Returns:
            Created recommendation record
        """
        result = self.supabase.table("recommendations").insert(recommendation_data).execute()
        return result.data[0] if result.data else None
    
    async def get_recommendations_by_farm_id(self, farm_id: str) -> List[Dict[str, Any]]:
        """
        Get all recommendations for a farm.
        
        Args:
            farm_id: Farm's unique ID
            
        Returns:
            List of recommendation records
        """
        result = self.supabase.table("recommendations").select("*").eq("farm_id", farm_id).order("created_at", desc=True).execute()
        return result.data if result.data else []
    
    async def get_recommendation_by_id(self, recommendation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get recommendation by ID.
        
        Args:
            recommendation_id: Recommendation's unique ID
            
        Returns:
            Recommendation record or None
        """
        result = self.supabase.table("recommendations").select("*").eq("id", recommendation_id).execute()
        return result.data[0] if result.data else None
    
    async def update_recommendation(self, recommendation_id: str, recommendation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update recommendation record.
        
        Args:
            recommendation_id: Recommendation's unique ID
            recommendation_data: Updated recommendation data
            
        Returns:
            Updated recommendation record
        """
        result = self.supabase.table("recommendations").update(recommendation_data).eq("id", recommendation_id).execute()
        return result.data[0] if result.data else None
    
    async def delete_recommendation(self, recommendation_id: str) -> bool:
        """
        Delete recommendation record.
        
        Args:
            recommendation_id: Recommendation's unique ID
            
        Returns:
            True if successful
        """
        result = self.supabase.table("recommendations").delete().eq("id", recommendation_id).execute()
        return len(result.data) > 0
    
    # Crop history operations
    async def add_crop_history(self, crop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add crop history record.
        
        Args:
            crop_data: Crop history data
            
        Returns:
            Created crop history record
        """
        result = self.supabase.table("crops_history").insert(crop_data).execute()
        return result.data[0] if result.data else None
    
    async def get_crop_history_by_farm_id(self, farm_id: str) -> List[Dict[str, Any]]:
        """
        Get crop history for a farm.
        
        Args:
            farm_id: Farm's unique ID
            
        Returns:
            List of crop history records
        """
        result = self.supabase.table("crops_history").select("*").eq("farm_id", farm_id).order("created_at", desc=True).execute()
        return result.data if result.data else []
    
    async def get_crop_history_by_id(self, history_id: str) -> Optional[Dict[str, Any]]:
        """
        Get crop history by ID.
        
        Args:
            history_id: Crop history's unique ID
            
        Returns:
            Crop history record or None
        """
        result = self.supabase.table("crops_history").select("*").eq("id", history_id).execute()
        return result.data[0] if result.data else None
    
    async def delete_crop_history(self, history_id: str) -> bool:
        """
        Delete crop history record.
        
        Args:
            history_id: Crop history's unique ID
            
        Returns:
            True if successful
        """
        result = self.supabase.table("crops_history").delete().eq("id", history_id).execute()
        return len(result.data) > 0
    
    # Audit operations
    async def add_audit_log(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add audit log entry.
        
        Args:
            audit_data: Audit log data
            
        Returns:
            Created audit log record
        """
        result = self.supabase.table("audit_logs").insert(audit_data).execute()
        return result.data[0] if result.data else None
    
    async def get_audit_logs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get audit logs with pagination.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip
            
        Returns:
            List of audit log records
        """
        result = self.supabase.table("audit_logs").select("*").order("timestamp", desc=True).range(offset, offset + limit - 1).execute()
        return result.data if result.data else []
    
    # Analytics operations
    async def get_farmer_count(self) -> int:
        """Get total number of farmers."""
        result = self.supabase.table("farmers").select("id", count="exact").execute()
        return result.count if result.count else 0
    
    async def get_farm_count(self) -> int:
        """Get total number of farms."""
        result = self.supabase.table("farms").select("id", count="exact").execute()
        return result.count if result.count else 0
    
    async def get_recommendation_count(self) -> int:
        """Get total number of recommendations."""
        result = self.supabase.table("recommendations").select("id", count="exact").execute()
        return result.count if result.count else 0
    
    async def get_popular_crops(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular crops based on recommendation history.
        
        Args:
            limit: Number of crops to return
            
        Returns:
            List of popular crops with counts
        """
        # This would require aggregation which might need a custom SQL function
        # For now, return a simple query
        result = self.supabase.table("crops_history").select("crop").execute()
        
        if not result.data:
            return []
        
        # Count crops manually for simplicity
        crop_counts = {}
        for record in result.data:
            crop = record.get("crop", "")
            if crop:
                crop_counts[crop] = crop_counts.get(crop, 0) + 1
        
        # Sort by count and return top crops
        sorted_crops = sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"crop": crop, "count": count} for crop, count in sorted_crops[:limit]]
    
    async def get_regional_data(self, district: str = None) -> Dict[str, Any]:
        """
        Get regional farming data.
        
        Args:
            district: Optional district filter
            
        Returns:
            Regional data summary
        """
        query = self.supabase.table("farms").select("location")
        if district:
            # This would depend on how location is stored in the database
            # For now, assuming it's stored as a JSON field
            query = query.contains("location", {"district": district})
        
        result = query.execute()
        
        return {
            "district": district,
            "farm_count": len(result.data) if result.data else 0,
            "farms": result.data if result.data else []
        }
    
    async def get_suitable_crops_by_district(self, district: str) -> List[Dict[str, Any]]:
        """
        Get suitable crops for a specific district.
        
        Args:
            district: District name
            
        Returns:
            List of suitable crops
        """
        # This would involve complex soil and climate data analysis
        # For prototype, returning common crops for Jharkhand
        from app.core.config import JHARKHAND_CROPS
        
        # Return a subset of crops with mock suitability scores
        suitable_crops = []
        for i, crop in enumerate(JHARKHAND_CROPS[:10]):
            suitable_crops.append({
                "crop": crop,
                "suitability_score": max(0.6, 1.0 - (i * 0.05)),
                "district": district,
                "season_recommendation": "Kharif" if i % 2 == 0 else "Rabi"
            })
        
        return suitable_crops


# Global database instance
db_service = DatabaseService()