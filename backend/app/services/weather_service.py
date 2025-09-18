# Weather service for fetching weather data from WeatherAPI.com
# WeatherAPI.com offers 1 million free API calls per month with excellent data quality

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self):
        self.api_key = settings.WEATHERAPI_KEY
        self.base_url = "https://api.weatherapi.com/v1"
        
        # Check if we have a real API key
        self.use_real_api = (
            self.api_key and 
            self.api_key != "mock_weatherapi_key" and 
            len(self.api_key) > 10
        )
        
        logger.info(f"WeatherService initialized with API key: {self.api_key[:10]}...")
        
        if not self.use_real_api:
            raise ValueError("Weather API key not configured. Real weather data is required.")
        else:
            logger.info("Using real WeatherAPI.com data")
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather for given coordinates using WeatherAPI.com."""
        logger.info(f"Getting current weather for {latitude}, {longitude} - use_real_api: {self.use_real_api}")
        
        if not self.use_real_api:
            raise ValueError("Weather API key not configured. Real weather data is required.")
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                logger.info(f"Making WeatherAPI.com current weather request: {self.base_url}/current.json?q={latitude},{longitude}")
                response = await client.get(
                    f"{self.base_url}/current.json",
                    params={
                        "key": self.api_key,
                        "q": f"{latitude},{longitude}",
                        "aqi": "no"  # Air quality data not needed for now
                    }
                )
                logger.info(f"WeatherAPI.com current weather response status: {response.status_code}")
                response.raise_for_status()
                data = response.json()
                logger.info(f"WeatherAPI.com current weather data received for {data.get('location', {}).get('name', 'unknown location')}")
                
                current = data["current"]
                location = data["location"]
                
                # WeatherAPI.com provides rainfall in mm directly
                rainfall_mm = current.get("precip_mm", 0)
                
                return {
                    # For UI display
                    "temperature": round(current["temp_c"], 1),
                    "humidity": current["humidity"],
                    "pressure": current["pressure_mb"],
                    "wind_speed": current["wind_kph"] / 3.6,  # Convert to m/s
                    "wind_direction": current["wind_degree"],
                    "description": current["condition"]["text"],
                    "icon": current["condition"]["icon"],
                    "visibility": current["vis_km"],
                    "feels_like": round(current["feelslike_c"], 1),
                    "uv_index": current["uv"],
                    
                    # For ML model input (standardized format)
                    "ml_data": {
                        "temperature": round(current["temp_c"], 1),  # Celsius
                        "rainfall": rainfall_mm,  # mm (current precipitation)
                        "humidity": current["humidity"],  # %
                    },
                    
                    # Metadata
                    "timestamp": datetime.utcnow().isoformat(),
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "city": location["name"],
                        "region": location["region"],
                        "country": location["country"]
                    },
                    "source": "weatherapi",
                    "api_status": "success"
                }
        
        except Exception as e:
            logger.error(f"Error fetching weather data from WeatherAPI: {str(e)}")
            raise Exception(f"Failed to fetch weather data: {str(e)}. Please check your internet connection and try again.")
    
    async def get_weather_forecast(
        self, 
        latitude: float, 
        longitude: float, 
        days: int = 7
    ) -> Dict[str, Any]:
        """Get weather forecast for given coordinates using WeatherAPI.com."""
        logger.info(f"Getting weather forecast for {latitude}, {longitude}, days={days} - use_real_api: {self.use_real_api}")
        
        if not self.use_real_api:
            raise ValueError("Weather API key not configured. Real weather data is required.")
            
        try:
            # WeatherAPI.com supports up to 14 days forecast
            forecast_days = min(days, 14)
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                logger.info(f"Making WeatherAPI.com forecast request: {self.base_url}/forecast.json?q={latitude},{longitude}&days={forecast_days}")
                response = await client.get(
                    f"{self.base_url}/forecast.json",
                    params={
                        "key": self.api_key,
                        "q": f"{latitude},{longitude}",
                        "days": forecast_days,
                        "aqi": "no",
                        "alerts": "no"
                    }
                )
                logger.info(f"WeatherAPI.com response status: {response.status_code}")
                response.raise_for_status()
                data = response.json()
                logger.info(f"WeatherAPI.com response received for {len(data.get('forecast', {}).get('forecastday', []))} days")
                
                location = data["location"]
                forecast_data = data["forecast"]["forecastday"]
                
                daily_forecasts = []
                for day_data in forecast_data:
                    day = day_data["day"]
                    date_str = day_data["date"]
                    
                    daily_forecasts.append({
                        "date": date_str,
                        "temperature_max": round(day["maxtemp_c"], 1),
                        "temperature_min": round(day["mintemp_c"], 1),
                        "temperature_avg": round(day["avgtemp_c"], 1),
                        "rainfall": round(day["totalprecip_mm"], 1),
                        "humidity_avg": round(day["avghumidity"], 1),
                        "description": day["condition"]["text"],
                        "icon": day["condition"]["icon"],
                        "uv_index": day["uv"],
                        "wind_speed": round(day["maxwind_kph"] / 3.6, 1),  # Convert to m/s
                        # ML-ready data
                        "ml_data": {
                            "temperature": round(day["avgtemp_c"], 1),
                            "rainfall": round(day["totalprecip_mm"], 1),
                            "humidity": round(day["avghumidity"], 1),
                        }
                    })
                
                return {
                    "forecasts": daily_forecasts,
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "city": location["name"],
                        "region": location["region"],
                        "country": location["country"]
                    },
                    "source": "weatherapi",
                    "api_status": "success"
                }
                
        except Exception as e:
            logger.error(f"Error fetching forecast data from WeatherAPI: {str(e)}")
            raise Exception(f"Failed to fetch weather forecast: {str(e)}. Please check your internet connection and try again.")
    
    async def get_weather_for_ml(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get weather data formatted for ML model input."""
        current_weather = await self.get_current_weather(latitude, longitude)
        
        result = {
            "current": current_weather.get("ml_data", {}),
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add forecast data for better ML predictions
        try:
            forecast_data = await self.get_weather_forecast(latitude, longitude, 7)
            if forecast_data.get("forecasts"):
                weekly_temps = [f["ml_data"]["temperature"] for f in forecast_data["forecasts"]]
                weekly_rainfall = [f["ml_data"]["rainfall"] for f in forecast_data["forecasts"]]
                weekly_humidity = [f["ml_data"]["humidity"] for f in forecast_data["forecasts"]]
                
                result["forecast_weekly_avg"] = {
                    "temperature": round(sum(weekly_temps) / len(weekly_temps), 1),
                    "rainfall": round(sum(weekly_rainfall), 1),  # Total rainfall for week
                    "humidity": round(sum(weekly_humidity) / len(weekly_humidity), 1),
                }
        except Exception as e:
            logger.warning(f"Could not fetch forecast for ML: {e}")
        
        return result


# Create a singleton instance
weather_service = WeatherService()
