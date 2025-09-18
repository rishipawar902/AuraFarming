"""
Enhanced Financial services API routes.
Comprehensive financial intelligence for agricultural success.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import FinanceResponse, APIResponse
from app.core.security import get_current_user
from app.services.database import DatabaseService
from app.services.finance_service import FinanceService
from app.services.enhanced_finance_service import enhanced_finance_service

finance_router = APIRouter()


@finance_router.get("/profile/comprehensive", response_model=APIResponse)
async def get_comprehensive_financial_profile(current_user: dict = Depends(get_current_user)):
    """
    Get comprehensive financial profile with enhanced analysis.
    
    Provides complete financial intelligence including:
    - Financial health scoring
    - Government scheme eligibility
    - Personalized loan recommendations
    - Insurance product suggestions
    - Investment opportunities
    - PM-KISAN integration
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Comprehensive financial profile with personalized recommendations
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    try:
        # Get farmer and farm data
        farmer = await db.get_farmer_by_id(farmer_id)
        farm = await db.get_farm_by_farmer_id(farmer_id)
        
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer profile not found"
            )
        
        # Get comprehensive financial profile
        financial_profile = await enhanced_finance_service.get_comprehensive_financial_profile(
            farmer, farm
        )
        
        return APIResponse(
            success=True,
            message="Comprehensive financial profile retrieved successfully",
            data=financial_profile
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve financial profile: {str(e)}"
        )


@finance_router.get("/recommendations", response_model=APIResponse)
async def get_financial_recommendations(current_user: dict = Depends(get_current_user)):
    """
    Get enhanced personalized financial recommendations.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Enhanced financial recommendations with government schemes and investments
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    try:
        # Get farmer and farm data
        farmer = await db.get_farmer_by_id(farmer_id)
        farm = await db.get_farm_by_farmer_id(farmer_id)
        
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer not found"
            )
        
        # Get comprehensive profile and extract recommendations
        financial_profile = await enhanced_finance_service.get_comprehensive_financial_profile(
            farmer, farm
        )
        
        recommendations_data = {
            "financial_health": financial_profile["financial_health_score"],
            "schemes": financial_profile["scheme_eligibility"],
            "loans": financial_profile["loan_products"][:3],  # Top 3 loan products
            "investments": financial_profile["investment_opportunities"][:3],  # Top 3 investments
            "recommendations": financial_profile["recommendations"]
        }
        
        return APIResponse(
            success=True,
            message="Enhanced financial recommendations retrieved successfully",
            data=recommendations_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recommendations: {str(e)}"
        )


@finance_router.get("/pm-kisan/status", response_model=APIResponse)
async def get_pm_kisan_status(current_user: dict = Depends(get_current_user)):
    """
    Get enhanced PM-KISAN scheme status and benefits information.
    
    Provides detailed PM-KISAN integration including:
    - Registration status and beneficiary ID
    - Installment history and payment status
    - Total received and pending amounts
    - Real-time status from government portal
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Enhanced PM-KISAN status with complete payment history
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    try:
        # Get farmer data
        farmer = await db.get_farmer_by_id(farmer_id)
        
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer profile not found"
            )
        
        # Get enhanced PM-KISAN status
        pm_kisan_status = await enhanced_finance_service.check_pm_kisan_status(farmer)
        
        return APIResponse(
            success=True,
            message="PM-KISAN status retrieved successfully",
            data=pm_kisan_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve PM-KISAN status: {str(e)}"
        )


@finance_router.get("/loans/products", response_model=APIResponse)
async def get_loan_products(current_user: dict = Depends(get_current_user)):
    """
    Get personalized loan product recommendations.
    
    Provides comprehensive loan analysis including:
    - Eligibility-based product filtering
    - Personalized interest rates and terms
    - EMI calculations and affordability analysis
    - Documentation requirements
    - Government subsidy opportunities
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Personalized loan products with detailed terms and conditions
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    try:
        # Get farmer and farm data
        farmer = await db.get_farmer_by_id(farmer_id)
        farm = await db.get_farm_by_farmer_id(farmer_id)
        
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer profile not found"
            )
        
        # Get comprehensive profile and extract loan products
        financial_profile = await enhanced_finance_service.get_comprehensive_financial_profile(
            farmer, farm
        )
        
        loan_data = {
            "financial_health": financial_profile["financial_health_score"],
            "loan_products": financial_profile["loan_products"],
            "eligibility_factors": financial_profile["financial_metrics"],
            "scheme_eligibility": financial_profile["scheme_eligibility"]
        }
        
        return APIResponse(
            success=True,
            message="Personalized loan products retrieved successfully",
            data=loan_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve loan products: {str(e)}"
        )


@finance_router.get("/investments/opportunities", response_model=APIResponse)
async def get_investment_opportunities(current_user: dict = Depends(get_current_user)):
    """
    Get personalized investment and subsidy opportunities.
    
    Provides comprehensive investment analysis including:
    - Equipment and infrastructure recommendations
    - Government subsidy calculations
    - ROI analysis and payback periods
    - Financing options and loan integration
    - Priority-based recommendations
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Personalized investment opportunities with subsidy details
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    try:
        # Get farmer and farm data
        farmer = await db.get_farmer_by_id(farmer_id)
        farm = await db.get_farm_by_farmer_id(farmer_id)
        
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer profile not found"
            )
        
        # Get comprehensive profile and extract investment opportunities
        financial_profile = await enhanced_finance_service.get_comprehensive_financial_profile(
            farmer, farm
        )
        
        investment_data = {
            "financial_health": financial_profile["financial_health_score"],
            "investment_opportunities": financial_profile["investment_opportunities"],
            "financial_capacity": financial_profile["financial_metrics"],
            "loan_products": [loan for loan in financial_profile["loan_products"] if "equipment" in loan["type"].lower()]
        }
        
        return APIResponse(
            success=True,
            message="Investment opportunities retrieved successfully",
            data=investment_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve investment opportunities: {str(e)}"
        )


@finance_router.get("/health-score", response_model=APIResponse)
async def get_financial_health_score(current_user: dict = Depends(get_current_user)):
    """
    Get detailed financial health assessment.
    
    Provides comprehensive financial health analysis including:
    - Multi-factor scoring algorithm
    - Risk assessment and creditworthiness
    - Performance benchmarking
    - Improvement recommendations
    - Trend analysis and projections
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Detailed financial health score with actionable insights
    """
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    try:
        # Get farmer and farm data
        farmer = await db.get_farmer_by_id(farmer_id)
        farm = await db.get_farm_by_farmer_id(farmer_id)
        
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer profile not found"
            )
        
        # Get comprehensive profile and extract health score
        financial_profile = await enhanced_finance_service.get_comprehensive_financial_profile(
            farmer, farm
        )
        
        health_data = {
            "financial_health_score": financial_profile["financial_health_score"],
            "financial_metrics": financial_profile["financial_metrics"],
            "recommendations": financial_profile["recommendations"],
            "improvement_areas": [
                rec for rec in financial_profile["recommendations"] 
                if any(word in rec.lower() for word in ["improve", "increase", "reduce", "optimize"])
            ]
        }
        
        return APIResponse(
            success=True,
            message="Financial health score retrieved successfully",
            data=health_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve financial health score: {str(e)}"
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