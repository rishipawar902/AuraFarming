#!/usr/bin/env python3
"""
Strategy 1: Synthetic Soil Type Dataset Generation
Generate realistic soil type data based on existing crop-soil relationships
"""

import pandas as pd
import numpy as np
from typing import Dict, List

class SoilTypeDataGenerator:
    """Generate soil type data based on agricultural knowledge."""
    
    def __init__(self):
        # Soil type preferences for different crops (based on agricultural research)
        self.crop_soil_preferences = {
            'rice': {
                'Clay Soil': 0.35, 'Alluvial Soil': 0.30, 'Loamy Soil': 0.20,
                'Black Soil': 0.10, 'Sandy Soil': 0.03, 'Red Soil': 0.02
            },
            'maize': {
                'Loamy Soil': 0.40, 'Alluvial Soil': 0.25, 'Black Soil': 0.20,
                'Clay Soil': 0.10, 'Red Soil': 0.03, 'Sandy Soil': 0.02
            },
            'wheat': {
                'Loamy Soil': 0.35, 'Alluvial Soil': 0.30, 'Black Soil': 0.20,
                'Clay Soil': 0.10, 'Red Soil': 0.03, 'Sandy Soil': 0.02
            },
            'cotton': {
                'Black Soil': 0.45, 'Clay Soil': 0.25, 'Loamy Soil': 0.15,
                'Alluvial Soil': 0.10, 'Red Soil': 0.03, 'Sandy Soil': 0.02
            },
            'sugarcane': {
                'Loamy Soil': 0.35, 'Clay Soil': 0.25, 'Alluvial Soil': 0.20,
                'Black Soil': 0.15, 'Red Soil': 0.03, 'Sandy Soil': 0.02
            }
        }
        
        # Soil characteristics affecting NPK and pH
        self.soil_characteristics = {
            'Clay Soil': {
                'ph_range': (6.0, 7.5), 'n_modifier': 1.1, 'p_modifier': 1.0, 'k_modifier': 1.2,
                'water_retention': 0.9, 'drainage': 0.3
            },
            'Loamy Soil': {
                'ph_range': (6.5, 7.2), 'n_modifier': 1.0, 'p_modifier': 1.0, 'k_modifier': 1.0,
                'water_retention': 0.7, 'drainage': 0.7
            },
            'Sandy Soil': {
                'ph_range': (5.5, 6.5), 'n_modifier': 0.8, 'p_modifier': 0.9, 'k_modifier': 0.7,
                'water_retention': 0.3, 'drainage': 0.9
            },
            'Black Soil': {
                'ph_range': (7.0, 8.5), 'n_modifier': 1.2, 'p_modifier': 1.1, 'k_modifier': 1.3,
                'water_retention': 0.8, 'drainage': 0.4
            },
            'Red Soil': {
                'ph_range': (5.0, 6.5), 'n_modifier': 0.9, 'p_modifier': 0.8, 'k_modifier': 0.8,
                'water_retention': 0.5, 'drainage': 0.6
            },
            'Alluvial Soil': {
                'ph_range': (6.5, 7.8), 'n_modifier': 1.1, 'p_modifier': 1.1, 'k_modifier': 1.0,
                'water_retention': 0.6, 'drainage': 0.7
            }
        }
    
    def generate_soil_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate realistic soil types for existing crop data."""
        
        df_with_soil = df.copy()
        soil_types = []
        
        for _, row in df.iterrows():
            crop = row['label'].lower()
            
            # Get soil preferences for this crop
            if crop in self.crop_soil_preferences:
                preferences = self.crop_soil_preferences[crop]
                # Choose soil type based on preferences
                soil_type = np.random.choice(
                    list(preferences.keys()),
                    p=list(preferences.values())
                )
            else:
                # Default distribution for unknown crops
                soil_type = np.random.choice([
                    'Loamy Soil', 'Clay Soil', 'Alluvial Soil', 
                    'Black Soil', 'Sandy Soil', 'Red Soil'
                ], p=[0.3, 0.25, 0.2, 0.15, 0.06, 0.04])
            
            soil_types.append(soil_type)
        
        df_with_soil['soil_type'] = soil_types
        return df_with_soil
    
    def adjust_npk_for_soil(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adjust NPK values based on soil characteristics."""
        
        df_adjusted = df.copy()
        
        for idx, row in df.iterrows():
            soil_type = row['soil_type']
            if soil_type in self.soil_characteristics:
                chars = self.soil_characteristics[soil_type]
                
                # Apply soil-specific modifiers with some randomness
                noise_factor = np.random.normal(1.0, 0.1)
                df_adjusted.loc[idx, 'N'] *= chars['n_modifier'] * noise_factor
                df_adjusted.loc[idx, 'P'] *= chars['p_modifier'] * noise_factor
                df_adjusted.loc[idx, 'K'] *= chars['k_modifier'] * noise_factor
                
                # Adjust pH towards soil-typical range
                soil_ph_center = np.mean(chars['ph_range'])
                current_ph = row['ph']
                adjusted_ph = 0.7 * current_ph + 0.3 * soil_ph_center
                df_adjusted.loc[idx, 'ph'] = adjusted_ph
        
        return df_adjusted

# Usage example
if __name__ == "__main__":
    # Load existing dataset
    df = pd.read_csv('Crop_recommendation.csv')
    
    # Generate soil types
    generator = SoilTypeDataGenerator()
    df_with_soil = generator.generate_soil_types(df)
    df_final = generator.adjust_npk_for_soil(df_with_soil)
    
    # Save enhanced dataset
    df_final.to_csv('Crop_recommendation_with_soil.csv', index=False)
    print(f"Enhanced dataset with soil types: {len(df_final)} rows")
    print("Soil type distribution:")
    print(df_final['soil_type'].value_counts())