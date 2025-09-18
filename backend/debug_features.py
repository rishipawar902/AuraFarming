#!/usr/bin/env python3
"""
Debug script to check model features and predictions.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.services.xgboost_service import get_xgboost_service
from app.services.feature_engineer import feature_engineer

def main():
    print("🔍 Debugging XGBoost Model Features")
    print("=" * 50)
    
    # Get XGBoost service
    xgb = get_xgboost_service()
    
    if not xgb.is_ready():
        print("❌ Model not ready!")
        return
    
    print("✅ Model is ready!")
    print(f"Total features expected: {len(xgb.feature_names)}")
    print("\nFeature names expected by model:")
    for i, name in enumerate(xgb.feature_names):
        print(f"{i+1:2d}. {name}")
    
    print("\n" + "=" * 50)
    print("🧪 Testing Feature Engineering")
    
    # Test with sample data
    test_data = {
        'N': 90,
        'P': 42, 
        'K': 43,
        'temperature': 20.87,
        'humidity': 82.0,
        'ph': 6.5,
        'rainfall': 202.9,
        'location': 'Jharkhand',
        'season': 'kharif'
    }
    
    print(f"\nInput data: {test_data}")
    
    # Process through feature engineer
    feature_dict = feature_engineer.prepare_feature_matrix(test_data, include_weather=False)
    
    print(f"\nProcessed features ({len(feature_dict)}):")
    for name, value in feature_dict.items():
        print(f"  {name}: {value}")
    
    print(f"\nMissing features:")
    missing = set(xgb.feature_names) - set(feature_dict.keys())
    for name in missing:
        print(f"  ❌ {name}")
        
    print(f"\nExtra features (not used by model):")
    extra = set(feature_dict.keys()) - set(xgb.feature_names)
    for name in extra:
        print(f"  ⚠️ {name}")

if __name__ == "__main__":
    main()