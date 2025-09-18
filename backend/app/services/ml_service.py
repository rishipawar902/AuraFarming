"""
Advanced Machine Learning service for crop recommendations and yield predictions.
Integrates XGBoost models for real-time agricultural intelligence with fallback to traditional models.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from app.models.schemas import CropRecommendation
import random
import logging
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Import services
from app.services.weather_service import weather_service
from app.services.xgboost_service import get_xgboost_service

logger = logging.getLogger(__name__)


class MLService:
    """
    Advanced Machine Learning service for generating crop recommendations and yield predictions.
    Primary: XGBoost models for production-grade recommendations
    Fallback: Random Forest models for basic recommendations
    """
    
    def __init__(self):
        """Initialize ML service with XGBoost integration."""
        # XGBoost service (primary)
        self.xgboost_service = get_xgboost_service()
        
        # Traditional models (fallback)
        self.crop_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.yield_predictor = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # ML Model components
        self.crop_model = None
        self.encoders = {}
        self.is_ml_initialized = False
        self.model_accuracy = 0.0
        self.supported_crops = []
        
        # Jharkhand-specific crop database
        self.jharkhand_crops = {
            'rice': {
                'seasons': ['kharif'],
                'soil_ph_range': (5.5, 7.0),
                'rainfall_requirement': (1000, 2500),
                'temperature_range': (20, 35),
                'soil_types': ['clay', 'loam', 'sandy_loam']
            },
            'wheat': {
                'seasons': ['rabi'],
                'soil_ph_range': (6.0, 7.5),
                'rainfall_requirement': (400, 800),
                'temperature_range': (15, 25),
                'soil_types': ['loam', 'clay_loam']
            },
            'maize': {
                'seasons': ['kharif', 'rabi'],
                'soil_ph_range': (5.8, 7.0),
                'rainfall_requirement': (600, 1200),
                'temperature_range': (18, 32),
                'soil_types': ['loam', 'sandy_loam', 'clay_loam']
            },
            'arhar': {
                'seasons': ['kharif'],
                'soil_ph_range': (6.0, 7.5),
                'rainfall_requirement': (600, 1000),
                'temperature_range': (20, 30),
                'soil_types': ['clay_loam', 'sandy_loam']
            },
            'sugarcane': {
                'seasons': ['annual'],
                'soil_ph_range': (6.0, 8.0),
                'rainfall_requirement': (1200, 2000),
                'temperature_range': (20, 35),
                'soil_types': ['clay_loam', 'loam']
            },
            'potato': {
                'seasons': ['rabi'],
                'soil_ph_range': (5.0, 6.5),
                'rainfall_requirement': (400, 600),
                'temperature_range': (15, 25),
                'soil_types': ['sandy_loam', 'loam']
            }
        }
        
        # Initialize ML models
        self._initialize_ml_models()
    
    def _initialize_ml_models(self):
        """Initialize machine learning models for crop recommendation"""
        try:
            print("🔄 Starting ML model training...")
            # Train a simple model with synthetic data
            self._train_crop_model()
            self.is_ml_initialized = True
            print(f"✅ ML model training completed! Accuracy: {self.model_accuracy:.3f}")
            logger.info("ML models initialized successfully")
        except Exception as e:
            print(f"❌ ML model training failed: {e}")
            logger.error(f"Failed to initialize ML models: {e}")
            self.is_ml_initialized = False
    
    def _train_crop_model(self):
        """Train crop recommendation model with synthetic data"""
        # Generate synthetic training data
        data = self._generate_training_data(2000)
        
        # Initialize encoders
        self.encoders['district'] = LabelEncoder()
        self.encoders['season'] = LabelEncoder()
        self.encoders['soil_type'] = LabelEncoder()
        self.encoders['crop'] = LabelEncoder()
        
        # Encode categorical variables
        data['district_encoded'] = self.encoders['district'].fit_transform(data['district'])
        data['season_encoded'] = self.encoders['season'].fit_transform(data['season'])
        data['soil_type_encoded'] = self.encoders['soil_type'].fit_transform(data['soil_type'])
        crop_encoded = self.encoders['crop'].fit_transform(data['crop'])
        
        # Prepare features
        feature_cols = ['district_encoded', 'season_encoded', 'soil_type_encoded', 
                       'soil_ph', 'rainfall', 'temperature', 'nitrogen', 'field_size']
        X = data[feature_cols].values
        y = crop_encoded
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.crop_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.crop_model.fit(X_train, y_train)
        
        # Calculate accuracy
        y_pred = self.crop_model.predict(X_test)
        self.model_accuracy = accuracy_score(y_test, y_pred)
        
        # Store metadata
        self.supported_crops = list(self.encoders['crop'].classes_)
        
        logger.info(f"Crop model trained with {len(data)} samples, accuracy: {self.model_accuracy:.3f}")
        print(f"📊 Model training complete: {len(data)} samples, {self.model_accuracy:.3f} accuracy, {len(self.supported_crops)} crops")
    
    def _generate_training_data(self, n_samples: int) -> pd.DataFrame:
        """Generate synthetic training data for Jharkhand agriculture"""
        np.random.seed(42)
        data = []
        
        crops = ['Rice', 'Wheat', 'Maize', 'Potato', 'Arhar', 'Sugarcane', 'Onion', 'Tomato']
        districts = ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Hazaribagh', 'Giridih', 'Palamu']
        seasons = ['Kharif', 'Rabi', 'Summer']
        soil_types = ['Clay', 'Loam', 'Sandy_Loam', 'Clay_Loam', 'Sandy']
        
        for _ in range(n_samples):
            # Generate realistic conditions for Jharkhand
            district = np.random.choice(districts)
            season = np.random.choice(seasons)
            soil_type = np.random.choice(soil_types)
            soil_ph = np.random.uniform(5.0, 8.0)
            rainfall = np.random.uniform(400, 2000)  # mm annually
            temperature = np.random.uniform(15, 35)  # Celsius
            nitrogen = np.random.uniform(200, 400)  # kg/ha
            field_size = np.random.uniform(0.5, 10.0)  # hectares
            
            # Logic-based crop selection for realistic training
            if season == 'Kharif' and rainfall > 1000:
                crop = np.random.choice(['Rice', 'Maize', 'Arhar', 'Sugarcane'], p=[0.4, 0.3, 0.2, 0.1])
            elif season == 'Rabi' and rainfall < 800:
                crop = np.random.choice(['Wheat', 'Potato', 'Onion', 'Tomato'], p=[0.4, 0.3, 0.2, 0.1])
            elif season == 'Summer':
                crop = np.random.choice(['Maize', 'Tomato', 'Onion'], p=[0.5, 0.3, 0.2])
            else:
                crop = np.random.choice(crops)
            
            # Calculate yield based on conditions
            base_yield = np.random.uniform(2, 8)  # tons/hectare
            
            # Adjust yield based on optimal conditions
            crop_lower = crop.lower()
            if crop_lower in self.jharkhand_crops:
                crop_info = self.jharkhand_crops[crop_lower]
                
                # pH factor
                ph_min, ph_max = crop_info['soil_ph_range']
                if ph_min <= soil_ph <= ph_max:
                    base_yield *= 1.2
                else:
                    base_yield *= 0.8
                
                # Rainfall factor
                rain_min, rain_max = crop_info['rainfall_requirement']
                if rain_min <= rainfall <= rain_max:
                    base_yield *= 1.3
                else:
                    base_yield *= 0.7
                
                # Temperature factor
                temp_min, temp_max = crop_info['temperature_range']
                if temp_min <= temperature <= temp_max:
                    base_yield *= 1.1
                else:
                    base_yield *= 0.9
            
            data.append({
                'district': district,
                'season': season,
                'soil_type': soil_type,
                'soil_ph': soil_ph,
                'rainfall': rainfall,
                'temperature': temperature,
                'nitrogen': nitrogen,
                'field_size': field_size,
                'crop': crop,
                'yield': base_yield
            })
        
        return pd.DataFrame(data)
    
    def predict_crop(self, farm_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Predict the best crops for given farm conditions
        
        Args:
            farm_data: Dictionary containing farm conditions
            
        Returns:
            List of crop recommendations with confidence scores
        """
        if not self.is_ml_initialized or self.crop_model is None:
            logger.warning("ML model not initialized, using fallback recommendations")
            return self._get_fallback_recommendations(farm_data)
        
        try:
            # Prepare input features
            features = self._prepare_features(farm_data)
            
            # Get predictions and probabilities
            predictions = self.crop_model.predict_proba([features])[0]
            
            # Get top 3 recommendations
            top_indices = np.argsort(predictions)[-3:][::-1]
            
            recommendations = []
            for idx in top_indices:
                crop_name = self.supported_crops[idx]
                confidence = float(predictions[idx])
                
                # Calculate yield prediction
                yield_prediction = self._predict_yield(farm_data, crop_name)
                
                recommendations.append({
                    'crop': crop_name,
                    'confidence': confidence,
                    'expected_yield': yield_prediction,
                    'suitability_score': self._calculate_suitability_score(farm_data, crop_name),
                    'profit_estimate': self._calculate_profit_estimate(yield_prediction, crop_name)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in crop prediction: {e}")
            return self._get_fallback_recommendations(farm_data)
    
    def _prepare_features(self, farm_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for ML model prediction"""
        # Map input data to encoded features
        district = farm_data.get('district', 'Ranchi')
        season = farm_data.get('season', 'Kharif')
        soil_type = farm_data.get('soil_type', 'Loam')
        
        # Encode categorical variables
        try:
            district_encoded = self.encoders['district'].transform([district])[0]
        except ValueError:
            district_encoded = 0  # Default to first district
            
        try:
            season_encoded = self.encoders['season'].transform([season])[0]
        except ValueError:
            season_encoded = 0  # Default to first season
            
        try:
            soil_type_encoded = self.encoders['soil_type'].transform([soil_type])[0]
        except ValueError:
            soil_type_encoded = 0  # Default to first soil type
        
        # Use weather-enhanced data if available
        rainfall = farm_data.get('rainfall', 1000)
        temperature = farm_data.get('temperature', 25)
        
        # Prepare feature vector
        features = np.array([
            district_encoded,
            season_encoded,
            soil_type_encoded,
            farm_data.get('soil_ph', 6.5),
            rainfall,  # Enhanced with real weather data
            temperature,  # Enhanced with real weather data
            farm_data.get('nitrogen', 300),
            farm_data.get('field_size', 2.0)
        ])
        
        return features
    
    async def _enhance_farm_data_with_weather(self, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance farm data with real-time weather information.
        
        Args:
            farm_data: Original farm data containing location information
            
        Returns:
            Enhanced farm data with weather information
        """
        enhanced_data = farm_data.copy()
        
        try:
            # Get coordinates from farm data
            latitude = farm_data.get('latitude')
            longitude = farm_data.get('longitude')
            
            if latitude is not None and longitude is not None:
                # Fetch weather data for ML model
                weather_data = await weather_service.get_weather_for_ml(latitude, longitude)
                
                if weather_data and weather_data.get('current'):
                    current_weather = weather_data['current']
                    
                    # Update farm data with current weather
                    enhanced_data['temperature'] = current_weather.get('temperature', farm_data.get('temperature', 25))
                    enhanced_data['rainfall'] = current_weather.get('rainfall', farm_data.get('rainfall', 1000))
                    enhanced_data['humidity'] = current_weather.get('humidity', farm_data.get('humidity', 65))
                    
                    logger.info(f"Enhanced farm data with weather: temp={enhanced_data['temperature']}, rainfall={enhanced_data['rainfall']}")
                else:
                    logger.warning("No weather data received, using defaults")
            else:
                logger.warning("No coordinates provided, cannot fetch weather data")
                
        except Exception as e:
            logger.error(f"Error enhancing farm data with weather: {str(e)}")
            # Continue with original data if weather enhancement fails
            
        return enhanced_data
    
    def _predict_yield(self, farm_data: Dict[str, Any], crop: str) -> float:
        """Predict yield for a specific crop"""
        # Base yield estimates for Jharkhand crops (tons/hectare)
        base_yields = {
            'Rice': 4.5, 'Wheat': 3.2, 'Maize': 5.1, 'Potato': 22.0,
            'Arhar': 1.8, 'Sugarcane': 65.0, 'Onion': 18.5, 'Tomato': 25.0
        }
        
        base_yield = base_yields.get(crop, 3.0)
        
        # Apply conditions-based adjustments
        crop_lower = crop.lower()
        if crop_lower in self.jharkhand_crops:
            crop_info = self.jharkhand_crops[crop_lower]
            
            # pH adjustment
            ph = farm_data.get('soil_ph', 6.5)
            ph_min, ph_max = crop_info['soil_ph_range']
            if ph_min <= ph <= ph_max:
                base_yield *= 1.15
            else:
                base_yield *= 0.85
            
            # Rainfall adjustment
            rainfall = farm_data.get('rainfall', 1000)
            rain_min, rain_max = crop_info['rainfall_requirement']
            if rain_min <= rainfall <= rain_max:
                base_yield *= 1.20
            else:
                base_yield *= 0.80
            
            # Temperature adjustment
            temp = farm_data.get('temperature', 25)
            temp_min, temp_max = crop_info['temperature_range']
            if temp_min <= temp <= temp_max:
                base_yield *= 1.10
            else:
                base_yield *= 0.90
        
        return round(base_yield, 2)
    
    def _calculate_suitability_score(self, farm_data: Dict[str, Any], crop: str) -> float:
        """Calculate suitability score for a crop"""
        score = 0.5  # Base score
        
        crop_lower = crop.lower()
        if crop_lower in self.jharkhand_crops:
            crop_info = self.jharkhand_crops[crop_lower]
            
            # Season compatibility
            season = farm_data.get('season', 'kharif').lower()
            if season in crop_info['seasons'] or 'annual' in crop_info['seasons']:
                score += 0.2
            
            # Soil type compatibility
            soil_type = farm_data.get('soil_type', 'loam').lower()
            if soil_type in [s.lower() for s in crop_info['soil_types']]:
                score += 0.15
            
            # pH range check
            ph = farm_data.get('soil_ph', 6.5)
            ph_min, ph_max = crop_info['soil_ph_range']
            if ph_min <= ph <= ph_max:
                score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_profit_estimate(self, yield_prediction: float, crop: str) -> float:
        """Calculate profit estimate based on yield and market prices"""
        # Average market prices in Jharkhand (INR per quintal)
        market_prices = {
            'Rice': 2000, 'Wheat': 2100, 'Maize': 1800, 'Potato': 1200,
            'Arhar': 6000, 'Sugarcane': 350, 'Onion': 1500, 'Tomato': 2000
        }
        
        price_per_quintal = market_prices.get(crop, 2000)
        revenue = yield_prediction * 10 * price_per_quintal  # Convert tons to quintals
        
        # Estimate costs (INR per hectare)
        cost_estimates = {
            'Rice': 45000, 'Wheat': 35000, 'Maize': 40000, 'Potato': 120000,
            'Arhar': 30000, 'Sugarcane': 150000, 'Onion': 80000, 'Tomato': 100000
        }
        
        cost = cost_estimates.get(crop, 40000)
        profit = revenue - cost
        
        return round(profit, 0)
    
    def _get_fallback_recommendations(self, farm_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Provide fallback recommendations when ML model is not available"""
        season = farm_data.get('season', 'kharif').lower()
        
        if season == 'kharif':
            crops = ['Rice', 'Maize', 'Arhar']
        elif season == 'rabi':
            crops = ['Wheat', 'Potato', 'Onion']
        else:
            crops = ['Maize', 'Tomato', 'Onion']
        
        recommendations = []
        for i, crop in enumerate(crops):
            yield_pred = self._predict_yield(farm_data, crop)
            recommendations.append({
                'crop': crop,
                'confidence': 0.7 - (i * 0.1),
                'expected_yield': yield_pred,
                'suitability_score': self._calculate_suitability_score(farm_data, crop),
                'profit_estimate': self._calculate_profit_estimate(yield_pred, crop)
            })
        
        return recommendations
    
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
        Generate crop recommendations using XGBoost model with fallback to traditional ML.
        Enhanced with real-time weather data integration.
        
        Args:
            farm_data: Farm characteristics (should include latitude/longitude for weather)
            season: Target season
            year: Target year
            crop_history: Historical crop data
            
        Returns:
            List of top 3 crop recommendations
        """
        recommendations = []
        
        # Enhance farm data with real-time weather information
        try:
            enhanced_farm_data = await self._enhance_farm_data_with_weather(farm_data)
            enhanced_farm_data['season'] = season
            enhanced_farm_data['year'] = year
            if crop_history:
                enhanced_farm_data['crop_history'] = crop_history
            logger.info("Successfully enhanced farm data with weather information")
        except Exception as e:
            logger.warning(f"Failed to enhance with weather data: {e}, using original data")
            enhanced_farm_data = farm_data.copy()
            enhanced_farm_data['season'] = season
            enhanced_farm_data['year'] = year
        
        # Try XGBoost recommendations first (primary approach)
        try:
            if self.xgboost_service.is_ready():
                logger.info("Using XGBoost model for crop recommendations")
                xgb_recommendations = await self.xgboost_service.get_crop_recommendations(
                    enhanced_farm_data, 
                    top_k=3, 
                    include_weather=True
                )
                if xgb_recommendations:
                    return xgb_recommendations
            else:
                logger.info("XGBoost model not ready, falling back to traditional ML")
        except Exception as e:
            logger.warning(f"XGBoost recommendation failed: {e}, falling back to traditional ML")
        
        # Try traditional ML-based recommendations (secondary approach)
        if self.is_ml_initialized and self.crop_model:
            try:
                ml_recommendations = await self._get_ml_recommendations(enhanced_farm_data, season)
                if ml_recommendations:
                    return ml_recommendations[:3]
            except Exception as e:
                logger.error(f"Traditional ML recommendation failed: {e}")
        
        # Fallback to rule-based recommendations (tertiary approach)
        return await self._get_rule_based_recommendations(enhanced_farm_data, season, year, crop_history)
    
    async def _get_ml_recommendations(
        self,
        farm_data: Dict[str, Any],
        season: str
    ) -> List[CropRecommendation]:
        """Generate traditional ML-based crop recommendations (fallback)"""
        try:
            # Extract location and environmental data
            location = farm_data.get("location", {})
            district = location.get("district", "Ranchi")
            
            # Get estimated environmental conditions
            # In production, this would come from weather APIs
            estimated_conditions = self._estimate_conditions(farm_data, season)
            
            # Prepare input for ML model
            try:
                district_encoded = self.encoders['district'].transform([district])[0]
            except:
                district_encoded = 0  # Default
            
            try:
                season_encoded = self.encoders['season'].transform([season.title()])[0]
            except:
                season_encoded = 0  # Default
            
            # Create feature vector
            features = [[
                district_encoded,
                season_encoded,
                estimated_conditions['soil_ph'],
                estimated_conditions['rainfall'],
                estimated_conditions['temperature'],
                estimated_conditions['nitrogen']
            ]]
            
            # Get predictions
            probabilities = self.crop_model.predict_proba(features)[0]
            
            # Create recommendations
            recommendations = []
            for i, crop in enumerate(self.encoders['crop'].classes_):
                confidence = probabilities[i]
                if confidence > 0.05:  # Only include crops with >5% confidence
                    
                    # Calculate additional metrics
                    yield_estimate = self._estimate_yield(crop, estimated_conditions)
                    profit_estimate = self._estimate_profit(crop, yield_estimate, farm_data)
                    
                    recommendation = CropRecommendation(
                        crop=crop,
                        confidence_score=float(confidence * 100),
                        reasons=[
                            f"ML model confidence: {confidence:.1%}",
                            f"Suitable for {season} season",
                            f"Good match for {district} region"
                        ],
                        expected_yield=yield_estimate,
                        market_price=profit_estimate['market_price'],
                        profit_estimate=profit_estimate['profit'],
                        planting_month=self._get_planting_month(crop, season),
                        harvest_month=self._get_harvest_month(crop, season)
                    )
                    recommendations.append(recommendation)
            
            # Sort by confidence and return top results
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            return recommendations
            
        except Exception as e:
            logger.error(f"ML recommendation error: {e}")
            return []
    
    def _estimate_conditions(self, farm_data: Dict[str, Any], season: str) -> Dict[str, float]:
        """Estimate environmental conditions based on farm data and season"""
        # This would be replaced with real weather API data
        base_conditions = {
            'soil_ph': 6.5,
            'rainfall': 1000,
            'temperature': 25,
            'nitrogen': 300
        }
        
        # Adjust based on season
        if season.lower() == 'kharif':
            base_conditions['rainfall'] = 1200
            base_conditions['temperature'] = 28
        elif season.lower() == 'rabi':
            base_conditions['rainfall'] = 400
            base_conditions['temperature'] = 22
        elif season.lower() == 'summer':
            base_conditions['rainfall'] = 200
            base_conditions['temperature'] = 32
        
        # Add some randomness for realism
        import random
        for key in base_conditions:
            variation = base_conditions[key] * 0.1  # 10% variation
            base_conditions[key] += random.uniform(-variation, variation)
        
        return base_conditions
    
    def _estimate_yield(self, crop: str, conditions: Dict[str, float]) -> float:
        """Estimate crop yield based on conditions"""
        base_yields = {
            'Rice': 3.5, 'Wheat': 2.8, 'Maize': 4.0, 'Potato': 25,
            'Arhar': 1.2, 'Sugarcane': 65, 'Groundnut': 1.5, 'Tomato': 30
        }
        
        base_yield = base_yields.get(crop, 2.0)
        
        # Adjust based on conditions
        ph_factor = 1.0 if 6.0 <= conditions['soil_ph'] <= 7.0 else 0.9
        rainfall_factor = 1.0 if 600 <= conditions['rainfall'] <= 1500 else 0.85
        temp_factor = 1.0 if 20 <= conditions['temperature'] <= 30 else 0.9
        
        adjusted_yield = base_yield * ph_factor * rainfall_factor * temp_factor
        return round(adjusted_yield, 2)
    
    def _estimate_profit(self, crop: str, yield_estimate: float, farm_data: Dict[str, Any]) -> Dict[str, float]:
        """Estimate profit based on yield and market prices"""
        # Mock market prices (₹ per unit)
        market_prices = {
            'Rice': 2000, 'Wheat': 2200, 'Maize': 1800, 'Potato': 1500,
            'Arhar': 6000, 'Sugarcane': 350, 'Groundnut': 5500, 'Tomato': 2000
        }
        
        # Mock production costs (₹ per hectare)
        production_costs = {
            'Rice': 45000, 'Wheat': 35000, 'Maize': 30000, 'Potato': 80000,
            'Arhar': 25000, 'Sugarcane': 120000, 'Groundnut': 40000, 'Tomato': 100000
        }
        
        market_price = market_prices.get(crop, 2000)
        production_cost = production_costs.get(crop, 40000)
        
        field_size = farm_data.get('field_size', 1.0)
        revenue = yield_estimate * market_price * field_size
        total_cost = production_cost * field_size
        profit = revenue - total_cost
        
        return {
            'market_price': market_price,
            'profit': round(profit, 2)
        }
    
    async def _get_rule_based_recommendations(
        self,
        farm_data: Dict[str, Any],
        season: str,
        year: int,
        crop_history: List[Dict[str, Any]] = None
    ) -> List[CropRecommendation]:
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
    
    def _get_planting_month(self, crop: str, season: str) -> str:
        """Get optimal planting month for crop"""
        planting_schedule = {
            'Kharif': {
                'Rice': 'June',
                'Maize': 'June',
                'Arhar': 'June',
                'Sugarcane': 'February',
                'Groundnut': 'June'
            },
            'Rabi': {
                'Wheat': 'November',
                'Potato': 'October',
                'Tomato': 'November',
                'Maize': 'November'
            },
            'Summer': {
                'Tomato': 'February',
                'Maize': 'February'
            }
        }
        
        return planting_schedule.get(season, {}).get(crop, 'Variable')
    
    def _get_harvest_month(self, crop: str, season: str) -> str:
        """Get optimal harvest month for crop"""
        harvest_schedule = {
            'Kharif': {
                'Rice': 'November',
                'Maize': 'September',
                'Arhar': 'December',
                'Sugarcane': 'December',
                'Groundnut': 'October'
            },
            'Rabi': {
                'Wheat': 'April',
                'Potato': 'February',
                'Tomato': 'March',
                'Maize': 'March'
            },
            'Summer': {
                'Tomato': 'May',
                'Maize': 'May'
            }
        }
        
        return harvest_schedule.get(season, {}).get(crop, 'Variable')
    
    def get_ml_model_info(self) -> Dict[str, Any]:
        """Get ML model information and statistics"""
        return {
            'is_initialized': self.is_ml_initialized,
            'model_type': 'Random Forest Classifier',
            'accuracy': self.model_accuracy,
            'supported_crops': self.supported_crops,
            'training_samples': 1000,
            'features_used': [
                'district', 'season', 'soil_ph', 
                'rainfall', 'temperature', 'nitrogen'
            ],
            'last_updated': datetime.now().isoformat()
        }
    
    async def predict_yield(self, crop: str, farm_data: Dict[str, Any], conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Predict yield for specific crop and conditions"""
        try:
            yield_estimate = self._estimate_yield(crop, conditions)
            profit_data = self._estimate_profit(crop, yield_estimate, farm_data)
            
            return {
                'crop': crop,
                'predicted_yield': yield_estimate,
                'unit': 'tonnes/hectare',
                'market_price': profit_data['market_price'],
                'estimated_profit': profit_data['profit'],
                'confidence': 'Medium' if self.is_ml_initialized else 'Low',
                'factors_considered': list(conditions.keys()),
                'recommendations': [
                    'Monitor soil moisture levels',
                    'Apply recommended fertilizers',
                    'Follow optimal planting schedule'
                ]
            }
        except Exception as e:
            logger.error(f"Yield prediction error: {e}")
            return {'error': f'Yield prediction failed: {str(e)}'}