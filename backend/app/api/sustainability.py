"""
Sustainability scoring API routes.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import SustainabilityResponse, APIResponse
from app.core.security import get_current_user
from app.services.database import DatabaseService
from app.services.sustainability_service import SustainabilityService

sustainability_router = APIRouter()


@sustainability_router.get("/score/{farm_id}", response_model=APIResponse)
async def get_sustainability_score(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get sustainability score for a farm.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Comprehensive sustainability scoring
    """
    db = DatabaseService()
    sustainability_service = SustainabilityService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get crop history for analysis
    crop_history = await db.get_crop_history_by_farm_id(farm_id)
    
    # Calculate sustainability metrics
    sustainability_data = await sustainability_service.calculate_sustainability_score(
        farm, crop_history
    )
    
    return APIResponse(
        success=True,
        message="Sustainability score calculated successfully",
        data=sustainability_data
    )


@sustainability_router.get("/carbon-footprint/{farm_id}", response_model=APIResponse)
async def get_carbon_footprint(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get carbon footprint analysis for a farm.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Detailed carbon footprint analysis
    """
    db = DatabaseService()
    sustainability_service = SustainabilityService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get crop history
    crop_history = await db.get_crop_history_by_farm_id(farm_id)
    
    # Calculate carbon footprint
    carbon_data = await sustainability_service.calculate_carbon_footprint(
        farm, crop_history
    )
    
    return APIResponse(
        success=True,
        message="Carbon footprint analysis completed successfully",
        data=carbon_data
    )


@sustainability_router.get("/water-efficiency/{farm_id}", response_model=APIResponse)
async def get_water_efficiency(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get water use efficiency analysis.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Water efficiency metrics and recommendations
    """
    db = DatabaseService()
    sustainability_service = SustainabilityService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get crop history
    crop_history = await db.get_crop_history_by_farm_id(farm_id)
    
    # Calculate water efficiency
    water_data = await sustainability_service.calculate_water_efficiency(
        farm, crop_history
    )
    
    return APIResponse(
        success=True,
        message="Water efficiency analysis completed successfully",
        data=water_data
    )


@sustainability_router.get("/soil-health/{farm_id}", response_model=APIResponse)
async def get_soil_health(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get soil health assessment.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Soil health metrics and improvement recommendations
    """
    db = DatabaseService()
    sustainability_service = SustainabilityService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get crop history
    crop_history = await db.get_crop_history_by_farm_id(farm_id)
    
    # Assess soil health
    soil_data = await sustainability_service.assess_soil_health(
        farm, crop_history
    )
    
    return APIResponse(
        success=True,
        message="Soil health assessment completed successfully",
        data=soil_data
    )


@sustainability_router.get("/biodiversity/{farm_id}", response_model=APIResponse)
async def get_biodiversity_score(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get biodiversity impact score.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Biodiversity impact assessment
    """
    db = DatabaseService()
    sustainability_service = SustainabilityService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get crop history
    crop_history = await db.get_crop_history_by_farm_id(farm_id)
    
    # Calculate biodiversity score
    biodiversity_data = await sustainability_service.calculate_biodiversity_score(
        farm, crop_history
    )
    
    return APIResponse(
        success=True,
        message="Biodiversity score calculated successfully",
        data=biodiversity_data
    )


@sustainability_router.get("/recommendations/{farm_id}", response_model=APIResponse)
async def get_sustainability_recommendations(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get sustainability improvement recommendations.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Actionable sustainability recommendations
    """
    db = DatabaseService()
    sustainability_service = SustainabilityService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get crop history
    crop_history = await db.get_crop_history_by_farm_id(farm_id)
    
    # Get sustainability recommendations
    recommendations = await sustainability_service.get_sustainability_recommendations(
        farm, crop_history
    )
    
    return APIResponse(
        success=True,
        message="Sustainability recommendations generated successfully",
        data=recommendations
    )