"""
Realtime Market Scraper
A simple wrapper that uses the real government scraper for realtime data.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from .real_government_scraper import RealGovernmentDataScraper

logger = logging.getLogger(__name__)


class RealtimeMarketScraper:
    """
    Realtime market scraper that aggregates data from government sources.
    """
    
    def __init__(self):
        """Initialize the realtime scraper."""
        self.government_scraper = RealGovernmentDataScraper()
    
    async def get_market_data(self, district: str, commodity: Optional[str] = None) -> Dict[str, Any]:
        """
        Get realtime market data for a district and commodity.
        
        Args:
            district: District name
            commodity: Commodity name (optional)
            
        Returns:
            Market data with prices and trends
        """
        try:
            # Use the government scraper for real data
            data = await self.government_scraper.get_market_data(district, commodity)
            
            if data.get('success'):
                return {
                    'success': True,
                    'source': 'realtime_government',
                    'data': data.get('data', []),
                    'timestamp': datetime.now().isoformat(),
                    'district': district,
                    'commodity': commodity
                }
            else:
                # Fallback to mock data if scraping fails
                return await self._get_fallback_data(district, commodity)
                
        except Exception as e:
            logger.error(f"Realtime scraper error for {district}, {commodity}: {e}")
            return await self._get_fallback_data(district, commodity)
    
    async def _get_fallback_data(self, district: str, commodity: Optional[str] = None) -> Dict[str, Any]:
        """
        Provide fallback mock data when scraping fails.
        """
        import random
        
        # Mock data for Jharkhand districts
        mock_crops = ['Rice', 'Wheat', 'Maize', 'Potato', 'Arhar', 'Groundnut']
        
        if commodity:
            crops_data = [{
                'commodity': commodity,
                'min_price': random.randint(1000, 2000),
                'max_price': random.randint(2000, 3000),
                'modal_price': random.randint(1500, 2500),
                'market': f"{district} Mandi",
                'date': datetime.now().strftime('%Y-%m-%d')
            }]
        else:
            crops_data = []
            for crop in mock_crops[:3]:  # Return top 3 crops
                crops_data.append({
                    'commodity': crop,
                    'min_price': random.randint(1000, 2000),
                    'max_price': random.randint(2000, 3000),
                    'modal_price': random.randint(1500, 2500),
                    'market': f"{district} Mandi",
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
        
        return {
            'success': True,
            'source': 'fallback_mock',
            'data': crops_data,
            'timestamp': datetime.now().isoformat(),
            'district': district,
            'commodity': commodity,
            'note': 'Using fallback data due to scraping issues'
        }


# Create a singleton instance for import
realtime_scraper = RealtimeMarketScraper()