"""
Strategy 2: Soil Type Feature Engineering
Add soil-based features to existing XGBoost model without retraining
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

class SoilTypeFeatureEngineer:
    """Create soil-based features for crop prediction."""
    
    def __init__(self):
        """Initialize soil type feature engineering."""
        
        # Soil property database
        self.soil_properties = {
            'Clay Soil': {
                'water_retention': 0.85,
                'drainage_rate': 0.3,
                'nutrient_holding': 0.9,
                'aeration': 0.4,
                'workability': 0.5,
                'erosion_resistance': 0.8,
                'organic_matter': 0.7,
                'cation_exchange': 0.9
            },
            'Loamy Soil': {
                'water_retention': 0.7,
                'drainage_rate': 0.7,
                'nutrient_holding': 0.8,
                'aeration': 0.8,
                'workability': 0.9,
                'erosion_resistance': 0.6,
                'organic_matter': 0.8,
                'cation_exchange': 0.7
            },
            'Sandy Soil': {
                'water_retention': 0.3,
                'drainage_rate': 0.9,
                'nutrient_holding': 0.4,
                'aeration': 0.9,
                'workability': 0.8,
                'erosion_resistance': 0.3,
                'organic_matter': 0.4,
                'cation_exchange': 0.3
            },
            'Black Soil': {
                'water_retention': 0.8,
                'drainage_rate': 0.4,
                'nutrient_holding': 0.95,
                'aeration': 0.5,
                'workability': 0.6,
                'erosion_resistance': 0.7,
                'organic_matter': 0.8,
                'cation_exchange': 0.95
            },
            'Red Soil': {
                'water_retention': 0.5,
                'drainage_rate': 0.6,
                'nutrient_holding': 0.6,
                'aeration': 0.7,
                'workability': 0.7,
                'erosion_resistance': 0.5,
                'organic_matter': 0.5,
                'cation_exchange': 0.5
            },
            'Alluvial Soil': {
                'water_retention': 0.6,
                'drainage_rate': 0.7,
                'nutrient_holding': 0.8,
                'aeration': 0.7,
                'workability': 0.8,
                'erosion_resistance': 0.6,
                'organic_matter': 0.7,
                'cation_exchange': 0.7
            }
        }
        
        # Crop-soil compatibility matrix
        self.crop_soil_compatibility = {
            'rice': {
                'Clay Soil': 0.9, 'Alluvial Soil': 0.8, 'Loamy Soil': 0.7,
                'Black Soil': 0.6, 'Red Soil': 0.4, 'Sandy Soil': 0.3
            },
            'wheat': {
                'Loamy Soil': 0.9, 'Alluvial Soil': 0.8, 'Black Soil': 0.7,
                'Clay Soil': 0.6, 'Red Soil': 0.5, 'Sandy Soil': 0.4
            },
            'maize': {
                'Loamy Soil': 0.9, 'Black Soil': 0.8, 'Alluvial Soil': 0.7,
                'Clay Soil': 0.6, 'Red Soil': 0.5, 'Sandy Soil': 0.4
            },
            'cotton': {
                'Black Soil': 0.95, 'Clay Soil': 0.8, 'Loamy Soil': 0.6,
                'Alluvial Soil': 0.5, 'Red Soil': 0.4, 'Sandy Soil': 0.3
            }
        }
    
    def create_soil_features(self, soil_type: str, farm_data: Dict[str, Any]) -> Dict[str, float]:
        """Create soil-based features for prediction."""
        
        if soil_type not in self.soil_properties:
            soil_type = 'Loamy Soil'  # Default fallback
        
        soil_props = self.soil_properties[soil_type]
        features = {}
        
        # Direct soil properties
        for prop, value in soil_props.items():
            features[f'soil_{prop}'] = value
        
        # Soil-climate interaction features
        if 'rainfall' in farm_data and 'humidity' in farm_data:
            # Water availability considering soil retention
            water_availability = (
                farm_data['rainfall'] * 0.7 + 
                farm_data['humidity'] * 0.3
            ) * soil_props['water_retention']
            features['soil_water_availability'] = water_availability / 100.0
            
            # Drainage efficiency
            drainage_efficiency = soil_props['drainage_rate'] * (
                1.0 - farm_data['humidity'] / 100.0
            )
            features['soil_drainage_efficiency'] = drainage_efficiency
        
        # Soil-nutrient interaction features
        if all(nutrient in farm_data for nutrient in ['N', 'P', 'K']):
            # Effective nutrient availability
            features['soil_n_effectiveness'] = (
                farm_data['N'] * soil_props['nutrient_holding'] * 
                soil_props['cation_exchange']
            ) / 1000.0
            
            features['soil_p_effectiveness'] = (
                farm_data['P'] * soil_props['nutrient_holding'] * 
                soil_props['cation_exchange'] * 0.8  # P is less mobile
            ) / 1000.0
            
            features['soil_k_effectiveness'] = (
                farm_data['K'] * soil_props['nutrient_holding'] * 
                soil_props['cation_exchange'] * 1.2  # K is more available
            ) / 1000.0
        
        # Soil health composite score
        features['soil_health_score'] = np.mean([
            soil_props['water_retention'],
            soil_props['nutrient_holding'],
            soil_props['organic_matter'],
            soil_props['aeration']
        ])
        
        # Workability index (important for farming operations)
        if 'temperature' in farm_data:
            temp_factor = 1.0 if 15 <= farm_data['temperature'] <= 30 else 0.7
            features['soil_workability_index'] = (
                soil_props['workability'] * temp_factor
            )
        
        return features
    
    def get_crop_soil_suitability(self, crop: str, soil_type: str) -> float:
        """Get crop-soil compatibility score."""
        
        crop_lower = crop.lower()
        if crop_lower in self.crop_soil_compatibility:
            return self.crop_soil_compatibility[crop_lower].get(soil_type, 0.5)
        return 0.5  # Default neutral suitability

# Integration with existing feature engineer
def integrate_soil_features(feature_dict: Dict[str, Any], soil_type: str) -> Dict[str, Any]:
    """Integrate soil features into existing feature dictionary."""
    
    soil_engineer = SoilTypeFeatureEngineer()
    
    # Create soil-based features
    soil_features = soil_engineer.create_soil_features(soil_type, feature_dict)
    
    # Add to existing features
    enhanced_features = feature_dict.copy()
    enhanced_features.update(soil_features)
    
    # Add soil type encoding (one-hot or label encoding)
    soil_types = ['Clay Soil', 'Loamy Soil', 'Sandy Soil', 'Black Soil', 'Red Soil', 'Alluvial Soil']
    
    # Label encoding
    enhanced_features['soil_type_encoded'] = soil_types.index(soil_type) if soil_type in soil_types else 1
    
    # One-hot encoding (optional - choose one approach)
    for i, stype in enumerate(soil_types):
        enhanced_features[f'soil_is_{stype.lower().replace(" ", "_")}'] = 1 if soil_type == stype else 0
    
    return enhanced_features