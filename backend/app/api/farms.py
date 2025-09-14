"""
Farm management API routes.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.schemas import (
    FarmProfile, FarmResponse, CropHistory, APIResponse
)
from app.core.security import get_current_user
from app.services.database import DatabaseService
from app.core.config import JHARKHAND_DISTRICTS
import uuid

farms_router = APIRouter()


@farms_router.post("/profile", response_model=APIResponse)
async def create_farm_profile(
    farm_data: FarmProfile,
    current_user: dict = Depends(get_current_user)
):
    """
    Create or update farm profile.
    
    Args:
        farm_data: Farm profile data
        current_user: Current authenticated user
        
    Returns:
        Created farm profile
        
    Raises:
        HTTPException: If district is not in Jharkhand
    """
    try:
        # Validate district
        if farm_data.location.district not in JHARKHAND_DISTRICTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
            )
        
        db = DatabaseService()
        farmer_id = current_user["user_id"]
        
        # Check if farm already exists for this farmer
        existing_farm = await db.get_farm_by_farmer_id(farmer_id)
        
        farm_id = str(uuid.uuid4())
        farm_dict = {
            "id": farm_id,
            "farmer_id": farmer_id,
            "location": {
                "latitude": farm_data.location.latitude,
                "longitude": farm_data.location.longitude,
                "district": farm_data.location.district,
                "village": farm_data.location.village
            },
            "soil_type": farm_data.soil_type.value,
            "irrigation_method": farm_data.irrigation_method.value,
            "field_size": farm_data.field_size
        }
        
        if existing_farm:
            # Update existing farm
            farm_dict["id"] = existing_farm["id"]
            farm = await db.update_farm(existing_farm["id"], farm_dict)
            message = "Farm profile updated successfully"
        else:
            # Create new farm
            farm = await db.create_farm(farm_dict)
            message = "Farm profile created successfully"
        
        return APIResponse(
            success=True,
            message=message,
            data=farm
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating farm profile: {str(e)}"
        )


@farms_router.get("/profile", response_model=APIResponse)
async def get_farm_profile(current_user: dict = Depends(get_current_user)):
    """
    Get farm profile for current farmer.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Farm profile data
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    farm = await db.get_farm_by_farmer_id(farmer_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm profile not found. Please create a farm profile first."
        )
    
    return APIResponse(
        success=True,
        message="Farm profile retrieved successfully",
        data=farm
    )


@farms_router.post("/crop-history", response_model=APIResponse)
async def add_crop_history(
    crop_data: CropHistory,
    current_user: dict = Depends(get_current_user)
):
    """
    Add crop history entry.
    
    Args:
        crop_data: Crop history data
        current_user: Current authenticated user
        
    Returns:
        Created crop history entry
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    # Get farm for this farmer
    farm = await db.get_farm_by_farmer_id(farmer_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm profile not found. Please create a farm profile first."
        )
    
    crop_history_id = str(uuid.uuid4())
    crop_history = await db.create_crop_history({
        "id": crop_history_id,
        "farm_id": farm["id"],
        "season": crop_data.season.value,
        "crop": crop_data.crop,
        "yield_per_acre": crop_data.yield_per_acre,
        "year": crop_data.year
    })
    
    return APIResponse(
        success=True,
        message="Crop history added successfully",
        data=crop_history
    )


@farms_router.get("/crop-history", response_model=APIResponse)
async def get_crop_history(current_user: dict = Depends(get_current_user)):
    """
    Get crop history for current farmer's farm.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of crop history entries
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    # Get farm for this farmer
    farm = await db.get_farm_by_farmer_id(farmer_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm profile not found. Please create a farm profile first."
        )
    
    crop_history = await db.get_crop_history_by_farm_id(farm["id"])
    
    return APIResponse(
        success=True,
        message="Crop history retrieved successfully",
        data=crop_history
    )


@farms_router.delete("/crop-history/{history_id}", response_model=APIResponse)
async def delete_crop_history(
    history_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete crop history entry.
    
    Args:
        history_id: Crop history entry ID
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    # Verify ownership
    crop_history = await db.get_crop_history_by_id(history_id)
    if not crop_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop history entry not found"
        )
    
    # Get farm to verify ownership
    farm = await db.get_farm_by_id(crop_history["farm_id"])
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this crop history entry"
        )
    
    await db.delete_crop_history(history_id)
    
    return APIResponse(
        success=True,
        message="Crop history entry deleted successfully"
    )