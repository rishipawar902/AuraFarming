"""
Machine Learning service for crop recommendations.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from app.models.schemas import CropRecommendation
from app.core.config import JHARKHAND_CROPS
import random
from datetime import datetime


class MLService:
    """
    Machine Learning service for generating crop recommendations.
    In production, this would use a trained TensorFlow/scikit-learn model.
    """
    
    def __init__(self):
        """Initialize ML service with mock model weights."""
        self.model_weights = self._initialize_mock_weights()
        self.crop_features = self._initialize_crop_features()
    
    def _initialize_mock_weights(self) -> Dict[str, float]:
        """Initialize mock model weights for different features."""
        return {
            "soil_type_weight": 0.25,
            "irrigation_weight": 0.20,
            "field_size_weight": 0.15,
            "season_weight": 0.30,
            "history_weight": 0.10
        }
    
    def _initialize_crop_features(self) -> Dict[str, Dict[str, Any]]:
        """Initialize crop feature mappings."""
        return {
            "Rice": {
                "preferred_soil": ["Alluvial Soil", "Clay Soil"],
                "water_requirement": "High",
                "season": ["Kharif"],
                "min_field_size": 0.5,
                "profit_potential": "Medium",
                "risk_level": "Low"
            },
            "Wheat": {
                "preferred_soil": ["Alluvial Soil", "Loamy Soil"],
                "water_requirement": "Medium",
                "season": ["Rabi"],
                "min_field_size": 1.0,
                "profit_potential": "Medium",
                "risk_level": "Low"
            },
            "Maize": {
                "preferred_soil": ["Alluvial Soil", "Red Soil", "Loamy Soil"],
                "water_requirement": "Medium",
                "season": ["Kharif", "Rabi"],
                "min_field_size": 0.5,
                "profit_potential": "High",
                "risk_level": "Medium"
            },
            "Arhar": {
                "preferred_soil": ["Red Soil", "Black Soil"],
                "water_requirement": "Low",
                "season": ["Kharif"],
                "min_field_size": 0.25,
                "profit_potential": "Medium",
                "risk_level": "Medium"
            },
            "Potato": {
                "preferred_soil": ["Sandy Soil", "Loamy Soil"],
                "water_requirement": "High",
                "season": ["Rabi"],
                "min_field_size": 0.5,
                "profit_potential": "High",
                "risk_level": "High"
            },
            "Sugarcane": {
                "preferred_soil": ["Alluvial Soil", "Clay Soil"],
                "water_requirement": "Very High",
                "season": ["Annual"],
                "min_field_size": 2.0,
                "profit_potential": "Very High",
                "risk_level": "Medium"
            },
            "Groundnut": {
                "preferred_soil": ["Sandy Soil", "Red Soil"],
                "water_requirement": "Medium",
                "season": ["Kharif"],
                "min_field_size": 0.5,
                "profit_potential": "Medium",
                "risk_level": "Medium"
            },
            "Tomato": {
                "preferred_soil": ["Loamy Soil", "Red Soil"],
                "water_requirement": "High",
                "season": ["Rabi", "Kharif"],
                "min_field_size": 0.25,
                "profit_potential": "High",
                "risk_level": "High"
            }
        }
    
    async def get_crop_recommendations(
        self,
        farm_data: Dict[str, Any],
        season: str,
        year: int,
        crop_history: List[Dict[str, Any]] = None
    ) -> List[CropRecommendation]:
        """
        Generate crop recommendations based on farm data and ML model.
        
        Args:
            farm_data: Farm characteristics
            season: Target season
            year: Target year
            crop_history: Historical crop data
            
        Returns:
            List of top 3 crop recommendations
        """
        # Extract farm features
        soil_type = farm_data.get("soil_type")
        irrigation_method = farm_data.get("irrigation_method")
        field_size = farm_data.get("field_size", 1.0)
        location = farm_data.get("location", {})
        
        # Calculate scores for each crop
        crop_scores = {}
        
        for crop, features in self.crop_features.items():
            score = self._calculate_crop_score(
                crop, features, soil_type, irrigation_method, 
                field_size, season, crop_history
            )
            crop_scores[crop] = score
        
        # Sort crops by score and get top 3
        sorted_crops = sorted(crop_scores.items(), key=lambda x: x[1], reverse=True)
        top_crops = sorted_crops[:3]
        
        # Generate recommendations
        recommendations = []
        for i, (crop, score) in enumerate(top_crops):
            recommendation = await self._create_recommendation(
                crop, score, farm_data, season
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_crop_score(
        self,
        crop: str,
        features: Dict[str, Any],
        soil_type: str,
        irrigation_method: str,
        field_size: float,
        season: str,
        crop_history: List[Dict[str, Any]]
    ) -> float:
        """Calculate suitability score for a crop."""
        score = 0.0
        
        # Soil type compatibility
        if soil_type in features.get("preferred_soil", []):
            score += self.model_weights["soil_type_weight"]
        
        # Season compatibility
        if season in features.get("season", []):
            score += self.model_weights["season_weight"]
        
        # Field size adequacy
        min_size = features.get("min_field_size", 0.5)
        if field_size >= min_size:
            score += self.model_weights["field_size_weight"]
        
        # Irrigation compatibility
        water_req = features.get("water_requirement", "Medium")
        irrigation_score = self._calculate_irrigation_score(irrigation_method, water_req)
        score += irrigation_score * self.model_weights["irrigation_weight"]
        
        # Historical performance
        if crop_history:
            history_score = self._calculate_history_score(crop, crop_history)
            score += history_score * self.model_weights["history_weight"]
        
        # Add some randomness for variety
        score += random.uniform(-0.05, 0.05)
        
        return max(0.0, min(1.0, score))
    
    def _calculate_irrigation_score(self, irrigation_method: str, water_requirement: str) -> float:
        """Calculate irrigation compatibility score."""
        irrigation_capacity = {
            "Rain-fed": 0.3,
            "Dug well": 0.5,
            "Tube well": 0.8,
            "Canal": 0.7,
            "Drip irrigation": 0.9,
            "Sprinkler irrigation": 0.8
        }
        
        water_needs = {
            "Low": 0.3,
            "Medium": 0.5,
            "High": 0.8,
            "Very High": 1.0
        }
        
        capacity = irrigation_capacity.get(irrigation_method, 0.5)
        need = water_needs.get(water_requirement, 0.5)
        
        if capacity >= need:
            return 1.0
        else:
            return capacity / need
    
    def _calculate_history_score(self, crop: str, crop_history: List[Dict[str, Any]]) -> float:
        """Calculate score based on historical performance."""
        crop_performances = [
            h for h in crop_history 
            if h.get("crop") == crop and h.get("yield_per_acre")
        ]
        
        if not crop_performances:
            return 0.5  # Neutral score for new crops
        
        # Calculate average yield performance
        avg_yield = sum(h["yield_per_acre"] for h in crop_performances) / len(crop_performances)
        
        # Convert to score (this would use regional benchmarks in production)
        if avg_yield > 20:  # High yield
            return 0.8
        elif avg_yield > 15:  # Medium yield
            return 0.6
        elif avg_yield > 10:  # Low yield
            return 0.4
        else:
            return 0.2
    
    async def _create_recommendation(
        self,
        crop: str,
        score: float,
        farm_data: Dict[str, Any],
        season: str
    ) -> CropRecommendation:
        """Create a detailed crop recommendation."""
        features = self.crop_features.get(crop, {})
        
        # Calculate expected yield based on soil and irrigation
        base_yield = self._calculate_expected_yield(crop, farm_data)
        
        # Generate fertilizer recommendations
        fertilizer_rec = self._generate_fertilizer_recommendation(crop, farm_data)
        
        return CropRecommendation(
            crop_name=crop,
            confidence=round(score, 3),
            expected_yield=round(base_yield, 2),
            profit_potential=features.get("profit_potential", "Medium"),
            risk_level=features.get("risk_level", "Medium"),
            water_requirement=features.get("water_requirement", "Medium"),
            fertilizer_recommendation=fertilizer_rec,
            market_demand=self._assess_market_demand(crop, season)
        )
    
    def _calculate_expected_yield(self, crop: str, farm_data: Dict[str, Any]) -> float:
        """Calculate expected yield per acre."""
        base_yields = {
            "Rice": 18.0,
            "Wheat": 22.0,
            "Maize": 25.0,
            "Arhar": 12.0,
            "Potato": 180.0,
            "Sugarcane": 350.0,
            "Groundnut": 15.0,
            "Tomato": 200.0
        }
        
        base = base_yields.get(crop, 15.0)
        
        # Adjust based on soil and irrigation
        soil_multiplier = {
            "Alluvial Soil": 1.2,
            "Loamy Soil": 1.1,
            "Red Soil": 1.0,
            "Clay Soil": 0.9,
            "Sandy Soil": 0.8,
            "Black Soil": 1.0,
            "Laterite Soil": 0.8
        }
        
        irrigation_multiplier = {
            "Rain-fed": 0.8,
            "Dug well": 0.9,
            "Tube well": 1.1,
            "Canal": 1.0,
            "Drip irrigation": 1.2,
            "Sprinkler irrigation": 1.1
        }
        
        soil_factor = soil_multiplier.get(farm_data.get("soil_type"), 1.0)
        irrigation_factor = irrigation_multiplier.get(farm_data.get("irrigation_method"), 1.0)
        
        return base * soil_factor * irrigation_factor * random.uniform(0.9, 1.1)
    
    def _generate_fertilizer_recommendation(self, crop: str, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fertilizer recommendations."""
        base_recommendations = {
            "Rice": {"N": 120, "P": 60, "K": 40},
            "Wheat": {"N": 100, "P": 50, "K": 30},
            "Maize": {"N": 150, "P": 75, "K": 50},
            "Arhar": {"N": 20, "P": 40, "K": 20},
            "Potato": {"N": 180, "P": 90, "K": 100},
            "Sugarcane": {"N": 250, "P": 125, "K": 125},
            "Groundnut": {"N": 25, "P": 50, "K": 75},
            "Tomato": {"N": 200, "P": 100, "K": 100}
        }
        
        base_npk = base_recommendations.get(crop, {"N": 100, "P": 50, "K": 50})
        
        return {
            "npk_kg_per_acre": base_npk,
            "organic_fertilizer": "5 tonnes/acre farmyard manure",
            "application_schedule": "Split application - 50% at sowing, 30% at 30 days, 20% at 60 days",
            "soil_amendments": "Lime application if pH < 6.0"
        }
    
    def _assess_market_demand(self, crop: str, season: str) -> str:
        """Assess market demand for the crop."""
        demand_levels = ["Very High", "High", "Medium", "Low"]
        
        # Staple crops generally have stable demand
        if crop in ["Rice", "Wheat", "Maize"]:
            return random.choice(["High", "Medium"])
        
        # Cash crops have variable demand
        elif crop in ["Sugarcane", "Potato", "Tomato"]:
            return random.choice(["Very High", "High", "Medium"])
        
        # Pulses and oilseeds
        else:
            return random.choice(demand_levels)