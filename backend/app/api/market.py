"""
Market data API routes.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import MarketPriceResponse, APIResponse
from app.services.market_service import MarketService
from app.services.multi_source_market_service import MultiSourceMarketService
from typing import Optional

market_router = APIRouter()


@market_router.get("/prices/{district}", response_model=APIResponse)
async def get_mandi_prices(
    district: str,
    crop: Optional[str] = None
):
    """
    Get REAL-TIME market prices for a district from government portals.
    
    Args:
        district: District name in Jharkhand
        crop: Optional crop filter
        
    Returns:
        Real-time market prices from multiple government sources
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    # Use the enhanced multi-source service for real-time data
    multi_source_service = MultiSourceMarketService()
    
    try:
        # Get real-time comprehensive data
        real_time_data = await multi_source_service.get_comprehensive_market_data(district, crop)
        
        if real_time_data.get("status") == "success":
            return APIResponse(
                success=True,
                message=f"Real-time market prices for {district} retrieved successfully",
                data=real_time_data
            )
        else:
            # Fallback to basic market service if real-time fails
            market_service = MarketService()
            fallback_prices = await market_service.get_mandi_prices(district, crop)
            
            return APIResponse(
                success=True,
                message=f"Market prices for {district} retrieved (fallback mode)",
                data=fallback_prices
            )
            
    except Exception as e:
        # Emergency fallback
        market_service = MarketService()
        emergency_prices = await market_service.get_mandi_prices(district, crop)
        
        return APIResponse(
            success=True,
            message=f"Market prices for {district} retrieved (emergency fallback)",
            data=emergency_prices
        )


@market_router.get("/real-time/{district}", response_model=APIResponse)
async def get_real_time_prices(
    district: str,
    commodity: Optional[str] = None
):
    """
    Get REAL-TIME market prices with aggressive scraping from government portals.
    
    Args:
        district: District name in Jharkhand
        commodity: Optional commodity filter
        
    Returns:
        Live real-time prices from AGMARKNET, Data.gov.in, and eNAM
    """
    from app.core.config import JHARKHAND_DISTRICTS
    from app.services.realtime_market_scraper import realtime_scraper
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    try:
        # Get real-time data using aggressive scraping
        real_time_data = await realtime_scraper.get_real_time_prices(district, commodity)
        
        if real_time_data.get("status") == "success":
            return APIResponse(
                success=True,
                message=f"Real-time market prices for {district} retrieved successfully",
                data=real_time_data
            )
        else:
            return APIResponse(
                success=False,
                message=f"Real-time scraping failed for {district}",
                data=real_time_data
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Real-time scraping error: {str(e)}"
        )


@market_router.get("/real-government-data/{district}", response_model=APIResponse)
async def get_real_government_data(
    district: str,
    commodity: Optional[str] = None
):
    """
    Get REAL market data scraped from all government portals (Combined approach).
    
    Args:
        district: District name in Jharkhand
        commodity: Optional commodity filter
        
    Returns:
        Real data scraped from AGMARKNET, Data.gov.in, and eNAM without API keys
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    multi_source_service = MultiSourceMarketService()
    
    try:
        # Get combined real-time + government scraper data
        real_data = await multi_source_service.get_comprehensive_market_data(district, commodity)
        
        # Add data source transparency
        sources_info = {
            "data_quality": real_data.get("data_quality", "UNKNOWN"),
            "scraping_method": real_data.get("scraping_method", "fallback"),
            "sources_used": real_data.get("sources", []),
            "source_summary": real_data.get("source_summary", {}),
            "total_data_points": real_data.get("total_data_points", 0)
        }
        
        message = f"Real government data for {district}"
        if commodity:
            message += f" (commodity: {commodity})"
        
        if real_data.get("data_quality") == "REAL_SCRAPED":
            message += " - Successfully scraped from government portals"
        else:
            message += " - Using professional fallback data"
        
        return APIResponse(
            success=True,
            message=message,
            data={
                "market_data": real_data.get("data", []),
                "data_sources": sources_info,
                "timestamp": real_data.get("timestamp"),
                "district": district,
                "commodity": commodity
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving real government data: {str(e)}"
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