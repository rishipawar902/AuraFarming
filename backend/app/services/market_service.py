"""
Enhanced market service for fetching market prices and trends.
Integrates with multi-source data including AGMARKNET, government portals, and eNAM.
"""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import json
import logging
from app.core.config import settings
from app.services.enhanced_agmarknet_scraper import enhanced_agmarknet_scraper
from app.services.multi_source_market_service import MultiSourceMarketService

logger = logging.getLogger(__name__)


class MarketService:
    """
    Enhanced market service with multi-source data integration.
    Combines AGMARKNET, government portals, and eNAM for comprehensive market intelligence.
    """
    
    def __init__(self):
        """Initialize enhanced market service."""
        # Initialize multi-source service
        self.multi_source_service = MultiSourceMarketService()
        
        # Legacy API URLs for fallback
        self.agmarknet_base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        self.backup_api_url = "https://agmarknet.gov.in/Others/profile.aspx"
        
        # Initialize districts first
        self.jharkhand_districts = [
            "Ranchi", "Dhanbad", "Jamshedpur", "Bokaro", "Deoghar", 
            "Hazaribagh", "Giridih", "Ramgarh", "Medininagar", "Chaibasa"
        ]
        
        # Now initialize mock data (which uses districts)
        self.mock_data = self._initialize_enhanced_market_data()
        
        # Initialize enhanced scraper
        self.enhanced_scraper = enhanced_agmarknet_scraper
    
    def _initialize_enhanced_market_data(self) -> Dict[str, Any]:
        """Initialize comprehensive mock market data for all Jharkhand districts."""
        
        # Base prices for major crops (per quintal in INR)
        base_crops = {
            "Rice": {"min": 1800, "max": 2200, "modal": 2000, "seasonal_factor": 1.0},
            "Wheat": {"min": 1900, "max": 2300, "modal": 2100, "seasonal_factor": 1.1},
            "Maize": {"min": 1400, "max": 1800, "modal": 1600, "seasonal_factor": 0.9},
            "Potato": {"min": 800, "max": 1200, "modal": 1000, "seasonal_factor": 1.2},
            "Arhar (Tur)": {"min": 5500, "max": 6500, "modal": 6000, "seasonal_factor": 1.0},
            "Groundnut": {"min": 4500, "max": 5500, "modal": 5000, "seasonal_factor": 1.1},
            "Mustard": {"min": 4000, "max": 5000, "modal": 4500, "seasonal_factor": 1.0},
            "Gram": {"min": 4200, "max": 5200, "modal": 4700, "seasonal_factor": 0.95},
            "Soybean": {"min": 3800, "max": 4800, "modal": 4300, "seasonal_factor": 1.05},
            "Sugarcane": {"min": 280, "max": 320, "modal": 300, "seasonal_factor": 1.0},
            "Cotton": {"min": 5000, "max": 6000, "modal": 5500, "seasonal_factor": 1.15},
            "Onion": {"min": 1200, "max": 2000, "modal": 1600, "seasonal_factor": 1.3},
            "Tomato": {"min": 800, "max": 1500, "modal": 1200, "seasonal_factor": 1.4},
            "Cabbage": {"min": 400, "max": 800, "modal": 600, "seasonal_factor": 1.2},
            "Cauliflower": {"min": 600, "max": 1000, "modal": 800, "seasonal_factor": 1.1}
        }
        
        market_data = {}
        
        # Generate data for all Jharkhand districts
        for district in self.jharkhand_districts:
            district_factor = random.uniform(0.95, 1.05)  # District price variation
            market_data[district] = {}
            
            for crop, data in base_crops.items():
                # Apply district and seasonal factors
                price_modifier = district_factor * data["seasonal_factor"]
                
                market_data[district][crop] = {
                    "min": round(data["min"] * price_modifier),
                    "max": round(data["max"] * price_modifier),
                    "modal": round(data["modal"] * price_modifier),
                    "demand": random.choice(["High", "Medium", "Low"]),
                    "quality_grades": ["A", "B", "C"],
                    "transportation_cost": random.randint(50, 200),  # Per quintal
                    "market_fee": round(data["modal"] * 0.02, 2),  # 2% market fee
                    "storage_available": random.choice([True, False])
                }
        
        return market_data
    
    async def get_mandi_prices(self, district: str, crop: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current mandi prices using multi-source data integration.
        
        Args:
            district: District name
            crop: Optional crop filter
            
        Returns:
            Comprehensive market prices from multiple sources
        """
        try:
            # Use multi-source service for comprehensive data
            logger.info(f"Getting multi-source market data for {district}, crop: {crop}")
            comprehensive_data = await self.multi_source_service.get_comprehensive_market_data(district, crop)
            
            if comprehensive_data.get("status") == "success":
                # Format the comprehensive data for API response
                formatted_prices = []
                
                for item in comprehensive_data.get("data", []):
                    price_data = {
                        "crop": item["commodity"],
                        "market": item["market"],
                        "min_price": item["min_price"],
                        "max_price": item["max_price"],
                        "modal_price": item["modal_price"],
                        "unit": item.get("unit", "per quintal"),
                        "arrival_quantity": item["arrival"],
                        "date": item["date"],
                        "trend": item["trend"],
                        "price_change": self._calculate_price_change(item["modal_price"]),
                        "market_fee": round(item["modal_price"] * 0.02),  # 2% market fee
                        "transport_cost": self._calculate_transport_cost(district),
                        "source": item["source"],
                        "data_quality": "multi-source",
                        "variety": item.get("variety", "Common"),
                        "confidence": item.get("confidence", 0.75)
                    }
                    
                    # Filter by crop if specified
                    if not crop or price_data["crop"].lower() == crop.lower():
                        formatted_prices.append(price_data)
                
                return {
                    "status": "success",
                    "district": district,
                    "crop_filter": crop,
                    "prices": formatted_prices,
                    "market_summary": {
                        "total_commodities": len(set(p["crop"] for p in formatted_prices)),
                        "sources_used": comprehensive_data.get("sources_used", []),
                        "data_quality_score": comprehensive_data.get("data_quality_score", 0.0),
                        "market_insights": comprehensive_data.get("market_insights", {}),
                        "aggregated_prices": comprehensive_data.get("aggregated_prices", {}),
                        "last_updated": comprehensive_data.get("timestamp")
                    },
                    "source_summary": comprehensive_data.get("source_summary", {}),
                    "message": f"Multi-source market data for {district}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Fallback to legacy method
                logger.warning("Multi-source service failed, using legacy method")
                return await self._get_legacy_mandi_prices(district, crop)
                
        except Exception as e:
            logger.error(f"Error in multi-source market service: {e}")
            # Fallback to legacy method
            return await self._get_legacy_mandi_prices(district, crop)
            
    async def _get_legacy_mandi_prices(self, district: str, crop: Optional[str] = None) -> Dict[str, Any]:
        """
        Legacy method for getting mandi prices (fallback).
        """
        try:
            # Get real data from enhanced AGMARKNET scraper
            real_data = await enhanced_agmarknet_scraper.get_market_data(district, crop, days=7)
            
            if real_data.get("status") == "success" and real_data.get("data"):
                # Process and format the real data
                prices = []
                for item in real_data["data"]:
                    price_data = {
                        "crop": item["commodity"],
                        "market": item["market"],
                        "min_price": item["min_price"],
                        "max_price": item["max_price"],
                        "modal_price": item["modal_price"],
                        "unit": "per quintal",
                        "arrival_quantity": item["arrival"],
                        "date": item["date"],
                        "trend": item["trend"],
                        "price_change": self._calculate_price_change(item["modal_price"]),
                        "market_fee": round(item["modal_price"] * 0.02),  # 2% market fee
                        "transport_cost": self._calculate_transport_cost(district),
                        "source": "AGMARKNET",
                        "data_quality": "real",
                        "variety": item["variety"]
                    }
                    
                    # Filter by crop if specified
                    if not crop or crop.lower() in item["commodity"].lower():
                        prices.append(price_data)
                
                if prices:
                    return {
                        "district": district,
                        "prices": prices,
                        "last_updated": real_data["timestamp"],
                        "data_source": "AGMARKNET_SCRAPER",
                        "total_crops": len(prices),
                        "status": "success"
                    }
            
            # Fallback to enhanced mock data if real data fails
            print(f"AGMARKNET data unavailable for {district}, using enhanced fallback")
            return await self._get_fallback_mandi_prices(district, crop)
        except Exception as e:
            print(f"Error in get_mandi_prices: {e}")
            return await self._get_fallback_mandi_prices(district, crop)

    async def _get_fallback_mandi_prices(self, district: str, crop: Optional[str] = None) -> Dict[str, Any]:
        """Fallback method using enhanced mock data when AGMARKNET is unavailable."""
        district_prices = self.mock_data.get(district, self.mock_data["Ranchi"])
        
        prices = []
        crops_to_fetch = [crop] if crop else list(district_prices.keys())
        
        for crop_name in crops_to_fetch:
            if crop_name in district_prices:
                price_data = district_prices[crop_name]
                
                # Add time-based variation to simulate real market fluctuations
                current_hour = datetime.now().hour
                time_factor = 1.0 + (0.05 * (current_hour - 12) / 12)
                market_variation = random.uniform(0.98, 1.02)
                final_factor = time_factor * market_variation
                
                # Calculate prices with fees and transportation
                base_modal = price_data["modal"] * final_factor
                market_fee = price_data["market_fee"]
                transport_cost = price_data["transportation_cost"]
                
                prices.append({
                    "crop": crop_name,
                    "market": f"{district} Mandi",
                    "min_price": round(price_data["min"] * final_factor),
                    "max_price": round(price_data["max"] * final_factor),
                    "modal_price": round(base_modal),
                    "effective_price": round(base_modal - market_fee - transport_cost),
                    "market_fee": market_fee,
                    "transportation_cost": transport_cost,
                    "unit": "per quintal",
                    "currency": "INR",
                    "date": datetime.now().strftime("%d-%b-%Y"),
                    "demand": price_data["demand"],
                    "trend": self._calculate_price_trend(crop_name),
                    "volume_traded": random.randint(100, 1000),
                    "arrival_quantity": random.randint(500, 2000),
                    "source": "Enhanced Mock Data"
                })
        
        return {
            "district": district,
            "state": "Jharkhand", 
            "prices": prices,
            "market_status": "Open" if 9 <= datetime.now().hour <= 17 else "Closed",
            "last_updated": datetime.now().isoformat(),
            "source": "Enhanced Market Data Service (Fallback)",
            "total_crops": len(prices),
            "active_traders": random.randint(50, 200)
        }

    def _calculate_price_change(self, current_price: float) -> Dict[str, Any]:
        """Calculate price change metrics."""
        # Simulate price change (in real implementation, compare with historical data)
        change_percent = random.uniform(-5.0, 5.0)
        change_amount = round(current_price * (change_percent / 100))
        
        return {
            "amount": change_amount,
            "percentage": round(change_percent, 2),
            "direction": "up" if change_amount > 0 else "down" if change_amount < 0 else "stable"
        }

    def _calculate_transport_cost(self, district: str) -> int:
        """Calculate transportation cost based on district."""
        # Distance-based transport cost calculation
        transport_costs = {
            "Ranchi": 50, "Dhanbad": 60, "Bokaro": 55, "Hazaribagh": 65,
            "Deoghar": 70, "Giridih": 65, "East Singhbhum": 80, "West Singhbhum": 85
        }
        return transport_costs.get(district, 60)
    
    def _calculate_price_trend(self, crop: str) -> str:
        """Calculate price trend based on historical patterns."""
        # Simulate trend calculation
        trends = ["Rising", "Stable", "Falling"]
        weights = [0.3, 0.5, 0.2]  # Favor stable prices
        return random.choices(trends, weights=weights)[0]
    
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
        
        # Handle case when we don't have enough data for comparison
        if len(earlier_prices) == 0:
            # Use first half vs second half if we have less than 14 days
            mid_point = len(price_history) // 2
            if mid_point > 0:
                earlier_prices = [p["price"] for p in price_history[:mid_point]]
                recent_prices = [p["price"] for p in price_history[mid_point:]]
                earlier_avg = sum(earlier_prices) / len(earlier_prices)
                recent_avg = sum(recent_prices) / len(recent_prices)
            else:
                earlier_avg = recent_avg
        else:
            earlier_avg = sum(earlier_prices) / len(earlier_prices)
        
        trend_direction = "Rising" if recent_avg > earlier_avg else "Falling"
        trend_percentage = abs((recent_avg - earlier_avg) / max(earlier_avg, 1) * 100)
        
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