"""
Market-Aware ML Service for profit-optimized crop recommendations.
Integrates real-time market prices with agricultural ML models.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import asyncio

# Import existing services
from .ml_service import MLService
from .market_service import MarketService
from app.models.schemas import CropRecommendation

logger = logging.getLogger(__name__)


class MarketAwareMLService:
    """
    Enhanced ML service that combines crop suitability predictions with market intelligence
    for profit-optimized recommendations.
    """
    
    def __init__(self):
        """Initialize market-aware ML service."""
        self.ml_service = MLService()
        self.market_service = MarketService()
        
        # Market feature weights for profit calculation
        self.market_weights = {
            'current_price': 0.4,      # Current market price impact
            'price_trend': 0.2,        # Price trend direction
            'seasonal_factor': 0.15,   # Seasonal price patterns
            'demand_score': 0.15,      # Market demand
            'volatility': 0.1         # Price stability
        }
        
    async def get_market_enhanced_recommendations(
        self, 
        farm_data: Dict[str, Any],
        district: str,
        include_profit_analysis: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get crop recommendations enhanced with market intelligence.
        
        Args:
            farm_data: Farm characteristics (soil, climate, etc.)
            district: District for market data
            include_profit_analysis: Whether to include profit calculations
            
        Returns:
            List of market-aware crop recommendations
        """
        try:
            # Get base ML recommendations
            base_recommendations = self.ml_service.predict_crop(farm_data)
            
            # Get market data for enhancement
            market_data = await self.market_service.get_mandi_prices_with_fallback(district)
            
            enhanced_recommendations = []
            
            for rec in base_recommendations[:5]:  # Top 5 crops
                try:
                    crop_name = rec.get('crop', '')
                    logger.info(f"Processing crop: {crop_name}")
                    
                    # Find market price for this crop
                    market_price_info = self._find_crop_market_data(crop_name, market_data)
                    
                    # Calculate profit potential
                    profit_info = await self._calculate_profit_potential(
                        crop_name, rec, market_price_info, farm_data
                    ) if include_profit_analysis else {}
                    
                    # Enhance recommendation with market data
                    enhanced_rec = {
                        **rec,
                        'market_data': market_price_info,
                        'profit_analysis': profit_info,
                        'market_score': self._calculate_market_score(market_price_info),
                        'combined_score': self._calculate_combined_score(rec, market_price_info),
                        'recommendation_type': 'market_enhanced'
                    }
                    
                    enhanced_recommendations.append(enhanced_rec)
                    
                except Exception as e:
                    logger.error(f"Error processing crop {crop_name}: {e}")
                    # Add basic recommendation without market enhancement
                    enhanced_recommendations.append({
                        **rec,
                        'market_score': 0.5,
                        'combined_score': rec.get('suitability_score', 0.5),
                        'recommendation_type': 'fallback'
                    })
            
            # Sort by combined score (suitability + market potential)
            enhanced_recommendations.sort(
                key=lambda x: x.get('combined_score', 0), 
                reverse=True
            )
            
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Market-enhanced recommendations failed: {e}")
            # Fallback to base recommendations
            base_recs = self.ml_service.predict_crop(farm_data)
            return [{'recommendation_type': 'fallback', **rec} for rec in base_recs[:5]]
    
    def _find_crop_market_data(self, crop_name: str, market_data: Dict) -> Dict[str, Any]:
        """Find market data for a specific crop."""
        if not market_data or 'data' not in market_data:
            return self._get_default_market_data(crop_name)
        
        prices = market_data['data'].get('prices', [])
        
        # Find exact match or similar crop
        crop_variations = [
            crop_name,
            crop_name.lower(),
            crop_name.title(),
            crop_name.upper()
        ]
        
        for price_entry in prices:
            if price_entry.get('crop', '').lower() in [v.lower() for v in crop_variations]:
                return {
                    'current_price': price_entry.get('modal_price', 0),
                    'min_price': price_entry.get('min_price', 0),
                    'max_price': price_entry.get('max_price', 0),
                    'trend': price_entry.get('trend', 'Stable'),
                    'market_name': price_entry.get('market', 'Unknown'),
                    'last_updated': price_entry.get('date'),
                    'data_source': market_data['data'].get('data_source', 'unknown'),
                    'reliability': market_data['data'].get('reliability', 'medium')
                }
        
        return self._get_default_market_data(crop_name)
    
    def _get_default_market_data(self, crop_name: str) -> Dict[str, Any]:
        """Get default market data when real data is unavailable."""
        default_prices = {
            'rice': 2000, 'wheat': 2100, 'maize': 1600, 'potato': 1000,
            'arhar': 6000, 'groundnut': 5000, 'soybean': 4000, 'cotton': 5500,
            'sugarcane': 350, 'mustard': 4500, 'gram': 5200, 'turmeric': 8500
        }
        
        base_price = default_prices.get(crop_name.lower(), 2500)
        
        return {
            'current_price': base_price,
            'min_price': int(base_price * 0.9),
            'max_price': int(base_price * 1.1),
            'trend': 'Stable',
            'market_name': 'Default Market',
            'last_updated': datetime.now().isoformat(),
            'data_source': 'default',
            'reliability': 'low'
        }
    
    async def _calculate_profit_potential(
        self, 
        crop_name: str, 
        crop_rec: Dict, 
        market_data: Dict,
        farm_data: Dict
    ) -> Dict[str, Any]:
        """Calculate profit potential for a crop."""
        try:
            # Get expected yield (from ML prediction or estimate)
            expected_yield = crop_rec.get('expected_yield_per_hectare', 
                                        self._estimate_yield(crop_name, farm_data))
            
            # Calculate revenue
            current_price = market_data.get('current_price', 0)
            gross_revenue = expected_yield * current_price
            
            # Estimate production costs (simplified)
            production_costs = self._estimate_production_costs(crop_name, farm_data)
            
            # Calculate profit metrics
            net_profit = gross_revenue - production_costs
            profit_margin = (net_profit / gross_revenue * 100) if gross_revenue > 0 else 0
            roi = (net_profit / production_costs * 100) if production_costs > 0 else 0
            
            return {
                'expected_yield_quintal': expected_yield,
                'current_market_price': current_price,
                'gross_revenue': round(gross_revenue, 2),
                'estimated_costs': round(production_costs, 2),
                'net_profit': round(net_profit, 2),
                'profit_margin_percent': round(profit_margin, 2),
                'roi_percent': round(roi, 2),
                'profitability_score': self._calculate_profitability_score(
                    profit_margin, roi, market_data.get('trend', 'Stable')
                )
            }
            
        except Exception as e:
            logger.error(f"Profit calculation failed for {crop_name}: {e}")
            return {'error': 'Profit calculation unavailable'}
    
    def _estimate_yield(self, crop_name: str, farm_data: Dict) -> float:
        """Estimate crop yield based on farm conditions."""
        # Base yields per hectare (in quintals)
        base_yields = {
            'rice': 45, 'wheat': 35, 'maize': 40, 'potato': 200,
            'arhar': 15, 'groundnut': 20, 'soybean': 18, 'cotton': 20,
            'sugarcane': 700, 'mustard': 12, 'gram': 18, 'turmeric': 25
        }
        
        base_yield = base_yields.get(crop_name.lower(), 25)
        
        # Adjust based on soil quality and conditions
        soil_quality_multiplier = farm_data.get('soil_quality_score', 0.8)
        climate_suitability = farm_data.get('climate_suitability', 0.8)
        
        adjusted_yield = base_yield * soil_quality_multiplier * climate_suitability
        
        return round(adjusted_yield, 2)
    
    def _estimate_production_costs(self, crop_name: str, farm_data: Dict) -> float:
        """Estimate production costs per hectare."""
        # Base costs per hectare (in INR)
        base_costs = {
            'rice': 35000, 'wheat': 30000, 'maize': 25000, 'potato': 80000,
            'arhar': 28000, 'groundnut': 32000, 'soybean': 24000, 'cotton': 45000,
            'sugarcane': 120000, 'mustard': 22000, 'gram': 26000, 'turmeric': 55000
        }
        
        base_cost = base_costs.get(crop_name.lower(), 30000)
        
        # Adjust based on farm characteristics
        field_size = farm_data.get('field_size', 1)
        irrigation_multiplier = 1.2 if farm_data.get('irrigation', False) else 1.0
        
        # Economies of scale for larger farms
        scale_multiplier = max(0.8, 1 - (field_size - 1) * 0.05)
        
        adjusted_cost = base_cost * irrigation_multiplier * scale_multiplier
        
        return round(adjusted_cost, 2)
    
    def _calculate_profitability_score(self, profit_margin: float, roi: float, trend: str) -> float:
        """Calculate a normalized profitability score (0-1)."""
        # Ensure values are not None
        profit_margin = profit_margin if profit_margin is not None else 0
        roi = roi if roi is not None else 0
        
        # Base score from profit margin and ROI
        base_score = min(1.0, (profit_margin + roi) / 100)
        
        # Trend adjustment
        trend_multiplier = {
            'Rising': 1.1,
            'Stable': 1.0,
            'Falling': 0.9
        }.get(trend, 1.0)
        
        return round(min(1.0, base_score * trend_multiplier), 3)
    
    def _calculate_market_score(self, market_data: Dict) -> float:
        """Calculate market attractiveness score (0-1)."""
        try:
            current_price = market_data.get('current_price', 0) or 0
            min_price = market_data.get('min_price', current_price) or current_price
            max_price = market_data.get('max_price', current_price) or current_price
            trend = market_data.get('trend', 'Stable')
            reliability = market_data.get('reliability', 'medium')
            
            # Ensure all prices are numeric
            current_price = float(current_price) if current_price else 0
            min_price = float(min_price) if min_price else current_price
            max_price = float(max_price) if max_price else current_price
            
            # Price position score (where current price sits in min-max range)
            if max_price > min_price and max_price > 0:
                price_position = (current_price - min_price) / (max_price - min_price)
            else:
                price_position = 0.5
            
            # Trend score
            trend_scores = {'Rising': 0.8, 'Stable': 0.6, 'Falling': 0.3}
            trend_score = trend_scores.get(trend, 0.5)
            
            # Reliability score
            reliability_scores = {'high': 1.0, 'medium': 0.8, 'low': 0.6}
            reliability_score = reliability_scores.get(reliability, 0.7)
            
            # Combined market score
            market_score = (price_position * 0.4 + trend_score * 0.4 + reliability_score * 0.2)
            
            return round(market_score, 3)
            
        except Exception as e:
            logger.error(f"Market score calculation failed: {e}")
            return 0.5
    
    def _calculate_combined_score(self, crop_rec: Dict, market_data: Dict) -> float:
        """Calculate combined suitability + market score."""
        try:
            # Get ML suitability score
            suitability_score = crop_rec.get('suitability_score', 0.5)
            
            # Get market score
            market_score = self._calculate_market_score(market_data)
            
            # Combined score (60% suitability, 40% market potential)
            combined_score = (suitability_score * 0.6) + (market_score * 0.4)
            
            return round(combined_score, 3)
            
        except Exception as e:
            logger.error(f"Combined score calculation failed: {e}")
            return crop_rec.get('suitability_score', 0.5)


# Global instance
market_aware_ml_service = MarketAwareMLService()


def get_market_aware_ml_service() -> MarketAwareMLService:
    """Get the global market-aware ML service instance."""
    return market_aware_ml_service