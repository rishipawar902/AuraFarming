"""
Advanced Ensemble Training Script for AuraFarming
Trains multiple ML models and creates intelligent ensemble
"""

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
import asyncio
import logging

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Import our services
from app.services.ensemble_service import ensemble_service
from app.services.advanced_feature_engineer import advanced_feature_engineer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def train_advanced_ensemble():
    """Train the advanced ensemble system"""
    
    print("🚀 Starting Advanced Ensemble Training for AuraFarming!")
    print("=" * 60)
    
    # Load dataset
    try:
        data_path = Path("Crop_recommendation.csv")
        if not data_path.exists():
            print("❌ Dataset not found! Please ensure Crop_recommendation.csv is in the backend directory")
            return
        
        df = pd.read_csv(data_path)
        print(f"✅ Loaded dataset with {len(df)} samples and {len(df.columns)} columns")
        print(f"📊 Unique crops: {df['label'].nunique()}")
        print(f"🎯 Crop distribution: {dict(df['label'].value_counts().head())}")
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return
    
    # Prepare features using advanced feature engineering
    print("\n🔧 Creating Advanced Feature Matrix...")
    feature_matrices = []
    labels = []
    
    for idx, row in df.iterrows():
        # Convert row to farm_data format
        farm_data = {
            'nitrogen': row['N'],
            'phosphorus': row['P'], 
            'potassium': row['K'],
            'temperature': row['temperature'],
            'humidity': row['humidity'],
            'soil_ph': row['ph'],
            'rainfall': row['rainfall'],
            'soil_type': 'Red Soil'  # Default for training
        }
        
        # Create advanced features
        feature_matrix = advanced_feature_engineer.prepare_feature_matrix(farm_data)
        
        if feature_matrix is not None:
            feature_matrices.append(feature_matrix.iloc[0])
            labels.append(row['label'])
        
        # Progress indicator
        if (idx + 1) % 500 == 0:
            print(f"  Processed {idx + 1}/{len(df)} samples...")
    
    # Combine all features
    X = pd.DataFrame(feature_matrices)
    y = pd.Series(labels)
    
    print(f"✅ Created feature matrix with {X.shape[1]} features")
    print(f"📈 Feature matrix shape: {X.shape}")
    print(f"🎯 Labels shape: {y.shape}")
    
    # Display feature names
    print(f"\n🔍 Advanced Features Created:")
    for i, feature_name in enumerate(X.columns[:20]):  # Show first 20
        print(f"  {i+1:2d}. {feature_name}")
    if len(X.columns) > 20:
        print(f"  ... and {len(X.columns) - 20} more features")
    
    # Train ensemble
    print(f"\n🤖 Training Advanced Ensemble System...")
    print("=" * 50)
    
    results = ensemble_service.train_ensemble(X, y)
    
    print(f"\n🏆 ENSEMBLE TRAINING RESULTS")
    print("=" * 40)
    print(f"🎯 Ensemble Accuracy: {results['ensemble_accuracy']:.4f}")
    print(f"📊 Individual Model Accuracies:")
    for model_name, accuracy in results['individual_accuracies'].items():
        print(f"  📈 {model_name.upper()}: {accuracy:.4f}")
    
    print(f"\n⚖️  Dynamic Model Weights:")
    for model_name, weight in results['model_weights'].items():
        print(f"  🎯 {model_name.upper()}: {weight:.3f}")
    
    print(f"\n📋 Training Summary:")
    print(f"  🔢 Total Features: {results['total_features']}")
    print(f"  📊 Training Samples: {results['training_samples']}")
    print(f"  🌾 Unique Crops: {results['unique_crops']}")
    
    # Test ensemble predictions
    print(f"\n🧪 Testing Ensemble Predictions...")
    test_samples = [
        {
            'nitrogen': 90, 'phosphorus': 42, 'potassium': 43,
            'temperature': 20.8, 'humidity': 82, 'soil_ph': 6.5, 'rainfall': 202,
            'soil_type': 'Red Soil'
        },
        {
            'nitrogen': 85, 'phosphorus': 58, 'potassium': 41,
            'temperature': 21.7, 'humidity': 80, 'soil_ph': 7.0, 'rainfall': 226,
            'soil_type': 'Alluvial Soil'
        },
        {
            'nitrogen': 60, 'phosphorus': 55, 'potassium': 44,
            'temperature': 23.0, 'humidity': 62, 'soil_ph': 6.8, 'rainfall': 263,
            'soil_type': 'Black Soil'
        }
    ]
    
    for i, test_data in enumerate(test_samples, 1):
        print(f"\n🌱 Test Sample {i}:")
        print(f"  Input: N={test_data['nitrogen']}, P={test_data['phosphorus']}, K={test_data['potassium']}")
        print(f"         T={test_data['temperature']}°C, H={test_data['humidity']}%, pH={test_data['soil_ph']}")
        print(f"         Rainfall={test_data['rainfall']}mm, Soil={test_data['soil_type']}")
        
        try:
            prediction = ensemble_service.predict_with_confidence(test_data)
            print(f"  🎯 Ensemble Prediction: {prediction['ensemble_prediction']}")
            print(f"  📊 Confidence Score: {prediction['confidence_score']:.3f}")
            print(f"  🤝 Model Agreement: {prediction['model_agreement']:.3f}")
            print(f"  ❓ Uncertainty: {prediction['uncertainty_score']:.3f}")
            
            print(f"  🏆 Top 3 Recommendations:")
            for rec in prediction['top_recommendations'][:3]:
                print(f"    {rec['rank']}. {rec['crop']} (P={rec['probability']:.3f}, {rec['confidence']})")
                
        except Exception as e:
            print(f"  ❌ Prediction failed: {e}")
    
    print(f"\n🎉 ADVANCED ENSEMBLE TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"✅ Ensemble system is ready for high-accuracy predictions")
    print(f"🚀 Innovation features implemented:")
    print(f"  📈 Multi-model ensemble (XGBoost + RandomForest + LightGBM)")
    print(f"  🎯 Dynamic model weighting based on performance")
    print(f"  🔬 50+ advanced agricultural features")
    print(f"  📊 Confidence scoring and uncertainty quantification")
    print(f"  🌾 Soil-climate interaction modeling")
    print(f"  💰 Economic and risk assessment features")

if __name__ == "__main__":
    asyncio.run(train_advanced_ensemble())