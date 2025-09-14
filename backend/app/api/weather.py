"""
Weather API routes.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import WeatherForecast, APIResponse
from app.core.security import get_current_user
from app.services.database import DatabaseService
from app.services.weather_service import WeatherService

weather_router = APIRouter()


@weather_router.get("/current/{farm_id}", response_model=APIResponse)
async def get_current_weather(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get current weather for a farm location.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Current weather data
    """
    db = DatabaseService()
    weather_service = WeatherService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get current weather
    weather_data = await weather_service.get_current_weather(
        latitude=farm["location"]["latitude"],
        longitude=farm["location"]["longitude"]
    )
    
    return APIResponse(
        success=True,
        message="Current weather retrieved successfully",
        data=weather_data
    )


@weather_router.get("/forecast/{farm_id}", response_model=APIResponse)
async def get_weather_forecast(
    farm_id: str,
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    Get weather forecast for a farm location.
    
    Args:
        farm_id: Farm ID
        days: Number of forecast days (1-7)
        current_user: Current authenticated user
        
    Returns:
        Weather forecast data
    """
    if days < 1 or days > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forecast days must be between 1 and 7"
        )
    
    db = DatabaseService()
    weather_service = WeatherService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get weather forecast
    forecast_data = await weather_service.get_weather_forecast(
        latitude=farm["location"]["latitude"],
        longitude=farm["location"]["longitude"],
        days=days
    )
    
    return APIResponse(
        success=True,
        message=f"{days}-day weather forecast retrieved successfully",
        data=forecast_data
    )


@weather_router.get("/alerts/{farm_id}", response_model=APIResponse)
async def get_weather_alerts(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get weather alerts and advisories for farming.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Weather alerts and farming advisories
    """
    db = DatabaseService()
    weather_service = WeatherService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get weather alerts
    alerts = await weather_service.get_weather_alerts(
        latitude=farm["location"]["latitude"],
        longitude=farm["location"]["longitude"]
    )
    
    return APIResponse(
        success=True,
        message="Weather alerts retrieved successfully",
        data=alerts
    )


@weather_router.get("/seasonal/{district}", response_model=APIResponse)
async def get_seasonal_weather_patterns(district: str):
    """
    Get seasonal weather patterns for a district.
    
    Args:
        district: District name in Jharkhand
        
    Returns:
        Seasonal weather patterns and averages
    """
    from app.core.config import JHARKHAND_DISTRICTS
    
    if district not in JHARKHAND_DISTRICTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District must be one of: {', '.join(JHARKHAND_DISTRICTS)}"
        )
    
    weather_service = WeatherService()
    seasonal_data = await weather_service.get_seasonal_patterns(district)
    
    return APIResponse(
        success=True,
        message=f"Seasonal weather patterns for {district} retrieved successfully",
        data=seasonal_data
    )