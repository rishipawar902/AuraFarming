"""
Strategy 3: Ensemble Soil-Crop Model
Create specialized XGBoost models for each soil type and combine predictions
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, List, Any, Tuple
import joblib
from pathlib import Path

class SoilSpecificEnsemble:
    """Ensemble of soil-specific XGBoost models."""
    
    def __init__(self):
        """Initialize ensemble model."""
        
        self.soil_models = {}  # Models for each soil type
        self.general_model = None  # Fallback general model
        self.soil_weights = {
            'Clay Soil': 1.2,     # Higher weight for clay-specific predictions
            'Loamy Soil': 1.0,    # Baseline weight
            'Sandy Soil': 1.1,    # Slightly higher for sandy-specific
            'Black Soil': 1.3,    # Highest weight for black soil specificity
            'Red Soil': 1.1,      # Moderate weight
            'Alluvial Soil': 1.0  # Baseline weight
        }
        
        # Soil-specific crop preferences (training data distribution)
        self.soil_crop_distribution = {
            'Clay Soil': {
                'rice': 0.3, 'wheat': 0.2, 'cotton': 0.15, 'sugarcane': 0.1,
                'maize': 0.1, 'others': 0.15
            },
            'Black Soil': {
                'cotton': 0.4, 'sugarcane': 0.2, 'wheat': 0.15, 'maize': 0.1,
                'rice': 0.05, 'others': 0.1
            },
            'Loamy Soil': {
                'wheat': 0.25, 'maize': 0.2, 'rice': 0.15, 'cotton': 0.1,
                'vegetables': 0.15, 'others': 0.15
            },
            'Sandy Soil': {
                'millet': 0.3, 'groundnut': 0.2, 'cotton': 0.15,
                'maize': 0.1, 'others': 0.25
            },
            'Red Soil': {
                'groundnut': 0.25, 'cotton': 0.2, 'millets': 0.15,
                'maize': 0.1, 'rice': 0.1, 'others': 0.2
            },
            'Alluvial Soil': {
                'rice': 0.3, 'wheat': 0.25, 'sugarcane': 0.15,
                'maize': 0.1, 'cotton': 0.05, 'others': 0.15
            }
        }
    
    def train_soil_specific_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train separate models for each soil type."""
        
        results = {}
        
        for soil_type in self.soil_weights.keys():
            print(f"Training model for {soil_type}...")
            
            # Filter data for this soil type
            soil_data = df[df['soil_type'] == soil_type].copy()
            
            if len(soil_data) < 50:  # Minimum data requirement
                print(f"Insufficient data for {soil_type}: {len(soil_data)} samples")
                continue
            
            # Prepare features (excluding soil_type as it's constant)
            feature_cols = [col for col in df.columns 
                          if col not in ['label', 'soil_type']]
            X = soil_data[feature_cols]
            y = soil_data['label']
            
            # Train XGBoost model
            model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
            
            model.fit(X, y)
            self.soil_models[soil_type] = model
            
            # Calculate accuracy
            accuracy = model.score(X, y)
            results[soil_type] = {
                'accuracy': accuracy,
                'samples': len(soil_data),
                'crops': y.nunique()
            }
            
            print(f"{soil_type}: {accuracy:.3f} accuracy with {len(soil_data)} samples")
        
        return results
    
    def predict_ensemble(self, farm_data: Dict[str, Any], soil_type: str, top_k: int = 3) -> List[Dict]:
        """Make predictions using ensemble approach."""
        
        predictions = []
        
        # Method 1: Soil-specific model prediction
        if soil_type in self.soil_models:
            soil_model = self.soil_models[soil_type]
            
            # Prepare feature vector
            feature_vector = self._prepare_features(farm_data)
            probabilities = soil_model.predict_proba([feature_vector])[0]
            
            # Get top predictions from soil-specific model
            top_indices = np.argsort(probabilities)[-top_k:][::-1]
            
            for idx in top_indices:
                crop = soil_model.classes_[idx]
                confidence = float(probabilities[idx])
                
                # Apply soil-specific weight
                weighted_confidence = confidence * self.soil_weights.get(soil_type, 1.0)
                
                predictions.append({
                    'crop': crop,
                    'confidence': weighted_confidence,
                    'method': 'soil_specific',
                    'soil_type': soil_type
                })
        
        # Method 2: General model with soil bias
        if self.general_model:
            # Add soil preference bias to general predictions
            general_probs = self.general_model.predict_proba([feature_vector])[0]
            
            # Apply soil preference multipliers
            soil_prefs = self.soil_crop_distribution.get(soil_type, {})
            
            for i, crop in enumerate(self.general_model.classes_):
                crop_lower = crop.lower()
                soil_multiplier = soil_prefs.get(crop_lower, soil_prefs.get('others', 0.1))
                general_probs[i] *= (1.0 + soil_multiplier)
            
            # Normalize probabilities
            general_probs = general_probs / np.sum(general_probs)
            
            # Get top predictions
            top_indices = np.argsort(general_probs)[-top_k:][::-1]
            
            for idx in top_indices:
                crop = self.general_model.classes_[idx]
                confidence = float(general_probs[idx])
                
                predictions.append({
                    'crop': crop,
                    'confidence': confidence,
                    'method': 'general_with_soil_bias',
                    'soil_type': soil_type
                })
        
        # Combine and rank predictions
        final_predictions = self._combine_predictions(predictions, top_k)
        
        return final_predictions
    
    def _prepare_features(self, farm_data: Dict[str, Any]) -> np.ndarray:
        """Prepare feature vector from farm data."""
        # This should match your existing feature engineering
        # For now, using basic features
        features = [
            farm_data.get('N', 0),
            farm_data.get('P', 0),
            farm_data.get('K', 0),
            farm_data.get('temperature', 25),
            farm_data.get('humidity', 65),
            farm_data.get('ph', 6.5),
            farm_data.get('rainfall', 500)
        ]
        return np.array(features)
    
    def _combine_predictions(self, predictions: List[Dict], top_k: int) -> List[Dict]:
        """Combine predictions from different methods."""
        
        # Group by crop and combine confidences
        crop_scores = {}
        
        for pred in predictions:
            crop = pred['crop']
            confidence = pred['confidence']
            method = pred['method']
            
            if crop not in crop_scores:
                crop_scores[crop] = {
                    'total_confidence': 0,
                    'methods': [],
                    'soil_type': pred['soil_type']
                }
            
            # Weight soil-specific predictions higher
            weight = 2.0 if method == 'soil_specific' else 1.0
            crop_scores[crop]['total_confidence'] += confidence * weight
            crop_scores[crop]['methods'].append(method)
        
        # Sort by combined confidence
        sorted_crops = sorted(
            crop_scores.items(),
            key=lambda x: x[1]['total_confidence'],
            reverse=True
        )
        
        # Return top-k results
        final_results = []
        for crop, data in sorted_crops[:top_k]:
            final_results.append({
                'crop': crop,
                'confidence': min(data['total_confidence'], 1.0),  # Cap at 1.0
                'methods_used': data['methods'],
                'soil_type': data['soil_type']
            })
        
        return final_results
    
    def save_models(self, base_path: str):
        """Save all trained models."""
        base_path = Path(base_path)
        base_path.mkdir(exist_ok=True)
        
        for soil_type, model in self.soil_models.items():
            filename = f"xgb_model_{soil_type.lower().replace(' ', '_')}.pkl"
            joblib.dump(model, base_path / filename)
        
        if self.general_model:
            joblib.dump(self.general_model, base_path / "xgb_model_general.pkl")
        
        print(f"Saved {len(self.soil_models)} soil-specific models to {base_path}")
    
    def load_models(self, base_path: str):
        """Load all trained models."""
        base_path = Path(base_path)
        
        for soil_type in self.soil_weights.keys():
            filename = f"xgb_model_{soil_type.lower().replace(' ', '_')}.pkl"
            model_path = base_path / filename
            
            if model_path.exists():
                self.soil_models[soil_type] = joblib.load(model_path)
                print(f"Loaded model for {soil_type}")
        
        general_path = base_path / "xgb_model_general.pkl"
        if general_path.exists():
            self.general_model = joblib.load(general_path)
            print("Loaded general model")

# Usage example
if __name__ == "__main__":
    # Load dataset with soil types
    df = pd.read_csv('Crop_recommendation_with_soil.csv')
    
    # Initialize and train ensemble
    ensemble = SoilSpecificEnsemble()
    results = ensemble.train_soil_specific_models(df)
    
    print("\nTraining Results:")
    for soil_type, metrics in results.items():
        print(f"{soil_type}: {metrics['accuracy']:.3f} accuracy, {metrics['samples']} samples")
    
    # Save models
    ensemble.save_models('models/soil_ensemble')
    
    # Test prediction
    test_data = {
        'N': 90, 'P': 42, 'K': 43,
        'temperature': 27, 'humidity': 80, 'ph': 6.5, 'rainfall': 1200
    }
    
    predictions = ensemble.predict_ensemble(test_data, 'Clay Soil', top_k=3)
    print(f"\nPredictions for Clay Soil:")
    for pred in predictions:
        print(f"  {pred['crop']}: {pred['confidence']:.3f} confidence")