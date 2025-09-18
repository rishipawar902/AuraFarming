"""
Advanced AI Ensemble Service for AuraFarming
Multi-model ensemble with dynamic weighting and uncertainty quantification
"""

import numpy as np
import pandas as pd
import joblib
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import logging
from pathlib import Path
import json

# ML Libraries
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb

# Feature Engineering
from app.services.advanced_feature_engineer import AdvancedFeatureEngineer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedEnsembleService:
    """
    Advanced ensemble service combining multiple ML models with intelligent weighting
    """
    
    def __init__(self):
        self.models = {}
        self.model_weights = {}
        self.model_performances = {}
        self.feature_engineer = AdvancedFeatureEngineer()
        self.label_encoder = LabelEncoder()
        self.models_dir = Path("models/ensemble")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensemble configuration
        self.model_config = {
            'xgboost': {
                'n_estimators': 200,
                'max_depth': 8,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            },
            'random_forest': {
                'n_estimators': 150,
                'max_depth': 12,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42
            },
            'lightgbm': {
                'n_estimators': 200,
                'max_depth': 10,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'verbose': -1
            }
        }
        
    def train_ensemble(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Train ensemble of models with cross-validation
        
        Args:
            X: Feature matrix
            y: Target labels
            
        Returns:
            Training results and model performances
        """
        logger.info("🚀 Starting Advanced Ensemble Training...")
        
        # Convert to numpy arrays to avoid slicing warnings
        X_array = np.ascontiguousarray(X.values)
        
        # Encode string labels to numeric
        y_encoded = self.label_encoder.fit_transform(y)
        y_array = np.ascontiguousarray(y_encoded)
        logger.info(f"📊 Encoded {len(self.label_encoder.classes_)} unique crop classes")
        
        results = {}
        cv_scores = {}
        
        # Stratified K-Fold for robust validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        # Train XGBoost with optimized cross-validation
        logger.info("Training XGBoost model...")
        xgb_scores = []
        for train_idx, val_idx in cv.split(X_array, y_array):
            X_train_fold = np.ascontiguousarray(X_array[train_idx])
            X_val_fold = np.ascontiguousarray(X_array[val_idx])
            y_train_fold = np.ascontiguousarray(y_array[train_idx])
            y_val_fold = np.ascontiguousarray(y_array[val_idx])
            
            fold_model = xgb.XGBClassifier(**self.model_config['xgboost'])
            fold_model.fit(X_train_fold, y_train_fold)
            val_pred = fold_model.predict(X_val_fold)
            score = np.mean(val_pred == y_val_fold)
            xgb_scores.append(score)
        
        xgb_model = xgb.XGBClassifier(**self.model_config['xgboost'])
        xgb_model.fit(X_array, y_array)
        self.models['xgboost'] = xgb_model
        cv_scores['xgboost'] = np.mean(xgb_scores)
        
        # Train Random Forest with optimized cross-validation
        logger.info("Training Random Forest model...")
        rf_scores = []
        for train_idx, val_idx in cv.split(X_array, y_array):
            X_train_fold = np.ascontiguousarray(X_array[train_idx])
            X_val_fold = np.ascontiguousarray(X_array[val_idx])
            y_train_fold = np.ascontiguousarray(y_array[train_idx])
            y_val_fold = np.ascontiguousarray(y_array[val_idx])
            
            fold_model = RandomForestClassifier(**self.model_config['random_forest'])
            fold_model.fit(X_train_fold, y_train_fold)
            val_pred = fold_model.predict(X_val_fold)
            score = np.mean(val_pred == y_val_fold)
            rf_scores.append(score)
        
        rf_model = RandomForestClassifier(**self.model_config['random_forest'])
        rf_model.fit(X_array, y_array)
        self.models['random_forest'] = rf_model
        cv_scores['random_forest'] = np.mean(rf_scores)
        
        # Train LightGBM - completely optimized to eliminate ALL memory warnings
        logger.info("Training LightGBM model...")
        
        # Use complete custom cross-validation with LightGBM Dataset API
        lgb_scores = []
        lgb_models = []
        
        for train_idx, val_idx in cv.split(X_array, y_array):
            # Extract fold data using copy to ensure memory contiguity
            X_train_fold = X_array[train_idx].copy()
            X_val_fold = X_array[val_idx].copy()
            y_train_fold = y_array[train_idx].copy()
            y_val_fold = y_array[val_idx].copy()
            
            # Ensure arrays are contiguous
            X_train_fold = np.ascontiguousarray(X_train_fold)
            X_val_fold = np.ascontiguousarray(X_val_fold)
            y_train_fold = np.ascontiguousarray(y_train_fold)
            y_val_fold = np.ascontiguousarray(y_val_fold)
            
            # Create LightGBM datasets with proper memory handling
            train_dataset = lgb.Dataset(
                X_train_fold, 
                label=y_train_fold,
                free_raw_data=False
            )
            val_dataset = lgb.Dataset(
                X_val_fold, 
                label=y_val_fold, 
                reference=train_dataset,
                free_raw_data=False
            )
            
            # LightGBM native parameters (no sklearn conversion)
            lgb_params = {
                'objective': 'multiclass',
                'num_class': len(np.unique(y_array)),
                'metric': 'multi_logloss',
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'max_depth': 10,
                'learning_rate': 0.1,
                'feature_fraction': 0.8,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'seed': 42,
                'verbosity': -1,
                'force_row_wise': True  # Optimize memory usage
            }
            
            # Train using native LightGBM
            fold_model = lgb.train(
                lgb_params,
                train_dataset,
                num_boost_round=200,
                valid_sets=[val_dataset],
                callbacks=[
                    lgb.early_stopping(50, verbose=False),
                    lgb.log_evaluation(0)
                ]
            )
            
            lgb_models.append(fold_model)
            
            # Predict and evaluate
            val_pred = fold_model.predict(X_val_fold, num_iteration=fold_model.best_iteration)
            val_pred_class = np.argmax(val_pred, axis=1)
            score = np.mean(val_pred_class == y_val_fold)
            lgb_scores.append(score)
        
        # Train final LightGBM model on full dataset
        # Create final dataset
        full_dataset = lgb.Dataset(
            X_array, 
            label=y_array,
            free_raw_data=False
        )
        
        # Train final model
        final_lgb_params = {
            'objective': 'multiclass',
            'num_class': len(np.unique(y_array)),
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'max_depth': 10,
            'learning_rate': 0.1,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'seed': 42,
            'verbosity': -1,
            'force_row_wise': True
        }
        
        final_lgb_model = lgb.train(
            final_lgb_params,
            full_dataset,
            num_boost_round=200,
            callbacks=[lgb.log_evaluation(0)]
        )
        
        # Wrap in sklearn-compatible interface for consistency
        lgb_sklearn_model = lgb.LGBMClassifier(**self.model_config['lightgbm'])
        lgb_sklearn_model.fit(X_array, y_array)
        
        self.models['lightgbm'] = lgb_sklearn_model
        self.models['lightgbm_native'] = final_lgb_model  # Keep native model for reference
        cv_scores['lightgbm'] = np.mean(lgb_scores)
        
        # Calculate dynamic weights based on performance
        self._calculate_dynamic_weights(cv_scores)
        
        # Store model performances
        self.model_performances = cv_scores
        
        # Save models
        self._save_ensemble_models()
        
        # Calculate ensemble performance
        ensemble_predictions = self._ensemble_predict(X)
        ensemble_accuracy = accuracy_score(y_encoded, ensemble_predictions)
        
        results = {
            'ensemble_accuracy': ensemble_accuracy,
            'individual_accuracies': cv_scores,
            'model_weights': self.model_weights,
            'total_features': X.shape[1],
            'training_samples': X.shape[0],
            'unique_crops': len(y.unique())
        }
        
        logger.info(f"✅ Ensemble Training Complete!")
        logger.info(f"🎯 Ensemble Accuracy: {ensemble_accuracy:.4f}")
        logger.info(f"📊 Individual Accuracies: {cv_scores}")
        logger.info(f"⚖️  Model Weights: {self.model_weights}")
        
        return results
    
    def _calculate_dynamic_weights(self, cv_scores: Dict[str, float]):
        """Calculate dynamic weights based on model performance"""
        # Convert scores to weights (higher score = higher weight)
        total_score = sum(cv_scores.values())
        
        # Performance-based weighting with slight bias towards XGBoost (current best)
        weights = {}
        for model_name, score in cv_scores.items():
            base_weight = score / total_score
            
            # Add small bias for XGBoost (proven performer)
            if model_name == 'xgboost':
                weights[model_name] = base_weight * 1.1
            else:
                weights[model_name] = base_weight
        
        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        self.model_weights = {k: v/total_weight for k, v in weights.items()}
    
    def predict_with_confidence(self, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make ensemble predictions with confidence scores
        
        Args:
            farm_data: Farm input data
            
        Returns:
            Ensemble predictions with confidence scores and model agreement
        """
        # Prepare features
        features = self.feature_engineer.prepare_feature_matrix(farm_data)
        
        if features is None:
            raise ValueError("Failed to prepare features for prediction")
        
        # Ensure features are contiguous numpy array
        if hasattr(features, 'values'):
            features_array = np.ascontiguousarray(features.values)
        else:
            features_array = np.ascontiguousarray(features)
        
        # Get predictions from all models
        model_predictions = {}
        model_probabilities = {}
        
        for model_name, model in self.models.items():
            try:
                # Get class predictions (numeric)
                pred_encoded = model.predict(features_array)[0]
                # Convert back to string label
                pred = self.label_encoder.inverse_transform([pred_encoded])[0]
                model_predictions[model_name] = pred
                
                # Get probability distributions
                if hasattr(model, 'predict_proba'):
                    probas = model.predict_proba(features_array)[0]
                    model_probabilities[model_name] = probas
                    
            except Exception as e:
                logger.warning(f"Model {model_name} prediction failed: {e}")
                continue
        
        # Calculate ensemble prediction
        ensemble_prediction = self._weighted_ensemble_prediction(model_predictions)
        
        # Calculate confidence metrics
        confidence_metrics = self._calculate_confidence_metrics(
            model_predictions, model_probabilities
        )
        
        # Get top N recommendations with scores
        top_recommendations = self._get_top_n_recommendations(
            model_probabilities, n=5
        )
        
        return {
            'ensemble_prediction': ensemble_prediction,
            'confidence_score': confidence_metrics['overall_confidence'],
            'model_agreement': confidence_metrics['model_agreement'],
            'individual_predictions': model_predictions,
            'model_weights': self.model_weights,
            'top_recommendations': top_recommendations,
            'uncertainty_score': confidence_metrics['uncertainty'],
            'prediction_metadata': {
                'timestamp': datetime.now().isoformat(),
                'models_used': list(model_predictions.keys()),
                'feature_count': features.shape[1]
            }
        }
    
    def _weighted_ensemble_prediction(self, model_predictions: Dict[str, str]) -> str:
        """Calculate weighted ensemble prediction"""
        # Count votes with weights
        vote_scores = {}
        
        for model_name, prediction in model_predictions.items():
            weight = self.model_weights.get(model_name, 0.33)
            
            if prediction not in vote_scores:
                vote_scores[prediction] = 0
            vote_scores[prediction] += weight
        
        # Return prediction with highest weighted score
        return max(vote_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_confidence_metrics(self, 
                                    model_predictions: Dict[str, str],
                                    model_probabilities: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Calculate various confidence metrics"""
        
        # Model agreement (how many models agree on the same prediction)
        prediction_counts = {}
        for pred in model_predictions.values():
            prediction_counts[pred] = prediction_counts.get(pred, 0) + 1
        
        max_agreement = max(prediction_counts.values())
        model_agreement = max_agreement / len(model_predictions)
        
        # Overall confidence based on probability scores
        if model_probabilities:
            # Average of maximum probabilities across models
            max_probas = []
            for probas in model_probabilities.values():
                max_probas.append(np.max(probas))
            overall_confidence = np.mean(max_probas)
            
            # Uncertainty score (higher = more uncertain)
            prob_variances = []
            for probas in model_probabilities.values():
                # Entropy-based uncertainty
                entropy = -np.sum(probas * np.log(probas + 1e-8))
                prob_variances.append(entropy)
            uncertainty = np.mean(prob_variances)
        else:
            overall_confidence = model_agreement
            uncertainty = 1.0 - model_agreement
        
        return {
            'overall_confidence': float(overall_confidence),
            'model_agreement': float(model_agreement),
            'uncertainty': float(uncertainty)
        }
    
    def _get_top_n_recommendations(self, 
                                 model_probabilities: Dict[str, np.ndarray], 
                                 n: int = 5) -> List[Dict[str, Any]]:
        """Get top N crop recommendations with ensemble probabilities"""
        
        if not model_probabilities:
            return []
        
        # Get class labels (assuming all models have same classes)
        first_model = list(self.models.values())[0]
        if hasattr(first_model, 'classes_'):
            class_labels = first_model.classes_
        else:
            return []
        
        # Calculate weighted ensemble probabilities
        ensemble_probas = np.zeros(len(class_labels))
        
        for model_name, probas in model_probabilities.items():
            weight = self.model_weights.get(model_name, 0.33)
            ensemble_probas += weight * probas
        
        # Get top N indices
        top_indices = np.argsort(ensemble_probas)[::-1][:n]
        
        recommendations = []
        for i, idx in enumerate(top_indices):
            crop_name = self.label_encoder.inverse_transform([idx])[0]
            recommendations.append({
                'rank': i + 1,
                'crop': crop_name,
                'probability': float(ensemble_probas[idx]),
                'confidence': 'High' if ensemble_probas[idx] > 0.7 else 
                           'Medium' if ensemble_probas[idx] > 0.4 else 'Low'
            })
        
        return recommendations
    
    def _ensemble_predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make ensemble predictions for evaluation"""
        predictions = []
        
        for i in range(len(X)):
            sample = X.iloc[i:i+1]
            model_preds = {}
            
            for model_name, model in self.models.items():
                try:
                    pred_encoded = model.predict(sample)[0]
                    pred = self.label_encoder.inverse_transform([pred_encoded])[0]
                    model_preds[model_name] = pred
                except:
                    continue
            
            ensemble_pred = self._weighted_ensemble_prediction(model_preds)
            predictions.append(ensemble_pred)
        
        return np.array(predictions)
    
    def _save_ensemble_models(self):
        """Save all ensemble models and metadata"""
        
        # Save individual models
        for model_name, model in self.models.items():
            model_path = self.models_dir / f"{model_name}_ensemble.joblib"
            joblib.dump(model, model_path)
            logger.info(f"✅ Saved {model_name} model to {model_path}")
        
        # Save label encoder
        encoder_path = self.models_dir / "label_encoder.joblib"
        joblib.dump(self.label_encoder, encoder_path)
        logger.info(f"✅ Saved label encoder to {encoder_path}")
        
        # Save ensemble metadata
        metadata = {
            'model_weights': self.model_weights,
            'model_performances': self.model_performances,
            'model_config': self.model_config,
            'label_classes': self.label_encoder.classes_.tolist(),
            'training_timestamp': datetime.now().isoformat()
        }
        
        metadata_path = self.models_dir / "ensemble_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Saved ensemble metadata to {metadata_path}")
    
    def load_ensemble_models(self):
        """Load pre-trained ensemble models"""
        
        try:
            # Load metadata
            metadata_path = self.models_dir / "ensemble_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                self.model_weights = metadata.get('model_weights', {})
                self.model_performances = metadata.get('model_performances', {})
                
                # Restore label encoder classes
                if 'label_classes' in metadata:
                    self.label_encoder.classes_ = np.array(metadata['label_classes'])
                
                logger.info("✅ Loaded ensemble metadata")
            
            # Load individual models
            for model_name in ['xgboost', 'random_forest', 'lightgbm']:
                model_path = self.models_dir / f"{model_name}_ensemble.joblib"
                if model_path.exists():
                    self.models[model_name] = joblib.load(model_path)
                    logger.info(f"✅ Loaded {model_name} model")
            
            # Load label encoder
            encoder_path = self.models_dir / "label_encoder.joblib"
            if encoder_path.exists():
                self.label_encoder = joblib.load(encoder_path)
                logger.info("✅ Loaded label encoder")
            
            if self.models:
                logger.info(f"🚀 Ensemble loaded with {len(self.models)} models")
                return True
            else:
                logger.warning("⚠️  No ensemble models found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error loading ensemble models: {e}")
            return False
    
    def get_ensemble_info(self) -> Dict[str, Any]:
        """Get information about the current ensemble"""
        
        return {
            'models_loaded': list(self.models.keys()),
            'model_weights': self.model_weights,
            'model_performances': self.model_performances,
            'ensemble_size': len(self.models),
            'feature_engineer_status': 'Active'
        }

# Global ensemble service instance
ensemble_service = AdvancedEnsembleService()