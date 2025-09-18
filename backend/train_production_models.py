"""
Production Model Training Script for AuraFarming
Trains ensemble models and saves them for production use.
"""

import pandas as pd
import numpy as np
import joblib
import json
import logging
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import xgboost as xgb
import lightgbm as lgb

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionFeatureEngineer:
    """Advanced feature engineering for production models."""
    
    def __init__(self):
        self.label_encoders = {}
        self.feature_scaler = StandardScaler()
    
    def create_features(self, df):
        """Create advanced agricultural features."""
        df = df.copy()
        
        # Encode categorical features
        categorical_cols = ['soil_type', 'crop_season']
        for col in categorical_cols:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
        
        # NPK ratios and interactions
        df['np_ratio'] = df['N'] / (df['P'] + 1)
        df['nk_ratio'] = df['N'] / (df['K'] + 1)
        df['pk_ratio'] = df['P'] / (df['K'] + 1)
        df['npk_sum'] = df['N'] + df['P'] + df['K']
        df['npk_product'] = df['N'] * df['P'] * df['K']
        
        # Climate indices
        df['heat_index'] = df['temperature'] * df['humidity'] / 100
        df['drought_stress'] = (df['temperature'] - 20) / (df['rainfall'] + 1)
        df['moisture_balance'] = df['humidity'] * df['rainfall'] / (df['temperature'] + 1)
        
        # Soil health indicators
        df['ph_optimal'] = np.abs(df['ph'] - 6.5)  # Distance from optimal pH
        df['nutrient_balance'] = np.sqrt(df['N']**2 + df['P']**2 + df['K']**2)
        
        # Additional features if available
        if 'organic_matter' in df.columns:
            df['soil_quality'] = df['organic_matter'] * (7 - df['ph_optimal'])
            df['nutrient_efficiency'] = df['npk_sum'] * df['organic_matter']
        
        if 'soil_moisture' in df.columns:
            df['water_stress'] = np.abs(df['soil_moisture'] - 60)  # Optimal around 60%
            
        if 'irrigation_frequency' in df.columns:
            df['water_management'] = df['irrigation_frequency'] * df.get('soil_moisture', 60)
            
        if 'fertilizer_usage' in df.columns:
            df['fertilizer_efficiency'] = df['npk_sum'] / (df['fertilizer_usage'] + 1)
        
        # Select numerical features for scaling
        feature_cols = [col for col in df.columns if col not in ['label', 'soil_type', 'crop_season']]
        
        return df[feature_cols]

class ProductionEnsemble:
    """Production ensemble model with XGBoost, Random Forest, and LightGBM."""
    
    def __init__(self):
        self.xgb_model = None
        self.rf_model = None
        self.lgb_model = None
        self.label_encoder = LabelEncoder()
        self.feature_scaler = StandardScaler()
        self.label_encoders = {}
        self.model_weights = {}
        self.is_trained = False
    
    def train(self, X, y):
        """Train all ensemble models."""
        logger.info("Training XGBoost model...")
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='mlogloss'
        )
        self.xgb_model.fit(X, y)
        
        logger.info("Training Random Forest model...")
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X, y)
        
        logger.info("Training LightGBM model...")
        self.lgb_model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbosity=-1
        )
        self.lgb_model.fit(X, y)
        
        self.is_trained = True
        
    def calculate_weights(self, X_val, y_val):
        """Calculate dynamic model weights based on validation performance."""
        if not self.is_trained:
            raise ValueError("Models must be trained first")
            
        # Get individual accuracies
        xgb_acc = accuracy_score(y_val, self.xgb_model.predict(X_val))
        rf_acc = accuracy_score(y_val, self.rf_model.predict(X_val))
        lgb_acc = accuracy_score(y_val, self.lgb_model.predict(X_val))
        
        # Calculate weights based on performance
        total_acc = xgb_acc + rf_acc + lgb_acc
        self.model_weights = {
            'xgboost': xgb_acc / total_acc,
            'random_forest': rf_acc / total_acc,
            'lightgbm': lgb_acc / total_acc
        }
        
        return {
            'xgboost': xgb_acc,
            'random_forest': rf_acc,
            'lightgbm': lgb_acc
        }

