"""
Enhanced Market service for fetching real-time market prices and trends.
Now supports real government data scraping with fallback to mock data.
"""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import logging

# Import real market services
try:
    from .real_government_scraper import RealGovernmentDataScraper
    from .multi_source_market_service import MultiSourceMarketService
    REAL_MARKET_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Real market services not available: {e}")
    REAL_MARKET_AVAILABLE = False

logger = logging.getLogger(__name__)


class MarketService:
    """
    Original Market service for fetching mandi prices and market data.
    Maintained for backward compatibility and as reliable fallback.
    """
    
    def __init__(self):
        """Initialize market service."""
        # In production, this would use actual Agmarknet API
        self.agmarknet_base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        self.mock_data = self._initialize_mock_market_data()
    """
    Enhanced market service that combines real-time data with reliable fallback.
    Uses real government data when available, falls back to mock data for reliability.
    Inherits from MarketService to maintain all existing functionality.
    """
    
    def __init__(self):
        """Initialize enhanced market service."""
        # Initialize parent class first
        super().__init__()
        
        # Initialize real market services if available
        if REAL_MARKET_AVAILABLE:
            try:
                self.real_scraper = RealGovernmentDataScraper()
                self.multi_source = MultiSourceMarketService()
                self.use_real_data = True
                logger.info("Real market data services initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize real market services: {e}")
                self.use_real_data = False
        else:
            self.use_real_data = False
            logger.info("Using mock market data only")

    async def get_mandi_prices_with_fallback(self, district: str, crop: Optional[str] = None) -> Dict[str, Any]:
        """
        Get mandi prices with real data and fallback.
        
        Args:
            district: District name
            crop: Optional crop filter
            
        Returns:
            Current market prices (real or mock)
        """
        if self.use_real_data:
            try:
                # Try to get real data first
                logger.info(f"Attempting to fetch real market data for {district}")
                real_data = await self.multi_source.get_enhanced_market_data(district, crop)
                
                if real_data and real_data.get('prices'):
                    logger.info(f"Successfully fetched real market data for {district}")
                    return {
                        **real_data,
                        "data_source": "real_government_apis",
                        "reliability": "high"
                    }
            except Exception as e:
                logger.warning(f"Real market data failed for {district}: {e}")
        
        # Fallback to mock data
        logger.info(f"Using mock market data for {district}")
        mock_data = await self.get_mandi_prices(district, crop)
        return {
            **mock_data,
            "data_source": "mock_data",
            "reliability": "medium"
        }


