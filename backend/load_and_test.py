"""
Load the latest trained XGBoost model and test predictions.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.xgboost_service import get_xgboost_service

async def load_and_test():
    """Load the latest model and test predictions."""
    
    print("🔄 Loading Latest XGBoost Model")
    print("=" * 50)
    
    # Get XGBoost service
    xgb_service = get_xgboost_service()
    
    # Load the latest model
    model_path = "models/xgboost_model_20250915_222935"
    print(f"📁 Loading model from: {model_path}")
    
    success = xgb_service.load_model(model_path)
    
    if not success:
        print("❌ Failed to load model!")
        return False
    
    print("✅ Model loaded successfully!")
    print()
    
    # Check if model is ready
    if not xgb_service.is_ready():
        print("❌ Model is not ready for predictions!")
        return False
    
    print("✅ Model is ready for predictions")
    print()
    
    # Test prediction
    test_data = {
        'N': 90, 'P': 42, 'K': 43,
        'temperature': 20.87, 'humidity': 82.0,
        'ph': 6.5, 'rainfall': 202.9,
        'location': 'Jharkhand', 'season': 'kharif'
    }
    
    print("🧪 Testing with sample data:")
    for key, value in test_data.items():
        print(f"   • {key}: {value}")
    print()
    
    try:
        # Get predictions
        recommendations = await xgb_service.get_crop_recommendations(
            farm_data=test_data,
            top_k=3,
            include_weather=False
        )
        
        if recommendations:
            print("🎉 Predictions successful!")
            print("📊 Top 3 Crop Recommendations:")
            print()
            
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec.crop_name}")
                print(f"      • Confidence: {rec.confidence * 100:.2f}%")
                print(f"      • Expected yield: {rec.expected_yield} tons/hectare")
                print(f"      • Risk level: {rec.risk_level}")
                print(f"      • Profit potential: {rec.profit_potential}")
                
                if rec.reasons:
                    print(f"      • Key reasons:")
                    for reason in rec.reasons[:2]:  # Show first 2 reasons
                        print(f"        - {reason}")
                print()
            
            return True
            
        else:
            print("❌ No recommendations returned")
            return False
            
    except Exception as e:
        print(f"❌ Prediction failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(load_and_test())
    if success:
        print("✅ Model loading and testing successful!")
        print("\n🚀 Your XGBoost model is ready for production use!")
    else:
        print("\n❌ Model testing failed!")
        sys.exit(1)