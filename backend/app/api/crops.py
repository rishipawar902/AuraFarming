"""
Crop recommendation API routes.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.models.schemas import (
    CropRecommendationRequest, CropRecommendationResponse,
    CropRotationRequest, CropRotationResponse, APIResponse
)
from app.core.security import get_current_user
from app.services.database import DatabaseService
from app.services.ml_service import MLService
import uuid
from datetime import datetime

# Global ML service instance for reuse across requests
_global_ml_service = None

def get_ml_service():
    """Get or create the global ML service instance"""
    global _global_ml_service
    if _global_ml_service is None:
        _global_ml_service = MLService()
    return _global_ml_service

crops_router = APIRouter()

# Health check endpoint for crop service
@crops_router.get("/health")
async def crop_service_health():
    """Health check for crop service."""
    return {
        "status": "healthy",
        "service": "crop-recommendations",
        "ml_initialized": True,
        "endpoints_available": [
            "/ml/recommend",
            "/ml/yield-prediction", 
            "/ml/model-info",
            "/ml/crop-insights/{crop_name}",
            "/popular"
        ]
    }

# Pydantic models for ML endpoints
class MLCropRecommendationRequest(BaseModel):
    district: str
    season: str
    soil_type: str
    soil_ph: float
    rainfall: float
    temperature: float
    irrigation_type: str
    field_size: float
    nitrogen: Optional[float] = 300
    humidity: Optional[float] = 70

class MLCropRecommendationResponse(BaseModel):
    crop: str
    confidence: float
    expected_yield: float
    suitability_score: float
    profit_estimate: float

class YieldPredictionRequest(BaseModel):
    crop: str
    district: str
    season: str
    soil_type: str
    soil_ph: float
    rainfall: float
    temperature: float
    field_size: float
    nitrogen: Optional[float] = 300

class ModelInfoResponse(BaseModel):
    model_type: str
    accuracy: float
    supported_crops: List[str]
    last_trained: str
    total_features: int


# Simple demo login endpoint
@crops_router.post("/demo-login")
async def demo_login():
    """
    Demo login endpoint that returns a valid token without authentication.
    Use this for testing the ML features without going through full authentication.
    """
    from app.core.security import create_farmer_token
    import uuid
    
    farmer_id = str(uuid.uuid4())
    phone = "9876543210"  # Demo phone number
    
    access_token = create_farmer_token(farmer_id, phone)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "message": "Demo login successful - use this token for testing"
    }


# ML-powered endpoints (no authentication required for demo)
@crops_router.post("/ml/recommend", response_model=List[MLCropRecommendationResponse])
async def get_ml_crop_recommendations(request: MLCropRecommendationRequest):
    """
    Get ML-powered crop recommendations based on farm conditions.
    
    Args:
        request: Farm conditions for ML prediction
        
    Returns:
        List of crop recommendations with ML confidence scores
    """
    
    try:
        # Prepare farm data for ML model
        farm_data = {
            'district': request.district,
            'season': request.season,
            'soil_type': request.soil_type,
            'soil_ph': request.soil_ph,
            'rainfall': request.rainfall,
            'temperature': request.temperature,
            'field_size': request.field_size,
            'nitrogen': request.nitrogen,
            'irrigation_type': request.irrigation_type,
            'humidity': request.humidity
        }
        
        # Get ML predictions using global instance
        recommendations = get_ml_service().predict_crop(farm_data)
        
        # Convert to response format
        response = [
            MLCropRecommendationResponse(
                crop=rec['crop'],
                confidence=rec['confidence'],
                expected_yield=rec['expected_yield'],
                suitability_score=rec['suitability_score'],
                profit_estimate=rec['profit_estimate']
            )
            for rec in recommendations
        ]
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating ML recommendations: {str(e)}"
        )


@crops_router.post("/ml/yield-prediction")
async def predict_yield(request: YieldPredictionRequest):
    """
    Predict yield for a specific crop and conditions.
    
    Args:
        request: Crop and farm conditions
        
    Returns:
        Yield prediction with confidence metrics
    """
    
    try:
        farm_data = {
            'district': request.district,
            'season': request.season,
            'soil_type': request.soil_type,
            'soil_ph': request.soil_ph,
            'rainfall': request.rainfall,
            'temperature': request.temperature,
            'field_size': request.field_size,
            'nitrogen': request.nitrogen
        }
        
        yield_prediction = get_ml_service()._predict_yield(farm_data, request.crop)
        suitability_score = get_ml_service()._calculate_suitability_score(farm_data, request.crop)
        profit_estimate = get_ml_service()._calculate_profit_estimate(yield_prediction, request.crop)
        
        return {
            "crop": request.crop,
            "predicted_yield": yield_prediction,
            "suitability_score": suitability_score,
            "profit_estimate": profit_estimate,
            "confidence": suitability_score,
            "recommendations": [
                "Ensure optimal pH levels for better yield",
                "Monitor rainfall patterns during growing season",
                "Consider soil nutrient supplementation"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting yield: {str(e)}"
        )


@crops_router.get("/ml/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """
    Get information about the ML model.
    
    Returns:
        Model metadata and performance metrics
    """
    
    return ModelInfoResponse(
        model_type="Random Forest Classifier",
        accuracy=get_ml_service().model_accuracy,
        supported_crops=get_ml_service().supported_crops,
        last_trained=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_features=8
    )


@crops_router.get("/ml/crop-insights/{crop_name}")
async def get_crop_insights(crop_name: str):
    """
    Get detailed insights about a specific crop.
    
    Args:
        crop_name: Name of the crop
        
    Returns:
        Comprehensive crop information and growing guidelines
    """
    
    crop_lower = crop_name.lower()
    ml_service = get_ml_service()
    if crop_lower not in ml_service.jharkhand_crops:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop '{crop_name}' not found in database"
        )
    
    crop_info = ml_service.jharkhand_crops[crop_lower]
    
    return {
        "crop_name": crop_name.title(),
        "suitable_seasons": crop_info['seasons'],
        "soil_ph_range": {
            "min": crop_info['soil_ph_range'][0],
            "max": crop_info['soil_ph_range'][1]
        },
        "rainfall_requirement": {
            "min": crop_info['rainfall_requirement'][0],
            "max": crop_info['rainfall_requirement'][1]
        },
        "temperature_range": {
            "min": crop_info['temperature_range'][0],
            "max": crop_info['temperature_range'][1]
        },
        "suitable_soil_types": crop_info['soil_types'],
        "growing_tips": [
            f"Maintain soil pH between {crop_info['soil_ph_range'][0]} and {crop_info['soil_ph_range'][1]}",
            f"Ensure {crop_info['rainfall_requirement'][0]}-{crop_info['rainfall_requirement'][1]}mm rainfall",
            f"Optimal temperature: {crop_info['temperature_range'][0]}-{crop_info['temperature_range'][1]}°C"
        ]
    }


@crops_router.get("/popular")
async def get_popular_crops():
    """
    Get popular crops in Jharkhand based on adoption data.
    
    Returns:
        List of popular crops with statistics
    """
    # Mock data for popular crops
    popular_crops = [
        {"crop": "Rice", "adoption_rate": 75, "avg_yield": 4.5},
        {"crop": "Wheat", "adoption_rate": 45, "avg_yield": 3.2},
        {"crop": "Maize", "adoption_rate": 60, "avg_yield": 5.1},
        {"crop": "Potato", "adoption_rate": 35, "avg_yield": 22.0},
        {"crop": "Arhar", "adoption_rate": 25, "avg_yield": 1.8}
    ]
    
    return {
        "success": True,
        "message": "Popular crops retrieved successfully",
        "data": popular_crops
    }