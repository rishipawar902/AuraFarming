"""
Market data API routes.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import MarketPriceResponse, APIResponse
from app.services.market_service import MarketService
from typing import Optional

market_router = APIRouter()


@market_router.get("/prices/{district}", response_model=APIResponse)
async def get_mandi_prices(
    district: str,
    crop: Optional[str] = None
):
    """
    Get current mandi prices for a district.
    
    Args:
        district: District name in Jharkhand
        crop: Optional crop filter
        
    Returns:
        Current market prices from Agmarknet
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    market_service = MarketService()
    prices = await market_service.get_mandi_prices(district, crop)
    
    return APIResponse(
        success=True,
        message=f"Market prices for {district} retrieved successfully",
        data=prices
    )


@market_router.get("/trends/{crop}", response_model=APIResponse)
async def get_price_trends(crop: str, days: int = 30):
    """
    Get price trends for a specific crop.
    
    Args:
        crop: Crop name
        days: Number of days for trend analysis (7-90)
        
    Returns:
        Price trend data and analysis
    """
    if days < 7 or days > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be between 7 and 90"
        )
    
    market_service = MarketService()
    trends = await market_service.get_price_trends(crop, days)
    
    return APIResponse(
        success=True,
        message=f"Price trends for {crop} retrieved successfully",
        data=trends
    )


@market_router.get("/forecast/{crop}", response_model=APIResponse)
async def get_price_forecast(crop: str):
    """
    Get price forecast for a specific crop.
    
    Args:
        crop: Crop name
        
    Returns:
        Price forecast for next 30 days
    """
    market_service = MarketService()
    forecast = await market_service.get_price_forecast(crop)
    
    return APIResponse(
        success=True,
        message=f"Price forecast for {crop} retrieved successfully",
        data=forecast
    )


@market_router.get("/best-markets/{crop}", response_model=APIResponse)
async def get_best_markets(crop: str, origin_district: str):
    """
    Get best markets to sell a crop based on price and distance.
    
    Args:
        crop: Crop name
        origin_district: Farmer's district
        
    Returns:
        List of best markets with price and distance information
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if origin_district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    market_service = MarketService()
    best_markets = await market_service.get_best_markets(crop, origin_district)
    
    return APIResponse(
        success=True,
        message=f"Best markets for {crop} from {origin_district} retrieved successfully",
        data=best_markets
    )


@market_router.get("/demand/{district}", response_model=APIResponse)
async def get_market_demand(district: str):
    """
    Get market demand analysis for a district.
    
    Args:
        district: District name
        
    Returns:
        Market demand data and insights
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    market_service = MarketService()
    demand_data = await market_service.get_market_demand(district)
    
    return APIResponse(
        success=True,
        message=f"Market demand analysis for {district} retrieved successfully",
        data=demand_data
    )


@market_router.get("/buyers/{crop}", response_model=APIResponse)
async def get_potential_buyers(crop: str, district: str):
    """
    Get potential buyers and supply chain information.
    
    Args:
        crop: Crop name
        district: District name
        
    Returns:
        List of potential buyers and supply chain options
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    market_service = MarketService()
    buyers = await market_service.get_potential_buyers(crop, district)
    
    return APIResponse(
        success=True,
        message=f"Potential buyers for {crop} in {district} retrieved successfully",
        data=buyers
    )