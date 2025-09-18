"""
XGBoost model training pipeline for crop recommendation.
Implements comprehensive training, evaluation, and model management.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, List, Any, Tuple, Optional
import logging
from datetime import datetime
import json
from pathlib import Path
import asyncio

# ML libraries
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    precision_recall_fscore_support, roc_auc_score
)
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns

# AuraFarming imports
from app.services.data_processor import data_preprocessor
from app.services.feature_engineer import feature_engineer
from app.services.weather_service import weather_service
from app.models.schemas import CropRecommendation

logger = logging.getLogger(__name__)


class XGBoostTrainer:
    """
    Comprehensive XGBoost training pipeline for crop recommendation.
    Handles training, evaluation, hyperparameter tuning, and model deployment.
    """
    
    def __init__(self, model_manager):
        """Initialize trainer with model manager reference."""
        self.model_manager = model_manager
        self.training_history = []
        self.evaluation_metrics = {}
        
        # Hyperparameter search spaces
        self.param_grid = {
            'n_estimators': [300, 500, 800],
            'max_depth': [6, 8, 10],
            'learning_rate': [0.05, 0.1, 0.15],
            'subsample': [0.8, 0.9],
            'colsample_bytree': [0.8, 0.9]
        }
        
        logger.info("XGBoostTrainer initialized")
    
    async def train_from_csv(
        self, 
        csv_path: str,
        target_column: str = 'crop',
        test_size: float = 0.2,
        perform_tuning: bool = True,
        save_model: bool = True
    ) -> Dict[str, Any]:
        """
        Train XGBoost model from CSV dataset.
        
        Args:
            csv_path: Path to training CSV file
            target_column: Name of target column
            test_size: Fraction for test set
            perform_tuning: Whether to perform hyperparameter tuning
            save_model: Whether to save the trained model
            
        Returns:
            Training results and metrics
        """
        logger.info(f"Starting training from CSV: {csv_path}")
        
        training_start_time = datetime.now()
        
        try:
            # Step 1: Load and preprocess data
            logger.info("Step 1: Loading and preprocessing data...")
            df = data_preprocessor.load_kaggle_dataset(csv_path)
            
            # Engineer features
            df_engineered = data_preprocessor.engineer_features(df)
            
            # Add domain-specific features
            df_enhanced = feature_engineer.create_basic_features(df_engineered)
            df_final = feature_engineer.create_domain_features(df_enhanced)
            
            # Get dataset statistics
            dataset_stats = data_preprocessor.get_feature_statistics(df_final)
            logger.info(f"Dataset statistics: {dataset_stats}")
            
            # Step 2: Prepare training data
            logger.info("Step 2: Preparing training data...")
            X_train, X_test, y_train, y_test, feature_names, label_encoder = (
                data_preprocessor.prepare_for_training(
                    df_final, target_column, test_size
                )
            )
            
            # Update model manager with preprocessing components
            self.model_manager.feature_names = feature_names
            self.model_manager.label_encoders['crop'] = label_encoder
            
            # Step 3: Train the model
            logger.info("Step 3: Training XGBoost classifier...")
            
            if perform_tuning:
                best_params = await self._hyperparameter_tuning(X_train, y_train)
                config = {**self.model_manager.xgb_config['crop_classifier'], **best_params}
            else:
                config = self.model_manager.xgb_config['crop_classifier']
            
            # Handle class imbalance
            class_weights = compute_class_weight(
                'balanced', 
                classes=np.unique(y_train), 
                y=y_train
            )
            sample_weights = np.array([class_weights[y] for y in y_train])
            
            # Train the model
            self.model_manager.crop_classifier = xgb.XGBClassifier(**config)
            self.model_manager.crop_classifier.fit(
                X_train, y_train,
                sample_weight=sample_weights,
                eval_set=[(X_test, y_test)],
                verbose=False
            )
            
            # Step 4: Evaluate the model
            logger.info("Step 4: Evaluating model performance...")
            evaluation_results = self._evaluate_model(
                X_train, X_test, y_train, y_test, label_encoder
            )
            
            # Step 5: Feature importance analysis
            logger.info("Step 5: Analyzing feature importance...")
            feature_importance = self._analyze_feature_importance(feature_names)
            
            # Step 6: Update metadata
            training_end_time = datetime.now()
            training_duration = (training_end_time - training_start_time).total_seconds()
            
            self.model_manager.model_metadata.update({
                'training_date': training_start_time.isoformat(),
                'training_duration_seconds': training_duration,
                'dataset_size': len(df_final),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'feature_count': len(feature_names),
                'crop_count': len(label_encoder.classes_),
                'supported_crops': list(label_encoder.classes_),
                'training_features': feature_names,
                'accuracy_metrics': evaluation_results,
                'feature_importance': feature_importance,
                'dataset_statistics': dataset_stats,
                'hyperparameters': config
            })
            
            # Step 7: Save model if requested
            model_path = None
            if save_model:
                logger.info("Step 7: Saving trained model...")
                model_path = self.model_manager.save_model()
            
            # Prepare results
            training_results = {
                'success': True,
                'training_duration': training_duration,
                'model_path': model_path,
                'dataset_size': len(df_final),
                'feature_count': len(feature_names),
                'crop_count': len(label_encoder.classes_),
                'supported_crops': list(label_encoder.classes_),
                'accuracy_metrics': evaluation_results,
                'feature_importance': dict(list(feature_importance.items())[:10]),  # Top 10
                'dataset_statistics': dataset_stats
            }
            
            logger.info(f"Training completed successfully in {training_duration:.2f} seconds")
            logger.info(f"Model accuracy: {evaluation_results.get('accuracy', 0):.3f}")
            
            return training_results
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'training_duration': (datetime.now() - training_start_time).total_seconds()
            }
    
    async def _hyperparameter_tuning(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """Perform hyperparameter tuning using cross-validation."""
        logger.info("Performing hyperparameter tuning...")
        
        base_config = self.model_manager.xgb_config['crop_classifier'].copy()
        best_score = 0
        best_params = {}
        
        # Simplified grid search (full grid search would be computationally expensive)
        param_combinations = [
            {'n_estimators': 500, 'max_depth': 8, 'learning_rate': 0.1},
            {'n_estimators': 300, 'max_depth': 6, 'learning_rate': 0.15},
            {'n_estimators': 800, 'max_depth': 10, 'learning_rate': 0.05}
        ]
        
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        
        for params in param_combinations:
            try:
                config = {**base_config, **params}
                model = xgb.XGBClassifier(**config)
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
                mean_score = cv_scores.mean()
                
                logger.info(f"Params {params}: CV Score = {mean_score:.3f}")
                
                if mean_score > best_score:
                    best_score = mean_score
                    best_params = params
                    
            except Exception as e:
                logger.warning(f"Error testing params {params}: {e}")
        
        logger.info(f"Best hyperparameters: {best_params} (CV Score: {best_score:.3f})")
        return best_params
    
    def _evaluate_model(
        self,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        label_encoder: LabelEncoder
    ) -> Dict[str, Any]:
        """Comprehensive model evaluation."""
        logger.info("Evaluating model performance...")
        
        # Predictions
        y_train_pred = self.model_manager.crop_classifier.predict(X_train)
        y_test_pred = self.model_manager.crop_classifier.predict(X_test)
        
        # Prediction probabilities
        y_test_proba = self.model_manager.crop_classifier.predict_proba(X_test)
        
        # Basic metrics
        train_accuracy = accuracy_score(y_train, y_train_pred)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        
        # Detailed metrics
        precision, recall, f1, support = precision_recall_fscore_support(
            y_test, y_test_pred, average='weighted'
        )
        
        # Class-wise metrics
        class_report = classification_report(
            y_test, y_test_pred,
            target_names=label_encoder.classes_,
            output_dict=True
        )
        
        # Top-3 accuracy (important for recommendation systems)
        top3_accuracy = self._calculate_top_k_accuracy(y_test, y_test_proba, k=3)
        
        evaluation_results = {
            'accuracy': float(test_accuracy),
            'train_accuracy': float(train_accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'top3_accuracy': float(top3_accuracy),
            'class_wise_metrics': class_report,
            'confusion_matrix': confusion_matrix(y_test, y_test_pred).tolist(),
            'overfitting_score': float(train_accuracy - test_accuracy),
            'total_samples': len(y_test),
            'crops_evaluated': len(label_encoder.classes_)
        }
        
        logger.info(f"Test Accuracy: {test_accuracy:.3f}")
        logger.info(f"Top-3 Accuracy: {top3_accuracy:.3f}")
        logger.info(f"F1 Score: {f1:.3f}")
        
        return evaluation_results
    
    def _calculate_top_k_accuracy(self, y_true: np.ndarray, y_proba: np.ndarray, k: int = 3) -> float:
        """Calculate top-k accuracy for recommendation systems."""
        top_k_preds = np.argsort(y_proba, axis=1)[:, -k:]
        correct = 0
        
        for i, true_label in enumerate(y_true):
            if true_label in top_k_preds[i]:
                correct += 1
        
        return correct / len(y_true)
    
    def _analyze_feature_importance(self, feature_names: List[str]) -> Dict[str, float]:
        """Analyze and return feature importance."""
        if self.model_manager.crop_classifier is None:
            return {}
        
        importance_scores = self.model_manager.crop_classifier.feature_importances_
        feature_importance = dict(zip(feature_names, importance_scores))
        
        # Sort by importance
        sorted_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        logger.info("Top 10 most important features:")
        for i, (feature, importance) in enumerate(list(sorted_importance.items())[:10]):
            logger.info(f"{i+1}. {feature}: {importance:.4f}")
        
        return sorted_importance
    
    async def predict_crop_recommendations(
        self,
        farm_data: Dict[str, Any],
        top_k: int = 3,
        include_weather: bool = True
    ) -> List[CropRecommendation]:
        """
        Generate crop recommendations using trained XGBoost model.
        
        Args:
            farm_data: Farm input data
            top_k: Number of recommendations to return
            include_weather: Whether to include weather features
            
        Returns:
            List of crop recommendations
        """
        if not self.model_manager.is_ready():
            raise ValueError("Model not trained or loaded")
        
        logger.info("Generating crop recommendations...")
        
        try:
            # Step 1: Enhance with weather data if requested
            if include_weather and 'latitude' in farm_data and 'longitude' in farm_data:
                enhanced_data = await feature_engineer.integrate_weather_features(farm_data)
            else:
                enhanced_data = farm_data.copy()
            
            # Step 2: Engineer features
            feature_dict = feature_engineer.prepare_feature_matrix(enhanced_data, include_weather)
            
            # Step 3: Prepare feature vector
            feature_vector = self._prepare_prediction_features(feature_dict)
            
            # Step 4: Get predictions
            probabilities = self.model_manager.crop_classifier.predict_proba([feature_vector])[0]
            
            # Step 5: Get top-k recommendations
            top_indices = np.argsort(probabilities)[-top_k:][::-1]
            label_encoder = self.model_manager.label_encoders['crop']
            
            recommendations = []
            for i, idx in enumerate(top_indices):
                crop_name = label_encoder.classes_[idx]
                confidence = float(probabilities[idx])
                
                # Calculate additional metrics
                yield_estimate = self._estimate_yield(crop_name, enhanced_data)
                risk_level = self._assess_risk_level(crop_name, enhanced_data)
                market_demand = self._assess_market_demand(crop_name)
                
                recommendation = CropRecommendation(
                    crop_name=crop_name,
                    confidence=round(confidence, 4),  # Keep as decimal 0-1
                    expected_yield=round(yield_estimate, 2),
                    profit_potential=self._calculate_profit_potential(crop_name, yield_estimate),
                    risk_level=risk_level,
                    water_requirement=self._get_water_requirement(crop_name),
                    fertilizer_recommendation=self._get_fertilizer_recommendation(crop_name, enhanced_data),
                    market_demand=market_demand,
                    planting_month=self._get_planting_month(crop_name, enhanced_data.get('season', 'kharif')),
                    harvest_month=self._get_harvest_month(crop_name, enhanced_data.get('season', 'kharif')),
                    reasons=[
                        f"XGBoost model confidence: {confidence:.1%}",
                        f"Suitable for current conditions",
                        f"Good match for {enhanced_data.get('district', 'your region')}"
                    ]
                )
                
                recommendations.append(recommendation)
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise
    
    def _prepare_prediction_features(self, feature_dict: Dict[str, Any]) -> np.ndarray:
        """Prepare feature vector for prediction."""
        feature_vector = []
        
        for feature_name in self.model_manager.feature_names:
            if feature_name in feature_dict:
                value = feature_dict[feature_name]
                
                # Handle categorical encoding if needed
                if isinstance(value, str) and feature_name in self.model_manager.label_encoders:
                    encoder = self.model_manager.label_encoders[feature_name]
                    try:
                        value = encoder.transform([value])[0]
                    except ValueError:
                        value = 0  # Default for unknown categories
                
                feature_vector.append(float(value))
            else:
                feature_vector.append(0.0)  # Default value for missing features
        
        return np.array(feature_vector)
    
    def _estimate_yield(self, crop_name: str, farm_data: Dict[str, Any]) -> float:
        """Estimate crop yield based on conditions."""
        # Base yield estimates (tonnes/hectare) for different crops
        base_yields = {
            'Rice': 4.5,
            'Maize': 5.1,
            'Wheat': 3.2,
            'Chickpea': 1.8,
            'Potato': 22.0,
            'Sugarcane': 65.0,
            'Cotton': 2.5,
            'Soybean': 2.0
        }
        
        base_yield = base_yields.get(crop_name, 3.0)
        
        # Apply condition modifiers
        if 'soil_fertility' in farm_data:
            base_yield *= (0.7 + 0.6 * farm_data['soil_fertility'])
        
        if 'irrigation_efficiency' in farm_data:
            base_yield *= (0.8 + 0.4 * farm_data['irrigation_efficiency'])
        
        if 'overall_suitability' in farm_data:
            base_yield *= (0.6 + 0.8 * farm_data['overall_suitability'])
        
        return base_yield
    
    def _assess_risk_level(self, crop_name: str, farm_data: Dict[str, Any]) -> str:
        """Assess risk level for crop."""
        risk_score = 0.3  # Base risk
        
        if 'weather_risk' in farm_data:
            risk_score += farm_data['weather_risk'] * 0.4
        
        if 'water_stress' in farm_data and farm_data['water_stress']:
            risk_score += 0.2
        
        if risk_score < 0.3:
            return "Low"
        elif risk_score < 0.6:
            return "Medium"
        else:
            return "High"
    
    def _assess_market_demand(self, crop_name: str) -> str:
        """Assess market demand for crop."""
        high_demand_crops = ['Rice', 'Wheat', 'Maize', 'Potato', 'Onion']
        if crop_name in high_demand_crops:
            return "High"
        return "Medium"
    
    def _calculate_profit_potential(self, crop_name: str, yield_estimate: float) -> str:
        """Calculate profit potential."""
        # Simplified profit calculation based on yield and market prices
        market_prices = {  # Rs per tonne
            'Rice': 20000,
            'Wheat': 18000,
            'Maize': 16000,
            'Potato': 15000,
            'Chickpea': 50000
        }
        
        price = market_prices.get(crop_name, 20000)
        estimated_revenue = yield_estimate * price
        
        if estimated_revenue > 100000:
            return "High"
        elif estimated_revenue > 50000:
            return "Medium"
        else:
            return "Low"
    
    def _get_water_requirement(self, crop_name: str) -> str:
        """Get water requirement for crop."""
        high_water_crops = ['Rice', 'Sugarcane']
        if crop_name in high_water_crops:
            return "High"
        return "Medium"
    
    def _get_fertilizer_recommendation(self, crop_name: str, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fertilizer recommendation for crop."""
        # Simplified fertilizer recommendations
        base_recommendations = {
            'Rice': {'N': 120, 'P': 60, 'K': 40},
            'Wheat': {'N': 100, 'P': 50, 'K': 30},
            'Maize': {'N': 150, 'P': 75, 'K': 50}
        }
        
        return base_recommendations.get(crop_name, {'N': 100, 'P': 50, 'K': 40})
    
    def _get_planting_month(self, crop_name: str, season: str) -> str:
        """Get optimal planting month."""
        planting_months = {
            'kharif': {'Rice': 'June', 'Maize': 'July', 'Cotton': 'June'},
            'rabi': {'Wheat': 'November', 'Chickpea': 'December', 'Potato': 'November'},
            'summer': {'Maize': 'March', 'Fodder': 'March'}
        }
        
        return planting_months.get(season.lower(), {}).get(crop_name, 'Season-dependent')
    
    def _get_harvest_month(self, crop_name: str, season: str) -> str:
        """Get optimal harvest month."""
        harvest_months = {
            'kharif': {'Rice': 'November', 'Maize': 'October', 'Cotton': 'December'},
            'rabi': {'Wheat': 'April', 'Chickpea': 'April', 'Potato': 'February'},
            'summer': {'Maize': 'June', 'Fodder': 'June'}
        }
        
        return harvest_months.get(season.lower(), {}).get(crop_name, 'Season-dependent')


# This will be used by the XGBoost service
def create_trainer(model_manager) -> XGBoostTrainer:
    """Create trainer instance with model manager."""
    return XGBoostTrainer(model_manager)