def main():
    """Main training function."""
    try:
        logger.info("🌾 Starting Production Model Training...")
        
        # Load dataset
        data_path = "../Crop_recommendation.csv"
        if not Path(data_path).exists():
            data_path = "Crop_recommendation.csv"
        if not Path(data_path).exists():
            raise FileNotFoundError("Could not find Crop_recommendation.csv")
            
        df = pd.read_csv(data_path)
        logger.info(f"📊 Loaded dataset with {len(df)} samples")
        
        # Add synthetic extended features for production demo
        np.random.seed(42)
        n_samples = len(df)
        df['soil_type'] = np.random.choice(['loamy', 'sandy', 'clay', 'silt'], n_samples)
        df['crop_season'] = np.random.choice(['Kharif', 'Rabi', 'Zaid'], n_samples)
        df['organic_matter'] = np.random.uniform(1.0, 5.0, n_samples)
        df['soil_moisture'] = np.random.uniform(30, 90, n_samples)
        df['irrigation_frequency'] = np.random.randint(1, 8, n_samples)
        df['fertilizer_usage'] = np.random.uniform(50, 300, n_samples)
        df['pesticide_usage'] = np.random.uniform(0, 20, n_samples)
        
        # Initialize feature engineer
        feature_engineer = ProductionFeatureEngineer()
        
        # Create features
        logger.info("🔬 Creating advanced features...")
        X = feature_engineer.create_features(df)
        y = df['label']
        
        # Encode target
        ensemble = ProductionEnsemble()
        y_encoded = ensemble.label_encoder.fit_transform(y)
        
        # Scale features
        X_scaled = ensemble.feature_scaler.fit_transform(X)
        ensemble.label_encoders = feature_engineer.label_encoders
        
        logger.info(f"✅ Created {X_scaled.shape[1]} features")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train ensemble
        logger.info("🚀 Starting Ensemble Training...")
        ensemble.train(X_train, y_train)
        
        # Calculate weights
        individual_accuracies = ensemble.calculate_weights(X_val, y_val)
        
        # Test ensemble
        logger.info("📊 Testing ensemble performance...")
        xgb_pred = ensemble.xgb_model.predict(X_val)
        rf_pred = ensemble.rf_model.predict(X_val)
        lgb_pred = ensemble.lgb_model.predict(X_val)
        
        # Weighted ensemble prediction
        xgb_proba = ensemble.xgb_model.predict_proba(X_val)
        rf_proba = ensemble.rf_model.predict_proba(X_val)
        lgb_proba = ensemble.lgb_model.predict_proba(X_val)
        
        ensemble_proba = (
            ensemble.model_weights['xgboost'] * xgb_proba +
            ensemble.model_weights['random_forest'] * rf_proba +
            ensemble.model_weights['lightgbm'] * lgb_proba
        )
        ensemble_pred = np.argmax(ensemble_proba, axis=1)
        
        accuracy = accuracy_score(y_val, ensemble_pred)
        
        logger.info("✅ Ensemble Training Complete!")
        logger.info(f"🎯 Ensemble Accuracy: {accuracy:.4f}")
        logger.info(f"📊 Individual Accuracies: {individual_accuracies}")
        logger.info(f"⚖️  Model Weights: {ensemble.model_weights}")
        
        # Save models for production
        logger.info("💾 Saving models for production...")
        production_dir = Path("models/ensemble_production")
        production_dir.mkdir(parents=True, exist_ok=True)
        
        # Save individual models
        joblib.dump(ensemble.xgb_model, production_dir / "xgboost_model.pkl")
        joblib.dump(ensemble.rf_model, production_dir / "random_forest_model.pkl")
        joblib.dump(ensemble.lgb_model, production_dir / "lightgbm_model.pkl")
        
        # Save encoders and scalers
        joblib.dump(ensemble.label_encoders, production_dir / "label_encoders.pkl")
        joblib.dump(ensemble.feature_scaler, production_dir / "feature_scaler.pkl")
        joblib.dump(ensemble.label_encoder, production_dir / "target_encoder.pkl")
        
        # Save model weights and metadata
        feature_names = X.columns.tolist()
        metadata = {
            'model_weights': ensemble.model_weights,
            'feature_names': feature_names,
            'n_features': len(feature_names),
            'n_classes': len(ensemble.label_encoder.classes_),
            'classes': ensemble.label_encoder.classes_.tolist(),
            'training_accuracy': float(accuracy),
            'individual_accuracies': {k: float(v) for k, v in individual_accuracies.items()},
            'timestamp': datetime.now().isoformat()
        }
        
        with open(production_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Models saved to: {production_dir}")
        logger.info("🚀 Production service can now load these models!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Production model training")