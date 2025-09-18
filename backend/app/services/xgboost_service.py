"""
XGBoost-based Machine Learning Service for AuraFarming
Production-ready crop recommendation and yield prediction using real agricultural data.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, List, Any, Optional, Tuple
import joblib
import logging
from pathlib import Path
from datetime import datetime, timedelta
import asyncio
import json

# ML libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score
from sklearn.utils.class_weight import compute_class_weight

# AuraFarming imports
from app.services.weather_service import weather_service
from app.models.schemas import CropRecommendation
from app.core.config import settings

logger = logging.getLogger(__name__)


class XGBoostModelManager:
    """
    Advanced XGBoost model manager for production crop recommendations.
    Handles model training, deployment, versioning, and inference.
    """
    
    def __init__(self):
        """Initialize XGBoost model manager."""
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Model components
        self.crop_classifier = None
        self.yield_regressors = {}
        self.risk_classifier = None
        
        # Preprocessing components
        self.feature_scaler = RobustScaler()
        self.label_encoders = {}
        self.feature_names = []
        
        # Model metadata
        self.model_metadata = {
            'training_date': None,
            'dataset_size': 0,
            'model_version': '1.0.0',
            'accuracy_metrics': {},
            'feature_importance': {},
            'supported_crops': [],
            'training_features': []
        }
        
        # XGBoost configuration
        self.xgb_config = {
            'crop_classifier': {
                'objective': 'multi:softprob',
                'n_estimators': 500,
                'max_depth': 8,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'n_jobs': -1,
                'tree_method': 'auto',  # Will auto-detect GPU
                'verbosity': 1
            },
            'yield_regressor': {
                'objective': 'reg:squarederror',
                'n_estimators': 300,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.9,
                'random_state': 42,
                'n_jobs': -1,
                'tree_method': 'auto',
                'verbosity': 1
            },
            'risk_classifier': {
                'objective': 'multi:softprob',
                'n_estimators': 200,
                'max_depth': 5,
                'learning_rate': 0.15,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'n_jobs': -1,
                'tree_method': 'auto',
                'verbosity': 1
            }
        }
        
        # Initialize device configuration
        self._configure_device()
        
        # Initialize trainer (will be set when needed)
        self._trainer = None
        
        logger.info("XGBoost Model Manager initialized")
    
    def _configure_device(self):
        """Configure XGBoost device settings (CPU/GPU)."""
        try:
            # Try to detect GPU support
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus and len(gpus) > 0:
                # GPU available, configure for GPU training
                for model_config in self.xgb_config.values():
                    model_config['tree_method'] = 'gpu_hist'
                    model_config['device'] = 'cuda'
                logger.info(f"GPU detected: {gpus[0].name}. Configured for GPU training.")
            else:
                logger.info("No GPU detected. Using CPU training.")
        except ImportError:
            logger.info("GPUtil not available. Using CPU training.")
        except Exception as e:
            logger.warning(f"GPU detection failed: {e}. Using CPU training.")
    
    def get_trainer(self):
        """Get or create trainer instance."""
        if self._trainer is None:
            from app.services.xgboost_trainer import create_trainer
            self._trainer = create_trainer(self)
        return self._trainer
    
    async def train_model(self, csv_path: str, **kwargs) -> Dict[str, Any]:
        """Train the XGBoost model from CSV data."""
        trainer = self.get_trainer()
        return await trainer.train_from_csv(csv_path, **kwargs)
    
    async def get_crop_recommendations(
        self,
        farm_data: Dict[str, Any],
        top_k: int = 3,
        include_weather: bool = True
    ) -> List[CropRecommendation]:
        """Get crop recommendations using trained model."""
        if not self.is_ready():
            # Fallback to rule-based recommendations if model not ready
            return await self._get_fallback_recommendations(farm_data)
        
        trainer = self.get_trainer()
        return await trainer.predict_crop_recommendations(
            farm_data, top_k, include_weather
        )
    
    async def _get_fallback_recommendations(self, farm_data: Dict[str, Any]) -> List[CropRecommendation]:
        """Provide fallback recommendations when XGBoost model is not available."""
        logger.warning("XGBoost model not ready, using fallback recommendations")
        
        season = farm_data.get('season', 'kharif').lower()
        
        if season == 'kharif':
            crops = [
                ('Rice', 0.85, 4.5),
                ('Maize', 0.80, 5.1),
                ('Cotton', 0.75, 2.5)
            ]
        elif season == 'rabi':
            crops = [
                ('Wheat', 0.85, 3.2),
                ('Chickpea', 0.80, 1.8),
                ('Potato', 0.75, 22.0)
            ]
        else:
            crops = [
                ('Maize', 0.80, 5.1),
                ('Fodder', 0.75, 8.0),
                ('Vegetable', 0.70, 15.0)
            ]
        
        recommendations = []
        for crop, confidence, base_yield in crops:
            recommendation = CropRecommendation(
                crop_name=crop,
                confidence=round(confidence, 4),  # Keep as decimal 0-1
                expected_yield=base_yield,
                profit_potential="Medium",
                risk_level="Medium",
                water_requirement="Medium",
                fertilizer_recommendation={'N': 100, 'P': 50, 'K': 40},
                market_demand="Medium",
                planting_month="Season-dependent",
                harvest_month="Season-dependent",
                reasons=[
                    f"Rule-based recommendation for {season} season",
                    "XGBoost model not available",
                    "Based on traditional farming practices"
                ]
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information."""
        is_trained = self.crop_classifier is not None
        
        return {
            'model_type': 'XGBoost Ensemble',
            'version': self.model_metadata['model_version'],
            'is_trained': is_trained,
            'training_date': self.model_metadata['training_date'],
            'dataset_size': self.model_metadata['dataset_size'],
            'supported_crops': self.model_metadata['supported_crops'],
            'accuracy_metrics': self.model_metadata['accuracy_metrics'],
            'feature_count': len(self.feature_names),
            'features': self.feature_names,
            'device_config': self._get_device_info(),
            'models': {
                'crop_classifier': {
                    'trained': self.crop_classifier is not None,
                    'type': 'XGBClassifier',
                    'objective': 'multi:softprob'
                },
                'yield_regressors': {
                    'count': len(self.yield_regressors),
                    'crops': list(self.yield_regressors.keys()),
                    'type': 'XGBRegressor'
                },
                'risk_classifier': {
                    'trained': self.risk_classifier is not None,
                    'type': 'XGBClassifier',
                    'objective': 'multi:softprob'
                }
            }
        }
    
    def _get_device_info(self) -> Dict[str, Any]:
        """Get device configuration information."""
        device_info = {
            'cpu_available': True,
            'gpu_available': False,
            'current_device': 'cpu',
            'gpu_details': None
        }
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                device_info['gpu_available'] = True
                device_info['current_device'] = 'gpu'
                device_info['gpu_details'] = {
                    'name': gpus[0].name,
                    'memory_total': f"{gpus[0].memoryTotal}MB",
                    'memory_used': f"{gpus[0].memoryUsed}MB",
                    'driver_version': gpus[0].driver
                }
        except:
            pass
        
        return device_info
    
    def save_model(self, model_name: str = None) -> str:
        """Save trained models and metadata."""
        if model_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"xgboost_model_{timestamp}"
        
        model_path = self.models_dir / model_name
        model_path.mkdir(exist_ok=True)
        
        # Save models
        if self.crop_classifier:
            joblib.dump(self.crop_classifier, model_path / "crop_classifier.pkl")
        
        if self.yield_regressors:
            joblib.dump(self.yield_regressors, model_path / "yield_regressors.pkl")
        
        if self.risk_classifier:
            joblib.dump(self.risk_classifier, model_path / "risk_classifier.pkl")
        
        # Save preprocessing components
        joblib.dump(self.feature_scaler, model_path / "feature_scaler.pkl")
        joblib.dump(self.label_encoders, model_path / "label_encoders.pkl")
        
        # Save metadata
        with open(model_path / "metadata.json", "w") as f:
            json.dump(self.model_metadata, f, indent=2, default=str)
        
        # Save feature names
        with open(model_path / "feature_names.json", "w") as f:
            json.dump(self.feature_names, f, indent=2)
        
        logger.info(f"Model saved to {model_path}")
        return str(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """Load trained models and metadata."""
        model_path = Path(model_path)
        
        if not model_path.exists():
            logger.error(f"Model path does not exist: {model_path}")
            return False
        
        try:
            # Load models
            if (model_path / "crop_classifier.pkl").exists():
                self.crop_classifier = joblib.load(model_path / "crop_classifier.pkl")
            
            if (model_path / "yield_regressors.pkl").exists():
                self.yield_regressors = joblib.load(model_path / "yield_regressors.pkl")
            
            if (model_path / "risk_classifier.pkl").exists():
                self.risk_classifier = joblib.load(model_path / "risk_classifier.pkl")
            
            # Load preprocessing components
            self.feature_scaler = joblib.load(model_path / "feature_scaler.pkl")
            self.label_encoders = joblib.load(model_path / "label_encoders.pkl")
            
            # Load metadata
            with open(model_path / "metadata.json", "r") as f:
                self.model_metadata = json.load(f)
            
            # Load feature names
            with open(model_path / "feature_names.json", "r") as f:
                self.feature_names = json.load(f)
            
            logger.info(f"Model loaded from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def is_ready(self) -> bool:
        """Check if the model is ready for predictions."""
        return (
            self.crop_classifier is not None and
            len(self.label_encoders) > 0 and
            len(self.feature_names) > 0
        )


# Global instance
xgboost_service = XGBoostModelManager()

# Auto-load the latest model on startup
def _auto_load_latest_model():
    """Automatically load the latest trained model on service startup."""
    try:
        models_dir = Path("models")
        if not models_dir.exists():
            logger.warning("Models directory not found")
            return
            
        # Find the latest model directory
        model_dirs = [d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith('xgboost_model_')]
        
        if not model_dirs:
            logger.warning("No XGBoost models found")
            return
            
        # Sort by directory name (which includes timestamp)
        latest_model_dir = sorted(model_dirs, key=lambda x: x.name)[-1]
        
        logger.info(f"Auto-loading latest model: {latest_model_dir}")
        success = xgboost_service.load_model(str(latest_model_dir))
        
        if success:
            logger.info("✅ XGBoost model auto-loaded successfully")
        else:
            logger.error("❌ Failed to auto-load XGBoost model")
            
    except Exception as e:
        logger.error(f"Error auto-loading model: {e}")

# Auto-load on import
_auto_load_latest_model()


def get_xgboost_service() -> XGBoostModelManager:
    """Get the global XGBoost service instance."""
    return xgboost_service