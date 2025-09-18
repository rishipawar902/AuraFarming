"""
Advanced feature engineering pipeline for XGBoost model training.
Integrates weather data and creates domain-specific agricultural features.
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


class FeatureEngineer:
    """
    Advanced feature engineering for agricultural machine learning.
    Creates domain-specific features and integrates real-time weather data.
    """
    
    def __init__(self):
        """Initialize feature engineer."""
        
        # Optimal ranges for different crops (based on agricultural research)
        self.crop_optimal_ranges = {
            'Rice': {
                'temperature': (20, 35),
                'humidity': (70, 85),
                'rainfall': (1000, 1500),
                'soil_ph': (5.5, 7.0),
                'nitrogen': (80, 120)
            },
            'Maize': {
                'temperature': (21, 30),
                'humidity': (60, 75),
                'rainfall': (600, 1200),
                'soil_ph': (6.0, 7.5),
                'nitrogen': (100, 150)
            },
            'Wheat': {
                'temperature': (15, 25),
                'humidity': (50, 70),
                'rainfall': (300, 600),
                'soil_ph': (6.0, 7.5),
                'nitrogen': (60, 100)
            },
            'Chickpea': {
                'temperature': (20, 30),
                'humidity': (50, 70),
                'rainfall': (400, 800),
                'soil_ph': (6.5, 7.5),
                'nitrogen': (20, 40)
            },
            # Add more crops as needed
        }
        
        # Season characteristics for Jharkhand
        self.season_characteristics = {
            'kharif': {
                'months': [6, 7, 8, 9, 10, 11],
                'temp_range': (25, 35),
                'rainfall_range': (800, 1400),
                'humidity_range': (70, 85)
            },
            'rabi': {
                'months': [11, 12, 1, 2, 3, 4],
                'temp_range': (15, 25),
                'rainfall_range': (50, 200),
                'humidity_range': (50, 70)
            },
            'summer': {
                'months': [3, 4, 5, 6],
                'temp_range': (25, 40),
                'rainfall_range': (20, 100),
                'humidity_range': (40, 65)
            }
        }
        
        # Soil type characteristics
        self.soil_characteristics = {
            'Loamy Soil': {'drainage': 0.8, 'fertility': 0.9, 'water_retention': 0.7},
            'Clay Soil': {'drainage': 0.3, 'fertility': 0.7, 'water_retention': 0.9},
            'Sandy Soil': {'drainage': 0.9, 'fertility': 0.4, 'water_retention': 0.3},
            'Red Soil': {'drainage': 0.6, 'fertility': 0.6, 'water_retention': 0.5},
            'Alluvial Soil': {'drainage': 0.7, 'fertility': 0.8, 'water_retention': 0.6},
            'Black Soil': {'drainage': 0.4, 'fertility': 0.8, 'water_retention': 0.8}
        }
        
        # Irrigation efficiency scores
        self.irrigation_efficiency = {
            'Drip irrigation': 0.9,
            'Sprinkler irrigation': 0.7,
            'Tube well': 0.6,
            'Canal': 0.5,
            'Rain-fed': 0.3,
            'Dug well': 0.4
        }
        
        logger.info("FeatureEngineer initialized")
    
    def create_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create basic engineered features from the input data.
        
        Args:
            df: Input DataFrame with basic features
            
        Returns:
            DataFrame with additional basic features
        """
        logger.info("Creating basic engineered features...")
        
        df_features = df.copy()
        
        # Nutrient ratios and indices
        if all(col in df.columns for col in ['nitrogen', 'phosphorus', 'potassium']):
            # NPK ratios
            df_features['npk_ratio'] = df['nitrogen'] / (df['phosphorus'] + df['potassium'] + 1e-6)
            df_features['np_ratio'] = df['nitrogen'] / (df['phosphorus'] + 1e-6)
            df_features['nk_ratio'] = df['nitrogen'] / (df['potassium'] + 1e-6)
            df_features['pk_ratio'] = df['phosphorus'] / (df['potassium'] + 1e-6)
            
            # NPK balance
            total_npk = df['nitrogen'] + df['phosphorus'] + df['potassium']
            df_features['npk_total'] = total_npk
            df_features['nitrogen_percentage'] = df['nitrogen'] / total_npk
            df_features['phosphorus_percentage'] = df['phosphorus'] / total_npk
            df_features['potassium_percentage'] = df['potassium'] / total_npk
            
            # Ideal NPK ratios (4:2:1 for most crops)
            ideal_n = total_npk * 4/7
            ideal_p = total_npk * 2/7
            ideal_k = total_npk * 1/7
            
            df_features['npk_balance_score'] = 1 - (
                abs(df['nitrogen'] - ideal_n) + 
                abs(df['phosphorus'] - ideal_p) + 
                abs(df['potassium'] - ideal_k)
            ) / total_npk
            df_features['npk_balance_score'] = df_features['npk_balance_score'].clip(0, 1)
            
            # Nutrient adequacy scores (based on typical crop requirements)
            df_features['nitrogen_adequacy'] = np.minimum(df['nitrogen'] / 100.0, 1.0)  # Ideal ~100 kg/ha
            df_features['phosphorus_adequacy'] = np.minimum(df['phosphorus'] / 50.0, 1.0)  # Ideal ~50 kg/ha  
            df_features['potassium_adequacy'] = np.minimum(df['potassium'] / 50.0, 1.0)  # Ideal ~50 kg/ha
        
        # Climate comfort indices
        if all(col in df.columns for col in ['temperature', 'humidity']):
            # Temperature-Humidity Index (original THI formula)
            df_features['temperature_humidity_index'] = df['temperature'] * (0.8 + df['humidity'] / 100)
            
            # Also create the short version for compatibility
            df_features['thi'] = df_features['temperature_humidity_index']
            
            # Comfort zone (optimal growing conditions)
            comfort_temp = (df['temperature'] >= 20) & (df['temperature'] <= 30)
            comfort_humidity = (df['humidity'] >= 60) & (df['humidity'] <= 75)
            df_features['comfort_zone'] = (comfort_temp & comfort_humidity).astype(int)
        
        # Additional climate ratios
        if all(col in df.columns for col in ['rainfall', 'temperature']):
            df_features['rainfall_temperature_ratio'] = df['rainfall'] / (df['temperature'] + 1e-6)
        
        # Water availability index
        if all(col in df.columns for col in ['rainfall', 'humidity', 'temperature']):
            # Evapotranspiration approximation
            df_features['et_estimate'] = df['temperature'] * (100 - df['humidity']) / 100
            df_features['water_balance'] = df['rainfall'] - df_features['et_estimate']
            df_features['water_stress'] = (df_features['water_balance'] < 0).astype(int)
            
            # Water stress index (normalized)
            df_features['water_stress_index'] = np.maximum(0, -df_features['water_balance'] / 100.0)
        
        # Soil health index
        if 'soil_ph' in df.columns:
            # Optimal pH for most crops is 6.0-7.5
            optimal_ph_range = (df['soil_ph'] >= 6.0) & (df['soil_ph'] <= 7.5)
            df_features['ph_optimal'] = optimal_ph_range.astype(int)
            
            # pH deviation from optimal
            df_features['ph_deviation'] = abs(df['soil_ph'] - 6.75)  # 6.75 is ideal
            
            # pH optimality score (continuous)
            df_features['ph_optimality'] = 1 - np.minimum(df_features['ph_deviation'] / 2.0, 1.0)
        
        # Growing degree days
        if 'temperature' in df.columns:
            base_temp = 10  # Base temperature for most crops
            df_features['gdd'] = np.maximum(df['temperature'] - base_temp, 0)
            
            # Also create full name version
            df_features['growing_degree_days'] = df_features['gdd']
            
            # Heat stress indicator
            df_features['heat_stress'] = (df['temperature'] > 35).astype(int)
            df_features['cold_stress'] = (df['temperature'] < 15).astype(int)
        
        # Season encoding
        if 'season' in df.columns:
            season_mapping = {'kharif': 1, 'rabi': 2, 'summer': 3}
            df_features['season_type'] = df['season'].map(season_mapping).fillna(1)
        
        # Weather risk assessment
        df_features['weather_risk'] = 0.0  # Initialize
        if 'temperature' in df.columns:
            temp_risk = ((df['temperature'] < 15) | (df['temperature'] > 35)).astype(float) * 0.3
            df_features['weather_risk'] += temp_risk
        if 'rainfall' in df.columns:
            rainfall_risk = ((df['rainfall'] < 200) | (df['rainfall'] > 2000)).astype(float) * 0.3
            df_features['weather_risk'] += rainfall_risk
        if 'humidity' in df.columns:
            humidity_risk = ((df['humidity'] < 40) | (df['humidity'] > 90)).astype(float) * 0.4
            df_features['weather_risk'] += humidity_risk
        
        new_features = list(set(df_features.columns) - set(df.columns))
        logger.info(f"Created {len(new_features)} basic features: {new_features}")
        
        return df_features
    
    def create_domain_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create domain-specific agricultural features.
        
        Args:
            df: DataFrame with basic features
            
        Returns:
            DataFrame with domain-specific features
        """
        logger.info("Creating domain-specific features...")
        
        df_domain = df.copy()
        
        # Add soil type features if soil_type column exists
        if 'soil_type' in df.columns:
            for soil_type in self.soil_characteristics:
                soil_mask = df['soil_type'] == soil_type
                if soil_mask.any():
                    characteristics = self.soil_characteristics[soil_type]
                    df_domain.loc[soil_mask, 'soil_drainage'] = characteristics['drainage']
                    df_domain.loc[soil_mask, 'soil_fertility'] = characteristics['fertility']
                    df_domain.loc[soil_mask, 'soil_water_retention'] = characteristics['water_retention']
            
            # Fill missing values with average
            for col in ['soil_drainage', 'soil_fertility', 'soil_water_retention']:
                if col in df_domain.columns:
                    df_domain[col] = df_domain[col].fillna(df_domain[col].mean())
        
        # Add irrigation efficiency if irrigation_type exists
        if 'irrigation_type' in df.columns:
            df_domain['irrigation_efficiency'] = df['irrigation_type'].map(
                self.irrigation_efficiency
            ).fillna(0.5)  # Default efficiency
        
        # Season-based features
        if 'season' in df.columns:
            for season in self.season_characteristics:
                season_mask = df['season'].str.lower() == season
                if season_mask.any():
                    char = self.season_characteristics[season]
                    df_domain.loc[season_mask, 'season_temp_suitability'] = self._calculate_range_suitability(
                        df.loc[season_mask, 'temperature'], char['temp_range']
                    )
                    if 'rainfall' in df.columns:
                        df_domain.loc[season_mask, 'season_rainfall_suitability'] = self._calculate_range_suitability(
                            df.loc[season_mask, 'rainfall'], char['rainfall_range']
                        )
        
        # Comprehensive suitability score
        if all(col in df_domain.columns for col in ['soil_fertility', 'irrigation_efficiency']):
            df_domain['overall_suitability'] = (
                df_domain['soil_fertility'] * 0.3 +
                df_domain['irrigation_efficiency'] * 0.2 +
                df_domain.get('season_temp_suitability', 0.5) * 0.25 +
                df_domain.get('season_rainfall_suitability', 0.5) * 0.25
            )
        
        # Risk assessment features
        if all(col in df.columns for col in ['temperature', 'rainfall', 'humidity']):
            # Weather volatility (simplified)
            df_domain['weather_risk'] = (
                (df['temperature'] > 35).astype(int) * 0.4 +
                (df['rainfall'] < 200).astype(int) * 0.3 +
                (df['humidity'] < 40).astype(int) * 0.3
            )
        
        # Economic viability features
        if 'field_size' in df.columns:
            # Economies of scale
            df_domain['scale_efficiency'] = np.minimum(df['field_size'] / 2.0, 1.0)  # Optimal at 2+ hectares
            
            # Resource utilization
            if 'npk_total' in df_domain.columns:
                df_domain['nutrient_efficiency'] = df_domain['npk_total'] / df['field_size']
        
        new_features = list(set(df_domain.columns) - set(df.columns))
        logger.info(f"Created {len(new_features)} domain features: {new_features}")
        
        return df_domain
    
    def _calculate_range_suitability(self, values: pd.Series, optimal_range: Tuple[float, float]) -> pd.Series:
        """Calculate suitability score based on optimal range."""
        min_val, max_val = optimal_range
        mid_point = (min_val + max_val) / 2
        range_width = max_val - min_val
        
        # Calculate distance from optimal range
        distances = np.where(
            values < min_val, min_val - values,
            np.where(values > max_val, values - max_val, 0)
        )
        
        # Convert distance to suitability score (0-1)
        suitability = 1 - np.minimum(distances / range_width, 1)
        return pd.Series(suitability, index=values.index)
    
    async def integrate_weather_features(
        self, 
        farm_data: Dict[str, Any],
        historical_days: int = 7
    ) -> Dict[str, Any]:
        """
        Integrate real-time and historical weather features.
        
        Args:
            farm_data: Farm input data
            historical_days: Days of historical weather to consider
            
        Returns:
            Enhanced farm data with weather features
        """
        logger.info("Integrating weather features...")
        
        enhanced_data = farm_data.copy()
        
        try:
            # Get coordinates
            latitude = farm_data.get('latitude')
            longitude = farm_data.get('longitude')
            
            if latitude is not None and longitude is not None:
                # Get current weather
                current_weather = await weather_service.get_current_weather(latitude, longitude)
                
                # Get forecast
                forecast_data = await weather_service.get_weather_forecast(
                    latitude, longitude, days=7
                )
                
                if current_weather and 'ml_data' in current_weather:
                    ml_data = current_weather['ml_data']
                    
                    # Current weather features
                    enhanced_data['current_temperature'] = ml_data.get('temperature', farm_data.get('temperature', 25))
                    enhanced_data['current_rainfall'] = ml_data.get('rainfall', 0)
                    enhanced_data['current_humidity'] = ml_data.get('humidity', farm_data.get('humidity', 65))
                    
                    # Update base features with current weather
                    enhanced_data['temperature'] = enhanced_data['current_temperature']
                    enhanced_data['humidity'] = enhanced_data['current_humidity']
                
                # Forecast-based features
                if forecast_data and forecast_data.get('forecasts'):
                    forecasts = forecast_data['forecasts']
                    
                    # Weekly averages
                    weekly_temps = [f.get('ml_data', {}).get('temperature', 25) for f in forecasts]
                    weekly_rainfall = [f.get('ml_data', {}).get('rainfall', 0) for f in forecasts]
                    weekly_humidity = [f.get('ml_data', {}).get('humidity', 65) for f in forecasts]
                    
                    if weekly_temps:
                        enhanced_data['forecast_temp_avg'] = np.mean(weekly_temps)
                        enhanced_data['forecast_temp_max'] = np.max(weekly_temps)
                        enhanced_data['forecast_temp_min'] = np.min(weekly_temps)
                        enhanced_data['temp_volatility'] = np.std(weekly_temps)
                    
                    if weekly_rainfall:
                        enhanced_data['forecast_rainfall_total'] = np.sum(weekly_rainfall)
                        enhanced_data['rainfall_forecast_days'] = len([r for r in weekly_rainfall if r > 0])
                        enhanced_data['rainfall_consistency'] = 1 - (np.std(weekly_rainfall) / (np.mean(weekly_rainfall) + 1))
                    
                    if weekly_humidity:
                        enhanced_data['forecast_humidity_avg'] = np.mean(weekly_humidity)
                    
                    # Weather trend analysis
                    if len(weekly_temps) >= 3:
                        temp_trend = np.polyfit(range(len(weekly_temps)), weekly_temps, 1)[0]
                        enhanced_data['temperature_trend'] = temp_trend
                        enhanced_data['weather_stability'] = 1 / (1 + abs(temp_trend))
                
                # Enhanced rainfall features
                current_rainfall = enhanced_data.get('current_rainfall', 0)
                forecast_rainfall = enhanced_data.get('forecast_rainfall_total', 0)
                base_rainfall = farm_data.get('rainfall', 800)
                
                # Update rainfall with recent + forecast data (weighted)
                enhanced_data['rainfall'] = (
                    base_rainfall * 0.4 +  # Historical baseline
                    current_rainfall * 365 * 0.3 +  # Current daily * year
                    forecast_rainfall * 52 * 0.3  # Weekly forecast * year
                )
                
                logger.info("Weather features integrated successfully")
                
            else:
                logger.warning("No coordinates provided for weather integration")
                
        except Exception as e:
            logger.error(f"Error integrating weather features: {e}")
            # Continue with existing data if weather integration fails
        
        return enhanced_data
    
    def create_crop_specific_features(self, df: pd.DataFrame, target_crops: List[str] = None) -> pd.DataFrame:
        """
        Create crop-specific suitability features.
        
        Args:
            df: DataFrame with features
            target_crops: List of crops to create features for
            
        Returns:
            DataFrame with crop-specific features
        """
        logger.info("Creating crop-specific features...")
        
        if target_crops is None:
            target_crops = list(self.crop_optimal_ranges.keys())
        
        df_crop = df.copy()
        
        for crop in target_crops:
            if crop in self.crop_optimal_ranges:
                optimal_ranges = self.crop_optimal_ranges[crop]
                
                crop_scores = []
                for feature, (min_val, max_val) in optimal_ranges.items():
                    if feature in df.columns:
                        score = self._calculate_range_suitability(df[feature], (min_val, max_val))
                        crop_scores.append(score)
                
                if crop_scores:
                    # Average suitability across all features
                    df_crop[f'{crop.lower()}_suitability'] = np.mean(crop_scores, axis=0)
        
        new_features = [col for col in df_crop.columns if col.endswith('_suitability')]
        logger.info(f"Created {len(new_features)} crop-specific features")
        
        return df_crop
    
    def prepare_feature_matrix(
        self, 
        raw_data: Dict[str, Any], 
        include_weather: bool = True
    ) -> Dict[str, Any]:
        """
        Prepare complete feature matrix for a single prediction.
        
        Args:
            raw_data: Raw input data
            include_weather: Whether to include weather features
            
        Returns:
            Complete feature dictionary
        """
        
        # Map field names to match training data
        normalized_data = {}
        field_mapping = {
            'N': 'nitrogen',
            'P': 'phosphorus', 
            'K': 'potassium',
            'ph': 'soil_ph',
            'temperature': 'temperature',
            'humidity': 'humidity',
            'rainfall': 'rainfall',
            'location': 'location',
            'season': 'season'
        }
        
        # Apply field mapping
        for key, value in raw_data.items():
            mapped_key = field_mapping.get(key, key)
            normalized_data[mapped_key] = value
        
        # Convert to DataFrame for processing
        df = pd.DataFrame([normalized_data])
        
        # Apply feature engineering pipeline
        df_features = self.create_basic_features(df)
        df_domain = self.create_domain_features(df_features)
        
        # Add crop-specific features
        df_final = self.create_crop_specific_features(df_domain)
        
        # Convert back to dictionary
        feature_dict = df_final.iloc[0].to_dict()
        
        # Remove any NaN values and replace with appropriate defaults
        cleaned_features = {}
        for k, v in feature_dict.items():
            if pd.notna(v):
                cleaned_features[k] = v
            else:
                # Set reasonable defaults for missing values
                cleaned_features[k] = 0.0
        
        return cleaned_features
    
    def get_feature_importance_mapping(self) -> Dict[str, str]:
        """Get mapping of feature names to descriptions."""
        return {
            'nitrogen': 'Nitrogen content in soil (kg/ha)',
            'phosphorus': 'Phosphorus content in soil (kg/ha)',
            'potassium': 'Potassium content in soil (kg/ha)',
            'temperature': 'Average temperature (°C)',
            'humidity': 'Relative humidity (%)',
            'soil_ph': 'Soil pH level',
            'rainfall': 'Annual rainfall (mm)',
            'npk_total': 'Total NPK nutrients',
            'npk_balance_score': 'NPK balance quality score',
            'thi': 'Temperature-Humidity Index',
            'water_balance': 'Water availability index',
            'gdd': 'Growing Degree Days',
            'soil_fertility': 'Soil fertility score',
            'irrigation_efficiency': 'Irrigation system efficiency',
            'overall_suitability': 'Overall growing suitability',
            'weather_risk': 'Weather-related risk score'
        }


# Global instance
feature_engineer = FeatureEngineer()