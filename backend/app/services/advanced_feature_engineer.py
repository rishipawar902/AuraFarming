"""
Advanced Feature Engineering Pipeline for Agricultural AI
Enhanced with soil-climate interactions and agricultural intelligence
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import logging
from datetime import datetime, timedelta
import asyncio

# AuraFarming imports
from app.services.weather_service import weather_service
from app.core.districts import JHARKHAND_DISTRICTS

logger = logging.getLogger(__name__)


class AdvancedFeatureEngineer:
    """
    Advanced feature engineering for agricultural machine learning with enhanced intelligence.
    Creates 50+ domain-specific features including soil-climate interactions.
    """
    
    def __init__(self):
        """Initialize advanced feature engineer."""
        
        # Enhanced crop optimal ranges with more parameters
        self.crop_optimal_ranges = {
            'Rice': {
                'temperature': (20, 35), 'humidity': (70, 85), 'rainfall': (1000, 1500),
                'soil_ph': (5.5, 7.0), 'nitrogen': (80, 120), 'phosphorus': (30, 50),
                'potassium': (40, 60), 'water_requirement': 'high', 'soil_drainage': 'poor'
            },
            'Maize': {
                'temperature': (21, 30), 'humidity': (60, 75), 'rainfall': (600, 1200),
                'soil_ph': (6.0, 7.5), 'nitrogen': (100, 150), 'phosphorus': (40, 70),
                'potassium': (60, 80), 'water_requirement': 'medium', 'soil_drainage': 'good'
            },
            'Wheat': {
                'temperature': (15, 25), 'humidity': (50, 70), 'rainfall': (300, 600),
                'soil_ph': (6.0, 7.5), 'nitrogen': (60, 100), 'phosphorus': (25, 45),
                'potassium': (30, 50), 'water_requirement': 'low', 'soil_drainage': 'good'
            },
            'Sugarcane': {
                'temperature': (25, 32), 'humidity': (75, 90), 'rainfall': (1200, 2000),
                'soil_ph': (6.0, 8.0), 'nitrogen': (150, 200), 'phosphorus': (50, 80),
                'potassium': (80, 120), 'water_requirement': 'very_high', 'soil_drainage': 'good'
            }
        }
        
        # Soil type characteristics for Jharkhand
        self.soil_characteristics = {
            'Red Soil': {
                'drainage': 'good', 'fertility': 'medium', 'ph_tendency': 'acidic',
                'water_retention': 'medium', 'nutrient_leaching': 'high'
            },
            'Laterite Soil': {
                'drainage': 'excellent', 'fertility': 'low', 'ph_tendency': 'acidic',
                'water_retention': 'low', 'nutrient_leaching': 'very_high'
            },
            'Alluvial Soil': {
                'drainage': 'medium', 'fertility': 'high', 'ph_tendency': 'neutral',
                'water_retention': 'high', 'nutrient_leaching': 'low'
            },
            'Black Soil': {
                'drainage': 'poor', 'fertility': 'high', 'ph_tendency': 'neutral',
                'water_retention': 'very_high', 'nutrient_leaching': 'very_low'
            }
        }
        
        # Seasonal factors for Jharkhand
        self.seasonal_factors = {
            'Kharif': {'months': [6, 7, 8, 9], 'rainfall_importance': 'critical'},
            'Rabi': {'months': [11, 12, 1, 2], 'temperature_importance': 'critical'},
            'Zaid': {'months': [3, 4, 5], 'irrigation_importance': 'critical'}
        }
        
        # Nutrient interaction matrix
        self.nutrient_interactions = {
            'N-P': 'synergistic',  # Nitrogen and Phosphorus enhance each other
            'N-K': 'synergistic',  # Nitrogen and Potassium work together
            'P-K': 'neutral',      # Phosphorus and Potassium don't interact strongly
        }
    
    def prepare_feature_matrix(self, farm_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Create comprehensive feature matrix with 50+ advanced features
        
        Args:
            farm_data: Farm input data
            
        Returns:
            Feature matrix with advanced agricultural features
        """
        try:
            # Validate required fields
            required_fields = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 
                             'humidity', 'soil_ph', 'rainfall']
            
            for field in required_fields:
                if field not in farm_data:
                    logger.error(f"Required field '{field}' missing from farm_data")
                    return None
            
            # Create base features
            features = self.create_basic_features(farm_data)
            
            # Add advanced soil-climate interaction features
            features.update(self.create_soil_climate_features(farm_data))
            
            # Add agricultural intelligence features
            features.update(self.create_agricultural_intelligence_features(farm_data))
            
            # Add economic and risk features
            features.update(self.create_economic_features(farm_data))
            
            # Add seasonal adaptation features
            features.update(self.create_seasonal_features(farm_data))
            
            # Convert to DataFrame
            feature_df = pd.DataFrame([features])
            
            logger.info(f"✅ Created feature matrix with {len(features)} features")
            return feature_df
            
        except Exception as e:
            logger.error(f"❌ Error creating feature matrix: {e}")
            return None
    
    def create_basic_features(self, farm_data: Dict[str, Any]) -> Dict[str, float]:
        """Create basic agricultural features"""
        
        features = {}
        
        # Extract basic parameters
        N = float(farm_data.get('nitrogen', 0))
        P = float(farm_data.get('phosphorus', 0))
        K = float(farm_data.get('potassium', 0))
        temp = float(farm_data.get('temperature', 25))
        humidity = float(farm_data.get('humidity', 65))
        ph = float(farm_data.get('soil_ph', 6.5))
        rainfall = float(farm_data.get('rainfall', 800))
        
        # Basic features
        features.update({
            'nitrogen': N, 'phosphorus': P, 'potassium': K,
            'temperature': temp, 'humidity': humidity, 
            'soil_ph': ph, 'rainfall': rainfall
        })
        
        # Nutrient ratios (critical for crop selection)
        features.update({
            'n_p_ratio': N / (P + 1e-6),
            'n_k_ratio': N / (K + 1e-6),
            'p_k_ratio': P / (K + 1e-6),
            'npk_balance': (N * P * K) ** (1/3),  # Geometric mean
            'total_nutrients': N + P + K,
        })
        
        # Climate indices
        features.update({
            'temp_humidity_index': temp * (humidity / 100),
            'heat_stress_index': max(0, temp - 30),
            'moisture_stress_index': max(0, 50 - humidity),
            'rainfall_intensity': rainfall / 365,  # Daily average
        })
        
        # Soil health indicators
        features.update({
            'ph_optimality': 1 - abs(ph - 6.5) / 3.5,  # Distance from optimal pH
            'nutrient_adequacy_n': min(1.0, N / 100),
            'nutrient_adequacy_p': min(1.0, P / 50),
            'nutrient_adequacy_k': min(1.0, K / 50),
        })
        
        return features
    
    def create_soil_climate_features(self, farm_data: Dict[str, Any]) -> Dict[str, float]:
        """Create soil-climate interaction features"""
        
        features = {}
        soil_type = farm_data.get('soil_type', 'Red Soil')
        
        # Get soil characteristics
        soil_chars = self.soil_characteristics.get(soil_type, self.soil_characteristics['Red Soil'])
        
        # Soil type encoding (one-hot style)
        for soil in self.soil_characteristics.keys():
            features[f'soil_{soil.lower().replace(" ", "_")}'] = 1.0 if soil_type == soil else 0.0
        
        # Soil-climate interactions
        temp = float(farm_data.get('temperature', 25))
        humidity = float(farm_data.get('humidity', 65))
        rainfall = float(farm_data.get('rainfall', 800))
        
        # Drainage interaction with rainfall
        drainage_scores = {'poor': 0.2, 'medium': 0.5, 'good': 0.8, 'excellent': 1.0}
        drainage_score = drainage_scores.get(soil_chars['drainage'], 0.5)
        features['soil_rainfall_suitability'] = drainage_score * min(1.0, rainfall / 1000)
        
        # Water retention vs. drought stress
        retention_scores = {'low': 0.2, 'medium': 0.5, 'high': 0.8, 'very_high': 1.0}
        retention_score = retention_scores.get(soil_chars['water_retention'], 0.5)
        features['drought_resilience'] = retention_score * (humidity / 100)
        
        # Fertility interaction with nutrients
        fertility_scores = {'low': 0.3, 'medium': 0.6, 'high': 1.0}
        fertility_score = fertility_scores.get(soil_chars['fertility'], 0.6)
        features['soil_fertility_score'] = fertility_score
        
        # pH tendency effects
        ph = float(farm_data.get('soil_ph', 6.5))
        if soil_chars['ph_tendency'] == 'acidic':
            features['ph_soil_compatibility'] = max(0, 7.0 - ph) / 2.0
        elif soil_chars['ph_tendency'] == 'neutral':
            features['ph_soil_compatibility'] = 1.0 - abs(ph - 6.8) / 2.0
        else:  # alkaline
            features['ph_soil_compatibility'] = max(0, ph - 6.0) / 2.0
        
        # Nutrient leaching risk
        leaching_scores = {'very_low': 0.1, 'low': 0.3, 'medium': 0.5, 'high': 0.7, 'very_high': 0.9}
        leaching_risk = leaching_scores.get(soil_chars['nutrient_leaching'], 0.5)
        features['nutrient_leaching_risk'] = leaching_risk * (rainfall / 1000)
        
        return features
    
    def create_agricultural_intelligence_features(self, farm_data: Dict[str, Any]) -> Dict[str, float]:
        """Create agricultural intelligence and crop suitability features"""
        
        features = {}
        
        # Extract parameters
        N = float(farm_data.get('nitrogen', 0))
        P = float(farm_data.get('phosphorus', 0))
        K = float(farm_data.get('potassium', 0))
        temp = float(farm_data.get('temperature', 25))
        humidity = float(farm_data.get('humidity', 65))
        rainfall = float(farm_data.get('rainfall', 800))
        ph = float(farm_data.get('soil_ph', 6.5))
        
        # Crop suitability scores for major crops
        for crop, ranges in self.crop_optimal_ranges.items():
            suitability_scores = []
            
            # Temperature suitability
            temp_min, temp_max = ranges['temperature']
            temp_suit = 1.0 if temp_min <= temp <= temp_max else max(0, 1.0 - abs(temp - (temp_min + temp_max)/2) / 10)
            suitability_scores.append(temp_suit)
            
            # Humidity suitability
            hum_min, hum_max = ranges['humidity']
            hum_suit = 1.0 if hum_min <= humidity <= hum_max else max(0, 1.0 - abs(humidity - (hum_min + hum_max)/2) / 20)
            suitability_scores.append(hum_suit)
            
            # Rainfall suitability
            rain_min, rain_max = ranges['rainfall']
            rain_suit = 1.0 if rain_min <= rainfall <= rain_max else max(0, 1.0 - abs(rainfall - (rain_min + rain_max)/2) / 500)
            suitability_scores.append(rain_suit)
            
            # pH suitability
            ph_min, ph_max = ranges['soil_ph']
            ph_suit = 1.0 if ph_min <= ph <= ph_max else max(0, 1.0 - abs(ph - (ph_min + ph_max)/2))
            suitability_scores.append(ph_suit)
            
            # Nitrogen suitability
            n_min, n_max = ranges['nitrogen']
            n_suit = 1.0 if n_min <= N <= n_max else max(0, 1.0 - abs(N - (n_min + n_max)/2) / 50)
            suitability_scores.append(n_suit)
            
            # Overall suitability (geometric mean for conservative estimate)
            overall_suitability = np.prod(suitability_scores) ** (1/len(suitability_scores))
            features[f'{crop.lower()}_suitability'] = overall_suitability
        
        # Nutrient interaction effects
        features['n_p_synergy'] = min(N/100, P/50) * 1.2  # Synergistic effect
        features['n_k_synergy'] = min(N/100, K/50) * 1.1  # Synergistic effect
        features['npk_balanced_score'] = 1.0 - np.std([N/100, P/50, K/50])  # Balance score
        
        # Stress indicators
        features['temperature_stress'] = max(0, temp - 35) + max(0, 10 - temp)
        features['water_stress'] = max(0, 30 - humidity) + max(0, rainfall - 2000) / 1000
        features['nutrient_stress'] = max(0, 1.0 - (N + P + K) / 200)
        
        return features
    
    def create_economic_features(self, farm_data: Dict[str, Any]) -> Dict[str, float]:
        """Create economic and profitability features"""
        
        features = {}
        
        # Input cost estimates (simplified)
        N = float(farm_data.get('nitrogen', 0))
        P = float(farm_data.get('phosphorus', 0))
        K = float(farm_data.get('potassium', 0))
        
        # Fertilizer cost estimation (₹/kg approximation)
        fertilizer_cost = (N * 20 + P * 30 + K * 25) / 1000  # Convert to thousands
        features['fertilizer_cost_estimate'] = fertilizer_cost
        
        # Input efficiency ratios
        features['nutrient_cost_efficiency'] = (N + P + K) / (fertilizer_cost + 1e-6)
        
        # Water requirement vs. availability
        rainfall = float(farm_data.get('rainfall', 800))
        features['irrigation_need_score'] = max(0, (1000 - rainfall) / 1000)
        
        # Risk factors
        temp = float(farm_data.get('temperature', 25))
        humidity = float(farm_data.get('humidity', 65))
        
        features['climate_risk_score'] = (
            (max(0, temp - 35) / 10) +  # Heat risk
            (max(0, 10 - temp) / 10) +  # Cold risk
            (max(0, 30 - humidity) / 30)  # Drought risk
        ) / 3
        
        return features
    
    def create_seasonal_features(self, farm_data: Dict[str, Any]) -> Dict[str, float]:
        """Create seasonal adaptation features"""
        
        features = {}
        current_month = datetime.now().month
        
        # Season identification
        for season, info in self.seasonal_factors.items():
            is_season = 1.0 if current_month in info['months'] else 0.0
            features[f'season_{season.lower()}'] = is_season
        
        # Seasonal suitability for current conditions
        temp = float(farm_data.get('temperature', 25))
        rainfall = float(farm_data.get('rainfall', 800))
        
        # Kharif season suitability (monsoon crops)
        kharif_temp_suit = 1.0 if 25 <= temp <= 35 else max(0, 1.0 - abs(temp - 30) / 10)
        kharif_rain_suit = 1.0 if rainfall >= 800 else rainfall / 800
        features['kharif_suitability'] = (kharif_temp_suit * kharif_rain_suit) ** 0.5
        
        # Rabi season suitability (winter crops)
        rabi_temp_suit = 1.0 if 15 <= temp <= 25 else max(0, 1.0 - abs(temp - 20) / 10)
        rabi_rain_suit = 1.0 if 300 <= rainfall <= 800 else max(0, 1.0 - abs(rainfall - 550) / 500)
        features['rabi_suitability'] = (rabi_temp_suit * rabi_rain_suit) ** 0.5
        
        # Zaid season suitability (summer crops with irrigation)
        zaid_temp_suit = 1.0 if 25 <= temp <= 32 else max(0, 1.0 - abs(temp - 28) / 8)
        zaid_irrigation_need = max(0, (1000 - rainfall) / 1000)  # Higher need = better for Zaid
        features['zaid_suitability'] = (zaid_temp_suit * zaid_irrigation_need) ** 0.5
        
        return features
    
    async def integrate_weather_features(self, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate real-time weather data with farm data
        
        Args:
            farm_data: Farm input data
            
        Returns:
            Enhanced farm data with weather features
        """
        enhanced_data = farm_data.copy()
        
        try:
            latitude = farm_data.get('latitude')
            longitude = farm_data.get('longitude')
            
            if latitude and longitude:
                # Get current weather
                weather_data = await weather_service.get_current_weather(
                    latitude=latitude,
                    longitude=longitude
                )
                
                if weather_data and weather_data.get('success'):
                    ml_data = weather_data.get('data', {})
                    
                    # Update with real-time weather
                    enhanced_data['current_temperature'] = ml_data.get('temperature', farm_data.get('temperature', 25))
                    enhanced_data['current_humidity'] = ml_data.get('humidity', farm_data.get('humidity', 65))
                    enhanced_data['current_pressure'] = ml_data.get('pressure', 1013)
                    enhanced_data['wind_speed'] = ml_data.get('wind_speed', 5)
                    
                    # Weather-based features
                    enhanced_data['weather_stress_index'] = (
                        max(0, enhanced_data['current_temperature'] - 35) +
                        max(0, 30 - enhanced_data['current_humidity'])
                    ) / 2
                    
                    logger.info("✅ Successfully integrated real-time weather data")
                else:
                    logger.warning("⚠️  Weather API returned no data, using defaults")
            else:
                logger.warning("⚠️  No coordinates provided, skipping weather integration")
                
                # Use base rainfall from farm data or reasonable default
                base_rainfall = farm_data.get('rainfall', 800)
                enhanced_data['current_temperature'] = farm_data.get('temperature', 25)
                enhanced_data['current_humidity'] = farm_data.get('humidity', 65)
                
        except Exception as e:
            logger.error(f"❌ Error integrating weather data: {e}")
            # Continue with original data
            
        return enhanced_data

# Global instance
advanced_feature_engineer = AdvancedFeatureEngineer()