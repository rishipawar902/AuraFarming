"""
🔧 Compatible Feature Engineering for Production & Explainability
Matches exactly the feature engineering used in training models.
Enhanced for SHAP explainability support.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CompatibleFeatureEngineer:
    """Feature engineering that matches the training process exactly."""
    
    def __init__(self):
        self.label_encoders = {}
        self.feature_names = self._get_feature_names()
    
    def _get_feature_names(self) -> list:
        """Get consistent feature names for explainability - matches training exactly."""
        return [
            # Original features
            'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall',
            
            # Nutrient ratios
            'N_P_ratio', 'N_K_ratio', 'P_K_ratio',
            
            # Total nutrients
            'total_NPK', 'NPK_balance',
            
            # Environmental indices
            'heat_humidity_index', 'water_stress_index', 'ph_optimality',
            
            # Soil fertility indicators
            'fertility_score', 'ph_category',
            
            # Climate suitability
            'temp_optimal', 'humidity_optimal',
            
            # Interaction features
            'N_temp_interaction', 'P_ph_interaction', 'K_rainfall_interaction',
            
            # Polynomial features
            'N_squared', 'P_squared', 'rainfall_log',
            
            # Growing degree days
            'growing_degree_days',
            
            # Nutrient efficiency
            'N_efficiency', 'P_efficiency',
            
            # Stress indicators
            'drought_stress', 'heat_stress', 'cold_stress',
            
            # Advanced interactions
            'climate_fertility', 'water_nutrient'
        ]
    
    def create_features(self, data):
        """Create features exactly as done in training."""
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
        
        # Create all engineered features to match training exactly
        features = df.copy()
        
        # Nutrient ratios
        features['N_P_ratio'] = features['N'] / (features['P'] + 1e-8)
        features['N_K_ratio'] = features['N'] / (features['K'] + 1e-8)
        features['P_K_ratio'] = features['P'] / (features['K'] + 1e-8)
        
        # Total nutrients
        features['total_NPK'] = features['N'] + features['P'] + features['K']
        features['NPK_balance'] = features[['N', 'P', 'K']].std(axis=1)
        
        # Environmental indices
        features['heat_humidity_index'] = features['temperature'] * features['humidity'] / 100
        features['water_stress_index'] = features['rainfall'] / (features['temperature'] + 1e-8)
        features['ph_optimality'] = np.abs(features['ph'] - 6.5)  # Distance from neutral
        
        # Soil fertility indicators
        features['fertility_score'] = (features['N'] + features['P'] + features['K']) / 3
        features['ph_category'] = pd.cut(features['ph'], bins=[0, 6.0, 7.0, 14], labels=[0, 1, 2])
        features['ph_category'] = features['ph_category'].astype(float)  # Convert to numeric
        
        # Climate suitability
        features['temp_optimal'] = np.exp(-0.5 * ((features['temperature'] - 25) / 10) ** 2)
        features['humidity_optimal'] = np.exp(-0.5 * ((features['humidity'] - 70) / 20) ** 2)
        
        # Interaction features
        features['N_temp_interaction'] = features['N'] * features['temperature']
        features['P_ph_interaction'] = features['P'] * features['ph']
        features['K_rainfall_interaction'] = features['K'] * features['rainfall']
        
        # Polynomial features for key nutrients
        features['N_squared'] = features['N'] ** 2
        features['P_squared'] = features['P'] ** 2
        features['rainfall_log'] = np.log1p(features['rainfall'])
        
        # Growing degree days approximation
        features['growing_degree_days'] = np.maximum(0, features['temperature'] - 10) * 30
        
        # Nutrient efficiency ratios
        features['N_efficiency'] = features['N'] / (features['rainfall'] + 1e-8)
        features['P_efficiency'] = features['P'] / (features['ph'] + 1e-8)
        
        # Stress indicators
        features['drought_stress'] = 1 / (features['rainfall'] + 1e-8)
        features['heat_stress'] = np.maximum(0, features['temperature'] - 35)
        features['cold_stress'] = np.maximum(0, 10 - features['temperature'])
        
        # Advanced interactions
        features['climate_fertility'] = features['fertility_score'] * features['temp_optimal']
        features['water_nutrient'] = features['rainfall'] * features['total_NPK']
        
        # Return only the exact features used in training
        result = features[self.feature_names].fillna(0)
        
        return result
    
    def get_feature_names(self):
        """Get list of feature names in processing order."""
        return self.feature_names.copy()
    
    def get_feature_categories(self):
        """Get features grouped by agricultural categories."""
        return {
            'nutrients': ['N', 'P', 'K', 'N_P_ratio', 'N_K_ratio', 'P_K_ratio', 'total_NPK', 'NPK_balance', 'fertility_score'],
            'climate': ['temperature', 'humidity', 'rainfall', 'heat_humidity_index', 'water_stress_index', 'temp_optimal', 'humidity_optimal'],
            'soil': ['ph', 'ph_optimality', 'ph_category'],
            'interactions': ['N_temp_interaction', 'P_ph_interaction', 'K_rainfall_interaction', 'climate_fertility', 'water_nutrient'],
            'derived': ['N_squared', 'P_squared', 'rainfall_log', 'growing_degree_days', 'N_efficiency', 'P_efficiency'],
            'stress': ['drought_stress', 'heat_stress', 'cold_stress']
        }
        """Get features grouped by agricultural categories."""
        return {
            'nutrients': ['N', 'P', 'K', 'npk_ratio', 'npk_balance', 'nutrient_density'],
            'climate': ['temperature', 'humidity', 'rainfall', 'climate_index', 'temperature_humidity_interaction'],
            'soil': ['ph', 'organic_matter', 'soil_moisture', 'soil_health_index', 'ph_nutrient_interaction', 'soil_type'],
            'management': ['irrigation_frequency', 'fertilizer_usage', 'pesticide_usage', 'rainfall_irrigation_ratio'],
            'season': ['crop_season']
        }