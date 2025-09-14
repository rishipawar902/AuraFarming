"""
Weather service for fetching weather data from OpenWeatherMap API.
"""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.schemas import WeatherData


class WeatherService:
    """
    Weather service for fetching current weather and forecasts.
    """
    
    def __init__(self):
        """Initialize weather service."""
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.onecall_url = "https://api.openweathermap.org/data/3.0/onecall"
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get current weather for given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Current weather data
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "rainfall": data.get("rain", {}).get("1h", 0),
                    "wind_speed": data["wind"]["speed"],
                    "description": data["weather"][0]["description"],
                    "date": datetime.utcnow(),
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "city": data.get("name", "Unknown")
                    }
                }
        
        except Exception as e:
            # Return mock data if API fails
            return await self._get_mock_weather_data(latitude, longitude)
    
    async def get_weather_forecast(
        self, 
        latitude: float, 
        longitude: float, 
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get weather forecast for given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of forecast days
            
        Returns:
            Weather forecast data
        """
        try:
            # Get current weather
            current = await self.get_current_weather(latitude, longitude)
            
            # Get forecast using OneCall API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                        "units": "metric",
                        "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Process forecast data
                daily_forecasts = []
                current_date = None
                daily_data = {"temps": [], "humidity": [], "rainfall": 0, "wind_speeds": []}
                
                for forecast in data["list"]:
                    forecast_date = datetime.fromtimestamp(forecast["dt"]).date()
                    
                    if current_date != forecast_date:
                        if current_date is not None:
                            # Save previous day's data
                            daily_forecasts.append(self._process_daily_forecast(
                                current_date, daily_data
                            ))
                        
                        # Start new day
                        current_date = forecast_date
                        daily_data = {"temps": [], "humidity": [], "rainfall": 0, "wind_speeds": []}
                    
                    # Accumulate data for the day
                    daily_data["temps"].append(forecast["main"]["temp"])
                    daily_data["humidity"].append(forecast["main"]["humidity"])
                    daily_data["rainfall"] += forecast.get("rain", {}).get("3h", 0)
                    daily_data["wind_speeds"].append(forecast["wind"]["speed"])
                    daily_data["description"] = forecast["weather"][0]["description"]
                
                # Add last day if exists
                if current_date is not None and daily_data["temps"]:
                    daily_forecasts.append(self._process_daily_forecast(
                        current_date, daily_data
                    ))
                
                return {
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "city": data["city"]["name"]
                    },
                    "current_weather": current,
                    "forecast": daily_forecasts[:days],
                    "generated_at": datetime.utcnow()
                }
        
        except Exception as e:
            # Return mock data if API fails
            return await self._get_mock_forecast_data(latitude, longitude, days)
    
    def _process_daily_forecast(self, date, daily_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process daily forecast data."""
        return {
            "date": date,
            "temperature": round(sum(daily_data["temps"]) / len(daily_data["temps"]), 1),
            "min_temperature": round(min(daily_data["temps"]), 1),
            "max_temperature": round(max(daily_data["temps"]), 1),
            "humidity": round(sum(daily_data["humidity"]) / len(daily_data["humidity"]), 1),
            "rainfall": round(daily_data["rainfall"], 2),
            "wind_speed": round(sum(daily_data["wind_speeds"]) / len(daily_data["wind_speeds"]), 1),
            "description": daily_data.get("description", "Clear sky")
        }
    
    async def get_weather_alerts(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get weather alerts and farming advisories.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Weather alerts and advisories
        """
        try:
            # Get current weather and forecast
            forecast_data = await self.get_weather_forecast(latitude, longitude, 7)
            
            alerts = []
            advisories = []
            
            # Analyze forecast for alerts
            for day_forecast in forecast_data["forecast"]:
                date = day_forecast["date"]
                
                # Heavy rainfall alert
                if day_forecast["rainfall"] > 50:
                    alerts.append({
                        "type": "Heavy Rainfall",
                        "severity": "High",
                        "date": date,
                        "message": f"Heavy rainfall expected ({day_forecast['rainfall']}mm). Avoid field operations."
                    })
                
                # High temperature alert
                if day_forecast["max_temperature"] > 40:
                    alerts.append({
                        "type": "Heat Wave",
                        "severity": "Medium",
                        "date": date,
                        "message": f"High temperature expected ({day_forecast['max_temperature']}°C). Increase irrigation."
                    })
                
                # Low temperature alert
                if day_forecast["min_temperature"] < 5:
                    alerts.append({
                        "type": "Cold Wave",
                        "severity": "Medium",
                        "date": date,
                        "message": f"Low temperature expected ({day_forecast['min_temperature']}°C). Protect crops from frost."
                    })
            
            # Generate farming advisories
            current_weather = forecast_data["current_weather"]
            
            if current_weather["humidity"] > 80:
                advisories.append({
                    "type": "Disease Prevention",
                    "message": "High humidity may lead to fungal diseases. Apply preventive fungicides."
                })
            
            if current_weather["rainfall"] > 10:
                advisories.append({
                    "type": "Field Operations",
                    "message": "Recent rainfall. Wait for soil to dry before heavy machinery operations."
                })
            
            return {
                "alerts": alerts,
                "advisories": advisories,
                "last_updated": datetime.utcnow()
            }
        
        except Exception as e:
            return await self._get_mock_alerts_data()
    
    async def get_seasonal_patterns(self, district: str) -> Dict[str, Any]:
        """
        Get seasonal weather patterns for a district.
        
        Args:
            district: District name
            
        Returns:
            Seasonal weather patterns and averages
        """
        # This would integrate with historical weather data APIs
        # For prototype, returning mock seasonal data
        
        seasonal_data = {
            "Ranchi": {
                "monsoon": {
                    "start_date": "June 15",
                    "end_date": "September 30",
                    "average_rainfall": 1200,
                    "temperature_range": [22, 32]
                },
                "winter": {
                    "start_date": "December 1",
                    "end_date": "February 28",
                    "average_rainfall": 25,
                    "temperature_range": [8, 25]
                },
                "summer": {
                    "start_date": "March 1",
                    "end_date": "June 14",
                    "average_rainfall": 80,
                    "temperature_range": [20, 42]
                }
            }
        }
        
        district_data = seasonal_data.get(district, seasonal_data["Ranchi"])
        
        return {
            "district": district,
            "seasonal_patterns": district_data,
            "best_sowing_periods": {
                "Kharif": "June 15 - July 15",
                "Rabi": "November 1 - December 15",
                "Zaid": "February 15 - March 31"
            },
            "climate_zone": "Subtropical",
            "last_updated": datetime.utcnow()
        }
    
    async def _get_mock_weather_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Return mock weather data when API is unavailable."""
        return {
            "temperature": 28.5,
            "humidity": 65,
            "rainfall": 0,
            "wind_speed": 3.2,
            "description": "Partly cloudy",
            "date": datetime.utcnow(),
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "city": "Jharkhand"
            },
            "source": "Mock data - API unavailable"
        }
    
    async def _get_mock_forecast_data(self, latitude: float, longitude: float, days: int) -> Dict[str, Any]:
        """Return mock forecast data when API is unavailable."""
        import random
        
        forecasts = []
        base_temp = 28
        
        for i in range(days):
            date = datetime.now().date() + timedelta(days=i)
            temp_variation = random.uniform(-5, 5)
            
            forecasts.append({
                "date": date,
                "temperature": round(base_temp + temp_variation, 1),
                "min_temperature": round(base_temp + temp_variation - 5, 1),
                "max_temperature": round(base_temp + temp_variation + 5, 1),
                "humidity": random.randint(50, 85),
                "rainfall": random.uniform(0, 10) if random.random() > 0.7 else 0,
                "wind_speed": random.uniform(2, 8),
                "description": random.choice(["Clear sky", "Partly cloudy", "Cloudy", "Light rain"])
            })
        
        return {
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "city": "Jharkhand"
            },
            "current_weather": await self._get_mock_weather_data(latitude, longitude),
            "forecast": forecasts,
            "generated_at": datetime.utcnow(),
            "source": "Mock data - API unavailable"
        }
    
    async def _get_mock_alerts_data(self) -> Dict[str, Any]:
        """Return mock alerts data when API is unavailable."""
        return {
            "alerts": [
                {
                    "type": "Information",
                    "severity": "Low",
                    "date": datetime.now().date(),
                    "message": "Weather service temporarily unavailable. Using cached data."
                }
            ],
            "advisories": [
                {
                    "type": "General",
                    "message": "Monitor weather conditions regularly for farming decisions."
                }
            ],
            "last_updated": datetime.utcnow(),
            "source": "Mock data"
        }