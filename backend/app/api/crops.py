"""
Crop recommendation API routes.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import (
    CropRecommendationRequest, CropRecommendationResponse,
    CropRotationRequest, CropRotationResponse, APIResponse
)
from app.core.security import get_current_user
from app.services.database import DatabaseService
from app.services.ml_service import MLService
from app.services.crop_rotation import CropRotationService
import uuid
from datetime import datetime

crops_router = APIRouter()


@crops_router.post("/recommend", response_model=APIResponse)
async def get_crop_recommendations(
    request: CropRecommendationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-powered crop recommendations.
    
    Args:
        request: Crop recommendation request
        current_user: Current authenticated user
        
    Returns:
        Top-3 crop recommendations with confidence scores
    """
    db = DatabaseService()
    ml_service = MLService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(request.farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get crop history for better recommendations
    crop_history = await db.get_crop_history_by_farm_id(request.farm_id)
    
    # Get ML recommendations
    recommendations = await ml_service.get_crop_recommendations(
        farm_data=farm,
        season=request.season.value,
        year=request.year,
        crop_history=crop_history
    )
    
    # Save recommendation to database
    recommendation_id = str(uuid.uuid4())
    await db.create_recommendation({
        "id": recommendation_id,
        "farm_id": request.farm_id,
        "recommended_crops": [rec.dict() for rec in recommendations],
        "rotation_plan": None,
        "sustainability_score": None
    })
    
    response = CropRecommendationResponse(
        farm_id=request.farm_id,
        season=request.season,
        recommendations=recommendations,
        generated_at=datetime.utcnow()
    )
    
    return APIResponse(
        success=True,
        message="Crop recommendations generated successfully",
        data=response.dict()
    )


@crops_router.post("/rotation", response_model=APIResponse)
async def get_crop_rotation(
    request: CropRotationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get optimized crop rotation plan.
    
    Args:
        request: Crop rotation request
        current_user: Current authenticated user
        
    Returns:
        Multi-year crop rotation plan
    """
    db = DatabaseService()
    rotation_service = CropRotationService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(request.farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get crop history
    crop_history = await db.get_crop_history_by_farm_id(request.farm_id)
    
    # Generate rotation plan
    rotation_plan = await rotation_service.generate_rotation_plan(
        farm_data=farm,
        crop_history=crop_history,
        years=request.years
    )
    
    # Calculate sustainability score
    sustainability_score = await rotation_service.calculate_sustainability_score(
        rotation_plan, farm
    )
    
    # Save rotation plan
    rotation_id = str(uuid.uuid4())
    await db.create_recommendation({
        "id": rotation_id,
        "farm_id": request.farm_id,
        "recommended_crops": None,
        "rotation_plan": rotation_plan.dict(),
        "sustainability_score": sustainability_score
    })
    
    return APIResponse(
        success=True,
        message="Crop rotation plan generated successfully",
        data={
            "rotation_plan": rotation_plan.dict(),
            "sustainability_score": sustainability_score
        }
    )


@crops_router.get("/recommendations/{farm_id}", response_model=APIResponse)
async def get_saved_recommendations(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get saved crop recommendations for a farm.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        List of saved recommendations
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    recommendations = await db.get_recommendations_by_farm_id(farm_id)
    
    return APIResponse(
        success=True,
        message="Saved recommendations retrieved successfully",
        data=recommendations
    )


@crops_router.get("/popular", response_model=APIResponse)
async def get_popular_crops():
    """
    Get popular crops in Jharkhand based on adoption data.
    
    Returns:
        List of popular crops with adoption statistics
    """
    db = DatabaseService()
    popular_crops = await db.get_popular_crops()
    
    return APIResponse(
        success=True,
        message="Popular crops retrieved successfully",
        data=popular_crops
    )


@crops_router.get("/suitable/{district}", response_model=APIResponse)
async def get_suitable_crops_by_district(district: str):
    """
    Get crops suitable for a specific district in Jharkhand.
    
    Args:
        district: District name
        
    Returns:
        List of suitable crops for the district
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    db = DatabaseService()
    suitable_crops = await db.get_suitable_crops_by_district(district)
    
    return APIResponse(
        success=True,
        message=f"Suitable crops for {district} retrieved successfully",
        data=suitable_crops
    )