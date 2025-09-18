#!/usr/bin/env python3
"""
Test script to verify model predictions are different for different inputs.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.services.xgboost_service import get_xgboost_service
import asyncio

async def test_predictions():
    print("🧪 Testing Model Prediction Diversity")
    print("=" * 50)
    
    xgb = get_xgboost_service()
    
    if not xgb.is_ready():
        print("❌ Model not ready!")
        return
    
    # Test different farm conditions
    test_cases = [
        {
            'name': 'Ranchi Kharif (Rice conditions)',
            'data': {
                'N': 90, 'P': 42, 'K': 43,
                'temperature': 27, 'humidity': 82, 'ph': 6.5, 'rainfall': 1200,
                'location': 'Ranchi', 'season': 'kharif'
            }
        },
        {
            'name': 'Dhanbad Rabi (Wheat conditions)', 
            'data': {
                'N': 60, 'P': 30, 'K': 40,
                'temperature': 18, 'humidity': 65, 'ph': 7.2, 'rainfall': 400,
                'location': 'Dhanbad', 'season': 'rabi'
            }
        },
        {
            'name': 'Jamshedpur Summer (Hot conditions)',
            'data': {
                'N': 75, 'P': 50, 'K': 55,
                'temperature': 35, 'humidity': 45, 'ph': 6.8, 'rainfall': 150,
                'location': 'Jamshedpur', 'season': 'summer'
            }
        },
        {
            'name': 'High NPK Rich Soil',
            'data': {
                'N': 150, 'P': 80, 'K': 90,
                'temperature': 25, 'humidity': 70, 'ph': 6.0, 'rainfall': 800,
                'location': 'Ranchi', 'season': 'kharif'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)
        
        try:
            recommendations = await xgb.get_crop_recommendations(
                farm_data=test_case['data'],
                top_k=3,
                include_weather=False
            )
            
            for j, rec in enumerate(recommendations, 1):
                print(f"   {j}. {rec.crop_name} - {rec.confidence:.4f} confidence")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_predictions())