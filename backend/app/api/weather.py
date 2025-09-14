"""
Weather API routes with enhanced real-time data integration.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Response
from app.models.schemas import WeatherForecast, APIResponse
from app.core.security import get_current_user
from app.services.database import DatabaseService
from app.services.weather_service import weather_service
import logging

logger = logging.getLogger(__name__)
weather_router = APIRouter()


@weather_router.get("/current/{farm_id}", response_model=APIResponse)
async def get_current_weather(
    farm_id: str,
    response: Response,
    current_user: dict = Depends(get_current_user)
):
    """
    Get current weather for a farm location with rate limiting and caching.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Current weather data
    """
    # Set cache control headers for 30 minutes to prevent excessive API calls
    response.headers["Cache-Control"] = "public, max-age=1800"  # 30 minutes
    response.headers["Pragma"] = "cache"
    
    logger.info(f"🌤️ Getting current weather for farm_id: {farm_id} (with 30min cache)")
    
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    logger.info(f"Farm found: {farm.get('name', 'N/A')} at {farm['location']}")
    
    # Get current weather using the enhanced weather service
    weather_data = await weather_service.get_current_weather(
        latitude=farm["location"]["latitude"],
        longitude=farm["location"]["longitude"]
    )
    
    logger.info(f"Weather data retrieved for {farm['location']}")
    
    return APIResponse(
        success=True,
        message="Current weather retrieved successfully",
        data=weather_data
    )
    
    # Get current weather using the enhanced weather service
    weather_data = await weather_service.get_current_weather(
        latitude=farm["location"]["latitude"],
        longitude=farm["location"]["longitude"]
    )
    
    logger.info(f"Weather data retrieved: {weather_data.get('source', 'unknown')} source")
    
    return APIResponse(
        success=True,
        message="Current weather retrieved successfully",
        data=weather_data
    )


@weather_router.get("/forecast/{farm_id}", response_model=APIResponse)
async def get_weather_forecast(
    farm_id: str,
    response: Response,
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    Get weather forecast for a farm location with rate limiting and caching.
    
    Args:
        farm_id: Farm ID
        days: Number of forecast days (1-7)
        current_user: Current authenticated user
        
    Returns:
        Weather forecast data
    """
    # Set cache control headers for 1 hour to prevent excessive API calls
    response.headers["Cache-Control"] = "public, max-age=3600"  # 1 hour
    response.headers["Pragma"] = "cache"
    
    logger.info(f"🌦️ Getting weather forecast for farm_id: {farm_id}, days: {days} (with 1hr cache)")
    
    if days < 1 or days > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forecast days must be between 1 and 7"
        )
    
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    logger.info(f"Farm found for forecast: {farm.get('name', 'N/A')} at {farm['location']}")
    
    # Get weather forecast using the enhanced weather service
    forecast_data = await weather_service.get_weather_forecast(
        latitude=farm["location"]["latitude"],
        longitude=farm["location"]["longitude"],
        days=days
    )
    
    logger.info(f"Forecast data retrieved: {len(forecast_data.get('forecasts', []))} days")
    
    return APIResponse(
        success=True,
        message=f"{days}-day weather forecast retrieved successfully",
        data=forecast_data
    )
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    logger.info(f"Farm found for forecast: {farm.get('name', 'N/A')} at {farm['location']}")
    
    # Get weather forecast using the enhanced weather service
    forecast_data = await weather_service.get_weather_forecast(
        latitude=farm["location"]["latitude"],
        longitude=farm["location"]["longitude"],
        days=days
    )
    
    logger.info(f"Forecast data retrieved: {len(forecast_data.get('forecasts', []))} days")
    
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
    Get weather alerts and advisories for farming with caching.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Weather alerts and farming advisories
    """
    logger.info(f"⚠️ Getting weather alerts for farm_id: {farm_id}")
    
    db = DatabaseService()
    farmer_id = current_user["user_id"]
    
    # Verify farm ownership
    farm = await db.get_farm_by_id(farm_id)
    if not farm or farm["farmer_id"] != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    # Get current weather and generate basic alerts
    weather_data = await weather_service.get_current_weather(
        latitude=farm["location"]["latitude"],
        longitude=farm["location"]["longitude"]
    )
    
    # Generate basic farming alerts based on weather
    alerts = []
    if weather_data.get("temperature", 0) > 35:
        alerts.append({
            "type": "heat_warning",
            "message": "High temperature detected. Ensure adequate irrigation for crops.",
            "severity": "medium"
        })
    
    if weather_data.get("ml_data", {}).get("rainfall", 0) > 50:
        alerts.append({
            "type": "heavy_rain",
            "message": "Heavy rainfall expected. Check drainage and protect sensitive crops.",
            "severity": "high"
        })
    
    return APIResponse(
        success=True,
        message="Weather alerts retrieved successfully",
        data={"alerts": alerts, "weather": weather_data}
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
    
    # Return mock seasonal data for now
    # TODO: Implement actual seasonal patterns using historical weather data
    seasonal_data = {
        "district": district,
        "seasons": {
            "kharif": {
                "months": ["June", "July", "August", "September"],
                "avg_temperature": 28.5,
                "avg_rainfall": 1200,
                "humidity": 75
            },
            "rabi": {
                "months": ["November", "December", "January", "February"],
                "avg_temperature": 22.0,
                "avg_rainfall": 50,
                "humidity": 65
            },
            "summer": {
                "months": ["March", "April", "May"],
                "avg_temperature": 35.0,
                "avg_rainfall": 100,
                "humidity": 55
            }
        }
    }
    
    return APIResponse(
        success=True,
        message=f"Seasonal weather patterns for {district} retrieved successfully",
        data=seasonal_data
    )


@weather_router.get("/ml-enhanced/{farm_id}", response_model=APIResponse)
async def get_ml_enhanced_weather(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get weather data formatted for ML model input.
    
    Args:
        farm_id: Farm ID
        current_user: Current authenticated user
        
    Returns:
        Weather data optimized for ML model features
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
    
    # Get ML-optimized weather data
    ml_weather_data = await weather_service.get_weather_for_ml(
        latitude=farm["location"]["latitude"],
        longitude=farm["location"]["longitude"]
    )
    
    return APIResponse(
        success=True,
        message="ML-enhanced weather data retrieved successfully",
        data=ml_weather_data
    )