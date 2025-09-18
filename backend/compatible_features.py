"""
🔧 Compatible Feature Engineering for Production & Explainability
Matches exactly the feature engineering used in training models.
Enhanced for SHAP explainability support.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CompatibleFeatureEngineer:
    """Feature engineering that matches the training process exactly."""
    
    def __init__(self):
        self.feature_names = self._get_feature_names()
    
    def _get_feature_names(self) -> list:
        """Get exact feature names from the trained models - 29 features."""
        return [
            'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 
            'organic_matter', 'soil_moisture', 'irrigation_frequency', 
            'fertilizer_usage', 'pesticide_usage', 'soil_type_encoded', 
            'crop_season_encoded', 'np_ratio', 'nk_ratio', 'pk_ratio', 
            'npk_sum', 'npk_product', 'heat_index', 'drought_stress', 
            'moisture_balance', 'ph_optimal', 'nutrient_balance', 
            'soil_quality', 'nutrient_efficiency', 'water_stress', 
            'water_management', 'fertilizer_efficiency'
        ]
    
    def create_features(self, data):
        """Create features exactly as done in original production training."""
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()
        
        # Ensure all base features are present
        base_features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        for feature in base_features:
            if feature not in df.columns:
                # Set reasonable defaults
                defaults = {'N': 40, 'P': 50, 'K': 45, 'temperature': 25, 'humidity': 60, 'ph': 6.5, 'rainfall': 100}
                df[feature] = defaults.get(feature, 0)
        
        # Add extended features with defaults if not present
        extended_features = {
            'organic_matter': 3.5,
            'soil_moisture': 65.0,
            'irrigation_frequency': 2,
            'fertilizer_usage': 150.0,
            'pesticide_usage': 5.0,
            'soil_type': 'loamy',
            'crop_season': 'Kharif'
        }
        
        for col, default_val in extended_features.items():
            if col not in df.columns:
                df[col] = default_val
        
        # Create all engineered features to match original production
        features = df.copy()
        
        # Encode categorical features (matching original training)
        # soil_type_encoded: loamy=0, sandy=1, clay=2, silt=3
        soil_type_mapping = {'loamy': 0, 'sandy': 1, 'clay': 2, 'silt': 3}
        features['soil_type_encoded'] = features['soil_type'].map(soil_type_mapping).fillna(0)
        
        # crop_season_encoded: Kharif=0, Rabi=1, Zaid=2
        season_mapping = {'Kharif': 0, 'Rabi': 1, 'Zaid': 2}
        features['crop_season_encoded'] = features['crop_season'].map(season_mapping).fillna(0)
        
        # NPK ratios and interactions (matching original)
        features['np_ratio'] = features['N'] / (features['P'] + 1)
        features['nk_ratio'] = features['N'] / (features['K'] + 1)
        features['pk_ratio'] = features['P'] / (features['K'] + 1)
        features['npk_sum'] = features['N'] + features['P'] + features['K']
        features['npk_product'] = features['N'] * features['P'] * features['K']
        
        # Climate indices (matching original)
        features['heat_index'] = features['temperature'] * features['humidity'] / 100
        features['drought_stress'] = (features['temperature'] - 20) / (features['rainfall'] + 1)
        features['moisture_balance'] = features['humidity'] * features['rainfall'] / (features['temperature'] + 1)
        
        # Soil health indicators (matching original)
        features['ph_optimal'] = np.abs(features['ph'] - 6.5)  # Distance from optimal pH
        features['nutrient_balance'] = np.sqrt(features['N']**2 + features['P']**2 + features['K']**2)
        
        # Additional features based on available columns (matching original)
        features['soil_quality'] = features['organic_matter'] * (7 - features['ph_optimal'])
        features['nutrient_efficiency'] = features['npk_sum'] * features['organic_matter']
        features['water_stress'] = np.abs(features['soil_moisture'] - 60)  # Optimal around 60%
        features['water_management'] = features['irrigation_frequency'] * features['soil_moisture']
        features['fertilizer_efficiency'] = features['npk_sum'] / (features['fertilizer_usage'] + 1)
        
        # Return only the exact features used in training
        result = features[self.feature_names].fillna(0)
        
        return result
    
    def get_feature_names(self):
        """Get list of feature names in processing order."""
        return self.feature_names.copy()
    
    def get_feature_categories(self):
        """Get features grouped by agricultural categories."""
        return {
            'basic': ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'],
            'soil_management': ['organic_matter', 'soil_moisture', 'irrigation_frequency', 'fertilizer_usage', 'pesticide_usage'],
            'categorical': ['soil_type_encoded', 'crop_season_encoded'],
            'nutrient_ratios': ['np_ratio', 'nk_ratio', 'pk_ratio', 'npk_sum', 'npk_product'],
            'climate_stress': ['heat_index', 'drought_stress', 'moisture_balance'],
            'soil_health': ['ph_optimal', 'nutrient_balance', 'soil_quality'],
            'efficiency': ['nutrient_efficiency', 'water_management', 'fertilizer_efficiency'],
            'stress_indicators': ['water_stress']
        }