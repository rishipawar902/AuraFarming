#!/usr/bin/env python3
"""
🌾 AuraFarming - Production ML Service
Integrates the advanced ensemble models into the web application
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import pickle
import joblib
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime

# Suppress warnings for clean production environment
warnings.filterwarnings('ignore', message='Usage of np.ndarray subset.*', category=UserWarning)
warnings.filterwarnings('ignore', message='X has feature names.*', category=UserWarning)

# Import compatible feature engineer
sys.path.append(str(Path(__file__).parent.parent.parent))
from compatible_features import CompatibleFeatureEngineer

# ML imports
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb

logger = logging.getLogger(__name__)

class ProductionFeatureEngineer:
    """Production-ready feature engineering for real-time predictions"""
    
    def __init__(self):
        self.feature_names = []
        self.is_fitted = False
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced agricultural features for production use"""
        features = df.copy()
        feature_names = []
        
        # Ensure required columns exist with defaults
        required_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        for col in required_cols:
            if col not in features.columns:
                # Set reasonable defaults based on Indian agriculture
                defaults = {
                    'N': 50, 'P': 40, 'K': 35, 'temperature': 25,
                    'humidity': 70, 'ph': 6.5, 'rainfall': 150
                }
                features[col] = defaults.get(col, 0)
            feature_names.append(col)
        
        # Nutrient ratios (key agricultural indicators)
        features['N_P_ratio'] = features['N'] / (features['P'] + 1e-8)
        features['N_K_ratio'] = features['N'] / (features['K'] + 1e-8)
        features['P_K_ratio'] = features['P'] / (features['K'] + 1e-8)
        feature_names.extend(['N_P_ratio', 'N_K_ratio', 'P_K_ratio'])
        
        # Total nutrients and balance
        features['total_NPK'] = features['N'] + features['P'] + features['K']
        features['NPK_balance'] = features[['N', 'P', 'K']].std(axis=1)
        feature_names.extend(['total_NPK', 'NPK_balance'])
        
        # Environmental indices
        features['heat_humidity_index'] = features['temperature'] * features['humidity'] / 100
        features['water_stress_index'] = features['rainfall'] / (features['temperature'] + 1e-8)
        features['ph_optimality'] = np.abs(features['ph'] - 6.5)
        feature_names.extend(['heat_humidity_index', 'water_stress_index', 'ph_optimality'])
        
        # Soil fertility indicators
        features['fertility_score'] = (features['N'] + features['P'] + features['K']) / 3
        features['ph_category'] = pd.cut(features['ph'], bins=[0, 6.0, 7.0, 14], labels=[0, 1, 2])
        feature_names.extend(['fertility_score', 'ph_category'])
        
        # Climate suitability scores
        features['temp_optimal'] = np.exp(-0.5 * ((features['temperature'] - 25) / 10) ** 2)
        features['humidity_optimal'] = np.exp(-0.5 * ((features['humidity'] - 70) / 20) ** 2)
        feature_names.extend(['temp_optimal', 'humidity_optimal'])
        
        # Interaction features (important for ensemble models)
        features['N_temp_interaction'] = features['N'] * features['temperature']
        features['P_ph_interaction'] = features['P'] * features['ph']
        features['K_rainfall_interaction'] = features['K'] * features['rainfall']
        feature_names.extend(['N_temp_interaction', 'P_ph_interaction', 'K_rainfall_interaction'])
        
        # Polynomial features
        features['N_squared'] = features['N'] ** 2
        features['P_squared'] = features['P'] ** 2
        features['rainfall_log'] = np.log1p(features['rainfall'])
        feature_names.extend(['N_squared', 'P_squared', 'rainfall_log'])
        
        # Growing conditions
        features['growing_degree_days'] = np.maximum(0, features['temperature'] - 10) * 30
        feature_names.append('growing_degree_days')
        
        # Efficiency ratios
        features['N_efficiency'] = features['N'] / (features['rainfall'] + 1e-8)
        features['P_efficiency'] = features['P'] / (features['ph'] + 1e-8)
        feature_names.extend(['N_efficiency', 'P_efficiency'])
        
        # Stress indicators
        features['drought_stress'] = 1 / (features['rainfall'] + 1e-8)
        features['heat_stress'] = np.maximum(0, features['temperature'] - 35)
        features['cold_stress'] = np.maximum(0, 10 - features['temperature'])
        feature_names.extend(['drought_stress', 'heat_stress', 'cold_stress'])
        
        # Advanced interactions
        features['climate_fertility'] = features['fertility_score'] * features['temp_optimal']
        features['water_nutrient'] = features['rainfall'] * features['total_NPK']
        feature_names.extend(['climate_fertility', 'water_nutrient'])
        
        self.feature_names = feature_names
        self.is_fitted = True
        
        # Return only engineered features, handle missing values
        result = features[feature_names].fillna(0)
        return result

