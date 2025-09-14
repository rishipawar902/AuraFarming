"""
Admin Service for administrative operations and statistics.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AdminService:
    """
    Service for admin dashboard operations.
    """
    
    def __init__(self):
        pass
    
    async def get_platform_stats(self) -> Dict[str, Any]:
        """Get platform-wide statistics."""
        # Mock statistics for demo
        return {
            "total_farmers": 1250,
            "total_farms": 950,
            "total_recommendations": 3200,
            "active_users_today": 45,
            "avg_farm_size": 2.5,
            "total_area_covered": 2375.0
        }
    
    async def get_crop_adoption_stats(self) -> List[Dict[str, Any]]:
        """Get crop adoption statistics."""
        return [
            {"crop": "Rice", "adoption_rate": 75.2, "total_farmers": 940},
            {"crop": "Wheat", "adoption_rate": 45.6, "total_farmers": 570},
            {"crop": "Maize", "adoption_rate": 38.9, "total_farmers": 486},
            {"crop": "Potato", "adoption_rate": 22.1, "total_farmers": 276},
            {"crop": "Arhar", "adoption_rate": 18.7, "total_farmers": 234}
        ]
    
    async def get_district_wise_data(self) -> List[Dict[str, Any]]:
        """Get district-wise farming data."""
        return [
            {"district": "Ranchi", "farmers": 320, "avg_yield": 4.2},
            {"district": "Jamshedpur", "farmers": 280, "avg_yield": 3.8},
            {"district": "Dhanbad", "farmers": 245, "avg_yield": 4.1},
            {"district": "Bokaro", "farmers": 205, "avg_yield": 3.9},
            {"district": "Deoghar", "farmers": 200, "avg_yield": 4.0}
        ]