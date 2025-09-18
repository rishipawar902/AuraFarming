"""
Test XGBoost Model Predictions
Test the trained model with sample data to verify functionality.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.xgboost_service import get_xgboost_service

async def test_predictions():
    """Test model predictions with sample data."""
    
    print("🧪 Testing XGBoost Model Predictions")
    print("=" * 50)
    
    # Get XGBoost service
    xgb_service = get_xgboost_service()
    
    # Check if model is ready
    if not xgb_service.is_ready():
        print("❌ Model is not ready for predictions!")
        return False
    
    print("✅ Model is ready for predictions")
    print()
    
    # Test cases - different farm conditions
    test_cases = [
        {
            'name': 'Rice-friendly conditions',
            'data': {
                'N': 90, 'P': 42, 'K': 43,
                'temperature': 20.87, 'humidity': 82.0,
                'ph': 6.5, 'rainfall': 202.9,
                'location': 'Jharkhand', 'season': 'kharif'
            }
        },
        {
            'name': 'Wheat-friendly conditions',
            'data': {
                'N': 85, 'P': 60, 'K': 45,
                'temperature': 18.5, 'humidity': 65.0,
                'ph': 7.2, 'rainfall': 120.0,
                'location': 'Jharkhand', 'season': 'rabi'
            }
        },
        {
            'name': 'Maize-friendly conditions',
            'data': {
                'N': 78, 'P': 52, 'K': 48,
                'temperature': 24.0, 'humidity': 70.0,
                'ph': 6.8, 'rainfall': 180.0,
                'location': 'Jharkhand', 'season': 'kharif'
            }
        },
        {
            'name': 'High-nutrient conditions',
            'data': {
                'N': 120, 'P': 80, 'K': 65,
                'temperature': 22.0, 'humidity': 75.0,
                'ph': 6.5, 'rainfall': 150.0,
                'location': 'Jharkhand', 'season': 'rabi'
            }
        }
    ]
    
    all_success = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🌱 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Get predictions
            recommendations = await xgb_service.get_crop_recommendations(
                farm_data=test_case['data'],
                top_k=3,
                include_weather=False  # Skip weather API for testing
            )
            
            if recommendations:
                print("✅ Predictions successful!")
                print("📊 Top 3 Recommendations:")
                
                for j, rec in enumerate(recommendations, 1):
                    print(f"   {j}. {rec.crop_name}")
                    print(f"      • Confidence: {rec.confidence}%")
                    print(f"      • Expected yield: {rec.expected_yield} tons/hectare")
                    print(f"      • Risk level: {rec.risk_level}")
                    print()
                
            else:
                print("❌ No recommendations returned")
                all_success = False
                
        except Exception as e:
            print(f"❌ Prediction failed: {str(e)}")
            all_success = False
        
        print()
    
    # Model info summary
    model_info = xgb_service.get_model_info()
    print("📋 Model Summary:")
    print(f"   • Trained: {model_info['is_trained']}")
    print(f"   • Supported crops: {len(model_info['supported_crops'])}")
    print(f"   • Features: {model_info['feature_count']}")
    print(f"   • Device: {model_info['device_config']['current_device'].upper()}")
    
    if model_info.get('training_date'):
        print(f"   • Training date: {model_info['training_date']}")
    
    return all_success

if __name__ == "__main__":
    success = asyncio.run(test_predictions())
    if success:
        print("\n✅ All tests passed! Model is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the model implementation.")
        sys.exit(1)