class ProductionEnsembleService:
    """Production-ready ensemble service for real-time crop recommendations"""
    
    def __init__(self):
        self.models = {}
        self.feature_engineer = CompatibleFeatureEngineer()
        self.label_encoder = LabelEncoder()
        self.label_encoders = {}
        self.feature_scaler = None
        self.model_weights = {}
        self.is_trained = False
        self.model_info = {}
        
        # Model configurations optimized for production
        self.model_config = {
            'xgboost': {
                'n_estimators': 200,
                'max_depth': 10,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'eval_metric': 'mlogloss',
                'verbosity': 0
            },
            'random_forest': {
                'n_estimators': 200,
                'max_depth': 15,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42,
                'n_jobs': -1
            },
            'lightgbm': {
                'n_estimators': 200,
                'max_depth': 10,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'verbosity': -1
            }
        }
        
        # Try to load pre-trained models
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models if available"""
        model_dir = Path("models/ensemble_production")
        if model_dir.exists():
            try:
                # Load metadata
                metadata_path = model_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        self.model_weights = metadata.get('model_weights', {})
                        logger.info(f"📊 Loaded model weights: {self.model_weights}")
                
                # Load ensemble models
                model_files = {
                    'xgboost': 'xgboost_model.pkl',
                    'random_forest': 'random_forest_model.pkl', 
                    'lightgbm': 'lightgbm_model.pkl'
                }
                
                for model_name, filename in model_files.items():
                    model_path = model_dir / filename
                    if model_path.exists():
                        self.models[model_name] = joblib.load(model_path)
                        logger.info(f"✅ Loaded {model_name} model")
                
                # Load encoders and scalers
                target_encoder_path = model_dir / "target_encoder.pkl"
                if target_encoder_path.exists():
                    self.label_encoder = joblib.load(target_encoder_path)
                    logger.info("✅ Loaded target encoder")
                
                label_encoders_path = model_dir / "label_encoders.pkl"
                if label_encoders_path.exists():
                    self.label_encoders = joblib.load(label_encoders_path)
                    logger.info("✅ Loaded label encoders")
                
                feature_scaler_path = model_dir / "feature_scaler.pkl"
                if feature_scaler_path.exists():
                    self.feature_scaler = joblib.load(feature_scaler_path)
                    logger.info("✅ Loaded feature scaler")
                
                # Check if all required models are loaded
                required_models = ['xgboost', 'random_forest', 'lightgbm']
                models_loaded = all(model in self.models for model in required_models)
                
                if models_loaded and self.model_weights and self.label_encoder is not None:
                    self.is_trained = True
                    logger.info("✅ Pre-trained ensemble models loaded successfully")
                    logger.info(f"🎯 Ready for predictions with {len(self.models)} models")
                else:
                    logger.warning("⚠️ Not all required models/components loaded")
                    
            except Exception as e:
                logger.warning(f"Could not load pre-trained models: {e}")
                self._train_models()
        else:
            self._train_models()
    
    def _train_models(self):
        """Train models if not available"""
        try:
            logger.info("🔄 Training models for production use...")
            
            # Load training data
            data_path = self._find_data_file()
            if not data_path:
                logger.error("❌ Could not find training data")
                return
            
            df = pd.read_csv(data_path)
            
            # Prepare features
            feature_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
            X_basic = df[feature_columns]
            y = df['label']
            
            # Create advanced features
            X_advanced = self.feature_engineer.create_features(X_basic)
            
            # Train ensemble
            self._train_ensemble(X_advanced, y)
            
            # Save models
            self._save_models()
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
    
    def _find_data_file(self) -> Optional[str]:
        """Find the crop recommendation dataset"""
        possible_paths = [
            "Crop_recommendation.csv",
            "backend/Crop_recommendation.csv",
            "backend/app/data/Crop_recommendation.csv",
            "../Crop_recommendation.csv"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _train_ensemble(self, X: pd.DataFrame, y: pd.Series):
        """Train the ensemble models"""
        # Convert to numpy arrays
        X_array = np.ascontiguousarray(X.values)
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        y_array = np.ascontiguousarray(y_encoded)
        
        # Train models
        for model_name, config in self.model_config.items():
            logger.info(f"Training {model_name}...")
            
            if model_name == 'xgboost':
                model = xgb.XGBClassifier(**config)
            elif model_name == 'random_forest':
                model = RandomForestClassifier(**config)
            elif model_name == 'lightgbm':
                model = lgb.LGBMClassifier(**config)
            
            model.fit(X_array, y_array)
            self.models[model_name] = model
        
        # Calculate equal weights for simplicity in production
        self.model_weights = {name: 1.0/len(self.models) for name in self.models.keys()}
        
        self.is_trained = True
        self.model_info = {
            'trained_at': datetime.now().isoformat(),
            'feature_count': X.shape[1],
            'sample_count': len(X),
            'crop_count': len(self.label_encoder.classes_),
            'crops': list(self.label_encoder.classes_)
        }
        
        logger.info("✅ Ensemble training completed")
    
    def _save_models(self):
        """Save trained models for future use"""
        try:
            model_dir = Path("models")
            model_dir.mkdir(exist_ok=True)
            
            # Save individual models
            for model_name, model in self.models.items():
                model_path = model_dir / f"{model_name}_model.pkl"
                joblib.dump(model, model_path)
            
            # Save label encoder
            joblib.dump(self.label_encoder, model_dir / "label_encoder.pkl")
            
            # Save model weights
            joblib.dump(self.model_weights, model_dir / "model_weights.pkl")
            
            # Save model info
            joblib.dump(self.model_info, model_dir / "model_info.pkl")
            
            logger.info("✅ Models saved successfully")
            
        except Exception as e:
            logger.warning(f"Could not save models: {e}")
    
    def predict_crop(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make crop recommendation with confidence metrics
        
        Args:
            input_data: Dictionary with keys: N, P, K, temperature, humidity, ph, rainfall
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Please train the model first.")
        
        try:
            # Convert input to DataFrame
            df = pd.DataFrame([input_data])
            
            # Create features using compatible feature engineer
            X_features = self.feature_engineer.create_features(df)
            
            # Apply feature scaling if available
            if self.feature_scaler is not None:
                X_scaled = self.feature_scaler.transform(X_features)
                X_array = np.ascontiguousarray(X_scaled)
            else:
                X_array = np.ascontiguousarray(X_features.values)
            
            logger.info(f"🔍 Feature shape: {X_array.shape}, Expected features: 29")
            
            # Get predictions from all models
            predictions = {}
            probabilities = {}
            
            for model_name, model in self.models.items():
                pred_proba = model.predict_proba(X_array)
                pred_class = model.predict(X_array)
                predictions[model_name] = pred_class[0]
                probabilities[model_name] = pred_proba[0]
            
            # Ensemble prediction (weighted average)
            ensemble_proba = np.zeros_like(probabilities[list(probabilities.keys())[0]])
            for model_name, proba in probabilities.items():
                weight = self.model_weights[model_name]
                ensemble_proba += weight * proba
            
            ensemble_pred = np.argmax(ensemble_proba)
            
            # Convert back to crop name
            predicted_crop = self.label_encoder.inverse_transform([ensemble_pred])[0]
            confidence = float(np.max(ensemble_proba))
            
            # Model agreement
            pred_values = list(predictions.values())
            agreement = len(set(pred_values)) == 1
            model_agreement = float(len([p for p in pred_values if p == ensemble_pred]) / len(pred_values))
            
            # Uncertainty (entropy)
            uncertainty = float(-np.sum(ensemble_proba * np.log(ensemble_proba + 1e-8)))
            
            # Top recommendations
            top_indices = np.argsort(ensemble_proba)[::-1][:5]
            top_recommendations = []
            for idx in top_indices:
                crop_name = self.label_encoder.inverse_transform([idx])[0]
                probability = float(ensemble_proba[idx])
                conf_level = "High" if probability > 0.7 else "Medium" if probability > 0.3 else "Low"
                top_recommendations.append({
                    'crop': crop_name,
                    'probability': probability,
                    'confidence_level': conf_level
                })
            
            return {
                'predicted_crop': predicted_crop,
                'confidence': confidence,
                'model_agreement': model_agreement,
                'uncertainty': uncertainty,
                'top_recommendations': top_recommendations,
                'individual_predictions': {k: self.label_encoder.inverse_transform([v])[0] for k, v in predictions.items()},
                'model_info': self.model_info,
                'input_features': X_features.iloc[0].to_dict()
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and information"""
        return {
            'is_trained': self.is_trained,
            'models_available': list(self.models.keys()),
            'model_weights': self.model_weights,
            'feature_count': len(self.feature_engineer.feature_names) if self.feature_engineer.is_fitted else 0,
            'supported_crops': list(self.label_encoder.classes_) if self.is_trained else [],
            'model_info': self.model_info
        }
    
    def batch_predict(self, input_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Make batch predictions for multiple inputs"""
        results = []
        for input_data in input_list:
            try:
                result = self.predict_crop(input_data)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e), 'input': input_data})
        return results

# Global service instance
_production_service = None

def get_production_ml_service() -> ProductionEnsembleService:
    """Get or create the global production ML service instance"""
    global _production_service
    if _production_service is None:
        _production_service = ProductionEnsembleService()
    return _production_service

# Convenience functions for API integration
def predict_crop_recommendation(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenient function for crop prediction"""
    service = get_production_ml_service()
    return service.predict_crop(input_data)

def get_model_info() -> Dict[str, Any]:
    """Get model information"""
    service = get_production_ml_service()
    return service.get_model_status()

def batch_crop_recommendations(input_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Batch crop recommendations"""
    service = get_production_ml_service()
    return service.batch_predict(input_list)