class MarketService:
    """
    Original Market service for fetching mandi prices and market data.
    Maintained for backward compatibility and as reliable fallback.
    """
    
    def __init__(self):
        """Initialize market service."""
        # In production, this would use actual Agmarknet API
        self.agmarknet_base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        self.mock_data = self._initialize_mock_market_data()
    
    def _initialize_mock_market_data(self) -> Dict[str, Any]:
        """Initialize mock market data for prototype."""
        return {
            "Ranchi": {
                "Rice": {"min": 1800, "max": 2200, "modal": 2000},
                "Wheat": {"min": 1900, "max": 2300, "modal": 2100},
                "Maize": {"min": 1400, "max": 1800, "modal": 1600},
                "Potato": {"min": 800, "max": 1200, "modal": 1000},
                "Arhar": {"min": 5500, "max": 6500, "modal": 6000},
                "Groundnut": {"min": 4500, "max": 5500, "modal": 5000}
            },
            "Dhanbad": {
                "Rice": {"min": 1750, "max": 2150, "modal": 1950},
                "Wheat": {"min": 1850, "max": 2250, "modal": 2050},
                "Maize": {"min": 1350, "max": 1750, "modal": 1550},
                "Potato": {"min": 750, "max": 1150, "modal": 950},
                "Arhar": {"min": 5400, "max": 6400, "modal": 5900},
                "Groundnut": {"min": 4400, "max": 5400, "modal": 4900}
            }
        }
    
    async def get_mandi_prices(self, district: str, crop: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current mandi prices for a district.
        
        Args:
            district: District name
            crop: Optional crop filter
            
        Returns:
            Current market prices
        """
        try:
            # In production, this would call actual Agmarknet API
            district_prices = self.mock_data.get(district, self.mock_data["Ranchi"])
            
            prices = []
            crops_to_fetch = [crop] if crop else list(district_prices.keys())
            
            for crop_name in crops_to_fetch:
                if crop_name in district_prices:
                    price_data = district_prices[crop_name]
                    
                    # Add some random variation to simulate real market
                    variation = random.uniform(0.95, 1.05)
                    
                    prices.append({
                        "crop": crop_name,
                        "market": f"{district} Mandi",
                        "min_price": round(price_data["min"] * variation),
                        "max_price": round(price_data["max"] * variation),
                        "modal_price": round(price_data["modal"] * variation),
                        "unit": "per quintal",
                        "date": datetime.utcnow(),
                        "trend": random.choice(["Rising", "Stable", "Falling"])
                    })
            
            return {
                "district": district,
                "prices": prices,
                "last_updated": datetime.utcnow(),
                "source": "Mock Agmarknet Data"
            }
        
        except Exception as e:
            return {
                "district": district,
                "prices": [],
                "error": "Market data temporarily unavailable",
                "last_updated": datetime.utcnow()
            }
    
    async def get_price_trends(self, crop: str, days: int = 30) -> Dict[str, Any]:
        """
        Get price trends for a specific crop.
        
        Args:
            crop: Crop name
            days: Number of days for trend analysis
            
        Returns:
            Price trend data and analysis
        """
        # Generate mock historical price data
        base_price = 2000  # Base price per quintal
        if crop in self.mock_data["Ranchi"]:
            base_price = self.mock_data["Ranchi"][crop]["modal"]
        
        price_history = []
        current_price = base_price
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            
            # Simulate price fluctuation
            change = random.uniform(-0.05, 0.05)  # ±5% daily change
            current_price *= (1 + change)
            
            price_history.append({
                "date": date.date(),
                "price": round(current_price),
                "volume": random.randint(50, 500)  # Quintal traded
            })
        
        # Calculate trend analysis
        recent_prices = [p["price"] for p in price_history[-7:]]  # Last 7 days
        earlier_prices = [p["price"] for p in price_history[-14:-7]]  # Previous 7 days
        
        recent_avg = sum(recent_prices) / len(recent_prices)
        earlier_avg = sum(earlier_prices) / len(earlier_prices)
        
        trend_direction = "Rising" if recent_avg > earlier_avg else "Falling"
        trend_percentage = abs((recent_avg - earlier_avg) / earlier_avg * 100)
        
        return {
            "crop": crop,
            "price_history": price_history,
            "trend_analysis": {
                "direction": trend_direction,
                "percentage_change": round(trend_percentage, 2),
                "current_price": round(current_price),
                "highest_price": max(p["price"] for p in price_history),
                "lowest_price": min(p["price"] for p in price_history),
                "average_price": round(sum(p["price"] for p in price_history) / len(price_history))
            },
            "generated_at": datetime.utcnow()
        }
    
    async def get_price_forecast(self, crop: str) -> Dict[str, Any]:
        """
        Get price forecast for a specific crop.
        
        Args:
            crop: Crop name
            
        Returns:
            Price forecast for next 30 days
        """
        # Get current trend
        trend_data = await self.get_price_trends(crop, 30)
        current_price = trend_data["trend_analysis"]["current_price"]
        
        # Generate forecast based on seasonal patterns and trends
        forecast = []
        forecast_price = current_price
        
        for i in range(30):
            date = datetime.now() + timedelta(days=i+1)
            
            # Simulate seasonal and random factors
            seasonal_factor = 1 + 0.02 * (i / 30)  # Slight seasonal increase
            random_factor = random.uniform(0.98, 1.02)  # ±2% random variation
            
            forecast_price *= seasonal_factor * random_factor
            
            forecast.append({
                "date": date.date(),
                "predicted_price": round(forecast_price),
                "confidence": max(0.6, 0.9 - (i * 0.01))  # Decreasing confidence over time
            })
        
        return {
            "crop": crop,
            "forecast": forecast,
            "forecast_summary": {
                "expected_trend": "Rising" if forecast[-1]["predicted_price"] > current_price else "Falling",
                "price_range": {
                    "min": min(f["predicted_price"] for f in forecast),
                    "max": max(f["predicted_price"] for f in forecast)
                },
                "average_confidence": round(sum(f["confidence"] for f in forecast) / len(forecast), 2)
            },
            "generated_at": datetime.utcnow()
        }
    
    async def get_best_markets(self, crop: str, origin_district: str) -> Dict[str, Any]:
        """
        Get best markets to sell a crop.
        
        Args:
            crop: Crop name
            origin_district: Farmer's district
            
        Returns:
            List of best markets with price and distance information
        """
        # Mock market locations with distances
        market_options = [
            {"market": "Ranchi Mandi", "district": "Ranchi", "distance_km": 0 if origin_district == "Ranchi" else 100},
            {"market": "Dhanbad Market", "district": "Dhanbad", "distance_km": 0 if origin_district == "Dhanbad" else 150},
            {"market": "Bokaro Agricultural Market", "district": "Bokaro", "distance_km": 80},
            {"market": "Hazaribagh Wholesale Market", "district": "Hazaribagh", "distance_km": 120},
            {"market": "Jamshedpur Commodity Exchange", "district": "East Singhbhum", "distance_km": 200}
        ]
        
        best_markets = []
        
        for market in market_options:
            # Get price for this market
            district_prices = self.mock_data.get(market["district"], self.mock_data["Ranchi"])
            
            if crop in district_prices:
                price_data = district_prices[crop]
                modal_price = price_data["modal"]
                
                # Calculate transportation cost (₹2 per km per quintal)
                transport_cost = market["distance_km"] * 2
                net_price = modal_price - transport_cost
                
                best_markets.append({
                    "market_name": market["market"],
                    "district": market["district"],
                    "distance_km": market["distance_km"],
                    "modal_price": modal_price,
                    "transport_cost_per_quintal": transport_cost,
                    "net_price_per_quintal": max(0, net_price),
                    "facilities": ["Weighing", "Storage", "Banking"] if market["distance_km"] == 0 else ["Weighing"],
                    "market_timing": "6:00 AM - 6:00 PM"
                })
        
        # Sort by net price (descending)
        best_markets.sort(key=lambda x: x["net_price_per_quintal"], reverse=True)
        
        return {
            "crop": crop,
            "origin_district": origin_district,
            "markets": best_markets[:5],  # Top 5 markets
            "generated_at": datetime.utcnow()
        }
    
    async def get_market_demand(self, district: str) -> Dict[str, Any]:
        """
        Get market demand analysis for a district.
        
        Args:
            district: District name
            
        Returns:
            Market demand data and insights
        """
        # Mock demand data
        demand_data = {
            "high_demand_crops": [
                {"crop": "Rice", "demand_score": 0.9, "reason": "Staple food, consistent demand"},
                {"crop": "Potato", "demand_score": 0.85, "reason": "High consumption, good storage"},
                {"crop": "Arhar", "demand_score": 0.8, "reason": "Protein source, festival demand"}
            ],
            "moderate_demand_crops": [
                {"crop": "Wheat", "demand_score": 0.7, "reason": "Seasonal consumption"},
                {"crop": "Maize", "demand_score": 0.65, "reason": "Poultry feed demand"}
            ],
            "low_demand_crops": [
                {"crop": "Groundnut", "demand_score": 0.5, "reason": "Niche market, price volatility"}
            ],
            "emerging_opportunities": [
                {"crop": "Organic Vegetables", "growth_potential": "High", "reason": "Health consciousness"},
                {"crop": "Medicinal Plants", "growth_potential": "Medium", "reason": "Ayurveda industry growth"}
            ]
        }
        
        return {
            "district": district,
            "demand_analysis": demand_data,
            "market_insights": [
                "Focus on high-demand staple crops for stable income",
                "Consider value addition for better profit margins",
                "Explore organic certification for premium pricing"
            ],
            "generated_at": datetime.utcnow()
        }
    
    async def get_potential_buyers(self, crop: str, district: str) -> Dict[str, Any]:
        """
        Get potential buyers and supply chain information.
        
        Args:
            crop: Crop name
            district: District name
            
        Returns:
            List of potential buyers and supply chain options
        """
        # Mock buyer data
        buyers = [
            {
                "buyer_name": "Jharkhand State Cooperative",
                "type": "Government Procurement",
                "contact": "+91-9876543210",
                "payment_terms": "Immediate payment",
                "minimum_quantity": "10 quintal",
                "price_offered": "MSP + 5%",
                "location": district
            },
            {
                "buyer_name": "Regional Food Processing Unit",
                "type": "Private Processor",
                "contact": "+91-9876543211",
                "payment_terms": "15 days",
                "minimum_quantity": "50 quintal",
                "price_offered": "Market rate + 3%",
                "location": f"Near {district}"
            },
            {
                "buyer_name": "Direct Consumer Network",
                "type": "Retail Chain",
                "contact": "+91-9876543212",
                "payment_terms": "30 days",
                "minimum_quantity": "5 quintal",
                "price_offered": "Market rate + 10%",
                "location": "Multiple locations"
            }
        ]
        
        supply_chain_options = [
            {
                "option": "Farmer Producer Organization (FPO)",
                "benefits": ["Collective bargaining", "Better prices", "Input support"],
                "contact": "Jharkhand FPO Federation"
            },
            {
                "option": "E-marketplace",
                "benefits": ["Direct selling", "Wider reach", "Transparent pricing"],
                "contact": "eNAM platform"
            },
            {
                "option": "Contract Farming",
                "benefits": ["Assured price", "Input support", "Technical guidance"],
                "contact": "Agriculture Development Officer"
            }
        ]
        
        return {
            "crop": crop,
            "district": district,
            "potential_buyers": buyers,
            "supply_chain_options": supply_chain_options,
            "recommendations": [
                "Compare prices from multiple buyers",
                "Consider value addition before selling",
                "Join FPO for better market access"
            ],
            "generated_at": datetime.utcnow()
        }