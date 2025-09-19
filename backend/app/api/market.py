"""
Market data API routes.
Enhanced with real-time government data scraping and caching.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import MarketPriceResponse, APIResponse
from app.services.market_service import MarketService
from app.services.cache_service import market_cache
from typing import Optional
import logging

market_router = APIRouter()
logger = logging.getLogger(__name__)


@market_router.get("/prices/{district}/live", response_model=APIResponse)
async def get_live_mandi_prices(
    district: str,
    crop: Optional[str] = None
):
    """
    Get live mandi prices for a district with real-time data.
    
    Args:
        district: District name in Jharkhand
        crop: Optional crop filter
        
    Returns:
        Live market prices from government sources with fallback
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    try:
        market_service = MarketService()
        prices = await market_service.get_mandi_prices(district, crop)
        
        return APIResponse(
            success=True,
            message=f"Live market prices for {district} retrieved successfully",
            data=prices
        )
    except Exception as e:
        logger.error(f"Failed to get live market prices for {district}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve live market prices: {str(e)}"
        )


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


@market_router.get("/analytics/{district}", response_model=APIResponse)
async def get_market_analytics(district: str, timeframe: int = 30):
    """
    Get comprehensive market analytics for a district.
    
    Args:
        district: District name in Jharkhand
        timeframe: Analysis timeframe in days (7-90)
        
    Returns:
        Market analytics including price trends, volume, and insights
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    if timeframe < 7 or timeframe > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timeframe must be between 7 and 90 days"
        )
    
    try:
        market_service = MarketService()
        analytics = await market_service.get_market_analytics(district, timeframe)
        
        return APIResponse(
            success=True,
            message=f"Market analytics for {district} retrieved successfully",
            data=analytics
        )
    except Exception as e:
        logger.error(f"Failed to get market analytics for {district}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve market analytics: {str(e)}"
        )


@market_router.get("/crop-analytics/{crop}", response_model=APIResponse)
async def get_crop_analytics(crop: str, timeframe: int = 30):
    """
    Get analytics for a specific crop across all districts.
    
    Args:
        crop: Crop name
        timeframe: Analysis timeframe in days (7-90)
        
    Returns:
        Crop analytics including price trends, production, and market insights
    """
    if timeframe < 7 or timeframe > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timeframe must be between 7 and 90 days"
        )
    
    try:
        market_service = MarketService()
        analytics = await market_service.get_crop_analytics(crop, timeframe)
        
        return APIResponse(
            success=True,
            message=f"Crop analytics for {crop} retrieved successfully",
            data=analytics
        )
    except Exception as e:
        logger.error(f"Failed to get crop analytics for {crop}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve crop analytics: {str(e)}"
        )


@market_router.get("/yield-analytics/{district}", response_model=APIResponse)
async def get_yield_analytics(district: str, timeframe: int = 90):
    """
    Get yield analytics for a district.
    
    Args:
        district: District name in Jharkhand
        timeframe: Analysis timeframe in days (30-365)
        
    Returns:
        Yield analytics including production trends and forecasts
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    if timeframe < 30 or timeframe > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timeframe must be between 30 and 365 days"
        )
    
    try:
        market_service = MarketService()
        analytics = await market_service.get_yield_analytics(district, timeframe)
        
        return APIResponse(
            success=True,
            message=f"Yield analytics for {district} retrieved successfully",
            data=analytics
        )
    except Exception as e:
        logger.error(f"Failed to get yield analytics for {district}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve yield analytics: {str(e)}"
        )


@market_router.get("/cache/stats", response_model=APIResponse)
async def get_cache_stats():
    """
    Get cache statistics and performance metrics.
    
    Returns:
        Cache statistics including hit ratio, active entries, etc.
    """
    try:
        stats = market_cache.get_cache_stats()
        
        return APIResponse(
            success=True,
            message="Cache statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cache statistics: {str(e)}"
        )


@market_router.post("/cache/invalidate", response_model=APIResponse)
async def invalidate_cache(pattern: Optional[str] = None):
    """
    Invalidate cache entries.
    
    Args:
        pattern: Optional pattern to match cache keys
        
    Returns:
        Number of cache entries invalidated
    """
    try:
        invalidated_count = market_cache.invalidate(pattern)
        
        return APIResponse(
            success=True,
            message=f"Cache invalidated successfully. {invalidated_count} entries removed.",
            data={"invalidated_entries": invalidated_count, "pattern": pattern}
        )
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invalidate cache: {str(e)}"
        )


@market_router.post("/cache/cleanup", response_model=APIResponse)
async def cleanup_expired_cache():
    """
    Clean up expired cache entries.
    
    Returns:
        Number of expired entries removed
    """
    try:
        cleaned_count = market_cache.cleanup_expired()
        
        return APIResponse(
            success=True,
            message=f"Cache cleanup completed. {cleaned_count} expired entries removed.",
            data={"cleaned_entries": cleaned_count}
        )
    except Exception as e:
        logger.error(f"Failed to cleanup cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup cache: {str(e)}"
        )