"""
Financial services API routes.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import FinanceResponse, APIResponse
from app.core.security import get_current_user
from app.services.database import DatabaseService
from app.services.finance_service import FinanceService

finance_router = APIRouter()


@finance_router.get("/recommendations", response_model=APIResponse)
async def get_financial_recommendations(current_user: dict = Depends(get_current_user)):
    """
    Get personalized financial recommendations.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Financial recommendations including loans, insurance, and subsidies
    """
    db = DatabaseService()
    finance_service = FinanceService()
    farmer_id = current_user["user_id"]
    
    # Get farmer and farm data
    farmer = await db.get_farmer_by_id(farmer_id)
    farm = await db.get_farm_by_farmer_id(farmer_id)
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Get financial recommendations
    recommendations = await finance_service.get_recommendations(farmer, farm)
    
    return APIResponse(
        success=True,
        message="Financial recommendations retrieved successfully",
        data=recommendations
    )


@finance_router.get("/pm-kisan/status", response_model=APIResponse)
async def get_pm_kisan_status(current_user: dict = Depends(get_current_user)):
    """
    Get PM-KISAN scheme status and eligibility.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        PM-KISAN status and benefits information
    """
    db = DatabaseService()
    finance_service = FinanceService()
    farmer_id = current_user["user_id"]
    
    # Get farmer data
    farmer = await db.get_farmer_by_id(farmer_id)
    farm = await db.get_farm_by_farmer_id(farmer_id)
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Check PM-KISAN status
    pm_kisan_data = await finance_service.check_pm_kisan_status(farmer, farm)
    
    return APIResponse(
        success=True,
        message="PM-KISAN status retrieved successfully",
        data=pm_kisan_data
    )


@finance_router.get("/loans/agriculture", response_model=APIResponse)
async def get_agriculture_loans(current_user: dict = Depends(get_current_user)):
    """
    Get available agriculture loan schemes.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of applicable agriculture loan schemes
    """
    db = DatabaseService()
    finance_service = FinanceService()
    farmer_id = current_user["user_id"]
    
    # Get farmer and farm data
    farmer = await db.get_farmer_by_id(farmer_id)
    farm = await db.get_farm_by_farmer_id(farmer_id)
    
    # Get loan options
    loans = await finance_service.get_agriculture_loans(farmer, farm)
    
    return APIResponse(
        success=True,
        message="Agriculture loan schemes retrieved successfully",
        data=loans
    )


@finance_router.get("/insurance/crop", response_model=APIResponse)
async def get_crop_insurance(current_user: dict = Depends(get_current_user)):
    """
    Get crop insurance options and coverage.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Available crop insurance schemes
    """
    db = DatabaseService()
    finance_service = FinanceService()
    farmer_id = current_user["user_id"]
    
    # Get farmer and farm data
    farmer = await db.get_farmer_by_id(farmer_id)
    farm = await db.get_farm_by_farmer_id(farmer_id)
    
    # Get insurance options
    insurance = await finance_service.get_crop_insurance(farmer, farm)
    
    return APIResponse(
        success=True,
        message="Crop insurance options retrieved successfully",
        data=insurance
    )


@finance_router.get("/subsidies", response_model=APIResponse)
async def get_subsidies(current_user: dict = Depends(get_current_user)):
    """
    Get available government subsidies.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of applicable government subsidies
    """
    db = DatabaseService()
    finance_service = FinanceService()
    farmer_id = current_user["user_id"]
    
    # Get farmer and farm data
    farmer = await db.get_farmer_by_id(farmer_id)
    farm = await db.get_farm_by_farmer_id(farmer_id)
    
    # Get subsidy options
    subsidies = await finance_service.get_subsidies(farmer, farm)
    
    return APIResponse(
        success=True,
        message="Government subsidies retrieved successfully",
        data=subsidies
    )


@finance_router.post("/calculate-income", response_model=APIResponse)
async def calculate_projected_income(
    crop: str,
    area: float,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate projected income for a crop.
    
    Args:
        crop: Crop name
        area: Cultivation area in acres
        current_user: Current authenticated user
        
    Returns:
        Projected income calculation
    """
    if area <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Area must be greater than 0"
        )
    
    db = DatabaseService()
    finance_service = FinanceService()
    farmer_id = current_user["user_id"]
    
    # Get farm data for location
    farm = await db.get_farm_by_farmer_id(farmer_id)
    
    # Calculate projected income
    income_data = await finance_service.calculate_projected_income(crop, area, farm)
    
    return APIResponse(
        success=True,
        message="Projected income calculated successfully",
        data=income_data
    )


@finance_router.get("/micro-finance", response_model=APIResponse)
async def get_microfinance_options(current_user: dict = Depends(get_current_user)):
    """
    Get microfinance and SHG options.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Microfinance and Self Help Group options
    """
    db = DatabaseService()
    finance_service = FinanceService()
    farmer_id = current_user["user_id"]
    
    # Get farmer data
    farmer = await db.get_farmer_by_id(farmer_id)
    farm = await db.get_farm_by_farmer_id(farmer_id)
    
    # Get microfinance options
    microfinance = await finance_service.get_microfinance_options(farmer, farm)
    
    return APIResponse(
        success=True,
        message="Microfinance options retrieved successfully",
        data=microfinance
    )