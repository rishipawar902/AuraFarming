"""
Database service for Supabase integration.
"""

from supabase import create_client, Client
from app.core.config import settings
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import json


class DatabaseService:
    """
    Database service for handling all Supabase operations.
    """
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    
    # Farmer operations
    async def create_farmer(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new farmer record.
        
        Args:
            farmer_data: Farmer data dictionary
            
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
    
    # Farm operations
    async def create_farm(self, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new farm record.
        
        Args:
            farm_data: Farm data dictionary
            
        Returns:
            Created farm record
        """
        result = self.supabase.table("farms").insert(farm_data).execute()
        return result.data[0] if result.data else None
    
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
    
    async def get_farm_by_farmer_id(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get farm by farmer ID.
        
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
    
    # Crop history operations
    async def create_crop_history(self, crop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create crop history record.
        
        Args:
            crop_data: Crop history data
            
        Returns:
            Created crop history record
        """
        result = self.supabase.table("crops_history").insert(crop_data).execute()
        return result.data[0] if result.data else None
    
    async def get_crop_history_by_farm_id(self, farm_id: str) -> List[Dict[str, Any]]:
        """
        Get crop history by farm ID.
        
        Args:
            farm_id: Farm's unique ID
            
        Returns:
            List of crop history records
        """
        result = self.supabase.table("crops_history").select("*").eq("farm_id", farm_id).order("created_at", desc=True).execute()
        return result.data or []
    
    async def get_crop_history_by_id(self, history_id: str) -> Optional[Dict[str, Any]]:
        """
        Get crop history by ID.
        
        Args:
            history_id: Crop history ID
            
        Returns:
            Crop history record or None
        """
        result = self.supabase.table("crops_history").select("*").eq("id", history_id).execute()
        return result.data[0] if result.data else None
    
    async def delete_crop_history(self, history_id: str) -> bool:
        """
        Delete crop history record.
        
        Args:
            history_id: Crop history ID
            
        Returns:
            True if deleted successfully
        """
        result = self.supabase.table("crops_history").delete().eq("id", history_id).execute()
        return len(result.data) > 0
    
    # Recommendation operations
    async def create_recommendation(self, recommendation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create recommendation record.
        
        Args:
            recommendation_data: Recommendation data
            
        Returns:
            Created recommendation record
        """
        result = self.supabase.table("recommendations").insert(recommendation_data).execute()
        return result.data[0] if result.data else None
    
    async def get_recommendations_by_farm_id(self, farm_id: str) -> List[Dict[str, Any]]:
        """
        Get recommendations by farm ID.
        
        Args:
            farm_id: Farm's unique ID
            
        Returns:
            List of recommendation records
        """
        result = self.supabase.table("recommendations").select("*").eq("farm_id", farm_id).order("created_at", desc=True).execute()
        return result.data or []
    
    # Audit log operations
    async def create_audit_log(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create audit log record.
        
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
            limit: Number of records to retrieve
            offset: Number of records to skip
            
        Returns:
            List of audit log records
        """
        result = self.supabase.table("audit_logs").select("*").order("timestamp", desc=True).range(offset, offset + limit - 1).execute()
        return result.data or []
    
    # Analytics operations
    async def get_total_farmers(self) -> int:
        """Get total number of farmers."""
        result = self.supabase.table("farmers").select("id", count="exact").execute()
        return result.count or 0
    
    async def get_total_farms(self) -> int:
        """Get total number of farms."""
        result = self.supabase.table("farms").select("id", count="exact").execute()
        return result.count or 0
    
    async def get_total_recommendations(self) -> int:
        """Get total number of recommendations."""
        result = self.supabase.table("recommendations").select("id", count="exact").execute()
        return result.count or 0
    
    async def get_popular_crops(self) -> List[Dict[str, Any]]:
        """
        Get popular crops based on historical data.
        
        Returns:
            List of popular crops with counts
        """
        # This would be a more complex query in production
        # For now, returning mock data structure
        result = self.supabase.table("crops_history").select("crop").execute()
        
        if not result.data:
            return []
        
        # Count crop occurrences
        crop_counts = {}
        for record in result.data:
            crop = record.get("crop")
            if crop:
                crop_counts[crop] = crop_counts.get(crop, 0) + 1
        
        # Sort by popularity
        popular_crops = [
            {"crop": crop, "count": count}
            for crop, count in sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return popular_crops[:10]  # Top 10
    
    async def get_district_wise_stats(self) -> Dict[str, int]:
        """
        Get district-wise farm statistics.
        
        Returns:
            Dictionary with district names and farm counts
        """
        result = self.supabase.table("farms").select("location").execute()
        
        if not result.data:
            return {}
        
        district_counts = {}
        for farm in result.data:
            location = farm.get("location", {})
            if isinstance(location, str):
                try:
                    location = json.loads(location)
                except:
                    continue
            
            district = location.get("district")
            if district:
                district_counts[district] = district_counts.get(district, 0) + 1
        
        return district_counts
    
    async def get_suitable_crops_by_district(self, district: str) -> List[Dict[str, Any]]:
        """
        Get crops suitable for a specific district.
        
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