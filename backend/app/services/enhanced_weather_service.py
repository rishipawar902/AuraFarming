"""
Enhanced Weather Service for AuraFarming with multiple API providers and fallback.
Supports OpenWeatherMap, WeatherAPI, and realistic fallback data for Jharkhand.
"""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import random
import json
from app.core.config import settings
from app.core.districts import JHARKHAND_DISTRICT_COORDINATES

logger = logging.getLogger(__name__)


class EnhancedWeatherService:
    """
    Enhanced weather service with multiple API providers and intelligent fallback.
    Provides reliable weather data for Jharkhand farming operations.
    """
    
    def __init__(self):
        """Initialize enhanced weather service with multiple providers."""
        # Primary API key (WeatherAPI.com)
        self.weatherapi_key = getattr(settings, 'WEATHERAPI_KEY', None)
        
        # Secondary provider
        self.openweather_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
        
        # API endpoints
        self.weatherapi_base = "https://api.weatherapi.com/v1"
        self.openweather_base = "https://api.openweathermap.org/data/2.5"
        
        # Jharkhand-specific weather patterns for fallback
        self.jharkhand_weather_patterns = self._initialize_jharkhand_weather()
        
        if self.weatherapi_key:
            logger.info(f"Enhanced weather service initialized with WeatherAPI as primary")
            logger.info(f"WeatherAPI key configured: {self.weatherapi_key[:10]}...")
        else:
            logger.warning("No WeatherAPI key configured - using fallback data only")
            logger.info("Enhanced weather service initialized with fallback data")
    
    def _initialize_jharkhand_weather(self) -> Dict[str, Any]:
        """Initialize realistic weather patterns for Jharkhand state."""
        
        # Jharkhand seasonal weather patterns
        current_month = datetime.now().month
        
        # Monsoon season (June-September)
        if 6 <= current_month <= 9:
            base_temp = {"min": 22, "max": 32, "humidity": 80}
            rain_chance = 70
            weather_desc = "Monsoon season"
        # Winter season (December-February)
        elif 12 <= current_month <= 2:
            base_temp = {"min": 8, "max": 25, "humidity": 45}
            rain_chance = 10
            weather_desc = "Winter season"
        # Summer season (March-May)
        elif 3 <= current_month <= 5:
            base_temp = {"min": 20, "max": 40, "humidity": 35}
            rain_chance = 20
            weather_desc = "Summer season"
        # Post-monsoon (October-November)
        else:
            base_temp = {"min": 15, "max": 30, "humidity": 55}
            rain_chance = 25
            weather_desc = "Post-monsoon season"
        
        return {
            "base_temperature": base_temp,
            "rain_probability": rain_chance,
            "season_description": weather_desc,
            "district_variations": {
                "Ranchi": {"temp_offset": 0, "humidity_offset": 0},
                "Dhanbad": {"temp_offset": 2, "humidity_offset": -5},
                "Jamshedpur": {"temp_offset": 1, "humidity_offset": -3},
                "Bokaro": {"temp_offset": -1, "humidity_offset": 2},
                "Hazaribagh": {"temp_offset": -2, "humidity_offset": 5},
                "Deoghar": {"temp_offset": 0, "humidity_offset": 3},
                "Giridih": {"temp_offset": 1, "humidity_offset": -2},
                "Ramgarh": {"temp_offset": -1, "humidity_offset": 1},
                "Medininagar": {"temp_offset": 0, "humidity_offset": 0},
                "Chaibasa": {"temp_offset": -1, "humidity_offset": 2}
            }
        }
    
    async def get_current_weather(self, latitude: float, longitude: float, district: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current weather with multiple provider fallback.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            district: Optional district name for enhanced accuracy
            
        Returns:
            Current weather data with farming-relevant information
        """
        logger.info(f"Getting enhanced weather for {latitude}, {longitude} (district: {district})")
        
        # Try primary provider (WeatherAPI.com)
        weather_data = await self._try_weatherapi(latitude, longitude)
        
        if weather_data:
            logger.info("✅ Got weather data from WeatherAPI.com")
            return self._format_weather_response(weather_data, "weatherapi", district)
        
        # Try secondary provider (OpenWeatherMap)
        weather_data = await self._try_openweather(latitude, longitude)
        
        if weather_data:
            logger.info("✅ Got weather data from OpenWeatherMap")
            return self._format_weather_response(weather_data, "openweathermap", district)
        
        # If no real API data available, return error instead of fallback
        logger.warning("❌ NO REAL weather API data available - all services failed")
        return {
            "status": "no_data",
            "message": "Weather services unavailable - no real-time data",
            "district": district or "Unknown",
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.now().isoformat(),
            "error": "All weather APIs failed or not configured"
        }
    
    async def _try_openweather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Try getting weather from OpenWeatherMap API."""
        try:
            # Skip if no API key available
            if not self.openweather_key:
                logger.info("OpenWeatherMap API key not configured, skipping")
                return None
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.openweather_base}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.openweather_key,
                        "units": "metric"
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"OpenWeatherMap API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.warning(f"OpenWeatherMap API failed: {str(e)}")
            return None
    
    async def _try_weatherapi(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Try getting weather from WeatherAPI.com."""
        if not self.weatherapi_key or self.weatherapi_key == "mock_weatherapi_key":
            return None
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.weatherapi_base}/current.json",
                    params={
                        "key": self.weatherapi_key,
                        "q": f"{lat},{lon}",
                        "aqi": "no"
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"WeatherAPI error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.warning(f"WeatherAPI failed: {str(e)}")
            return None
    
    def _format_weather_response(self, raw_data: Dict[str, Any], source: str, district: Optional[str] = None) -> Dict[str, Any]:
        """Format weather data from different providers into unified response."""
        
        if source == "openweathermap":
            # OpenWeatherMap format
            current_time = datetime.now()
            return {
                "status": "success",
                "data_source": f"openweathermap_api",
                "location": {
                    "latitude": raw_data["coord"]["lat"],
                    "longitude": raw_data["coord"]["lon"],
                    "district": district or "Unknown",
                    "city": raw_data["name"]
                },
                "current": {
                    "temperature": round(raw_data["main"]["temp"], 1),
                    "feels_like": round(raw_data["main"]["feels_like"], 1),
                    "humidity": raw_data["main"]["humidity"],
                    "pressure": raw_data["main"]["pressure"],
                    "wind_speed": raw_data["wind"]["speed"],
                    "wind_direction": raw_data["wind"].get("deg", 0),
                    "visibility": raw_data.get("visibility", 10000) / 1000,  # Convert to km
                    "description": raw_data["weather"][0]["description"].title(),
                    "icon": raw_data["weather"][0]["icon"]
                },
                "farming_insights": self._generate_farming_insights(raw_data["main"]["temp"], raw_data["main"]["humidity"], raw_data["weather"][0]["main"]),
                "last_updated": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "cache_duration": 1800  # 30 minutes
            }
            
        elif source == "weatherapi":
            # WeatherAPI format
            current_time = datetime.now()
            current = raw_data["current"]
            return {
                "status": "success",
                "data_source": f"weatherapi_com",
                "location": {
                    "latitude": raw_data["location"]["lat"],
                    "longitude": raw_data["location"]["lon"],
                    "district": district or "Unknown",
                    "city": raw_data["location"]["name"]
                },
                "current": {
                    "temperature": current["temp_c"],
                    "feels_like": current["feelslike_c"],
                    "humidity": current["humidity"],
                    "pressure": current["pressure_mb"],
                    "wind_speed": current["wind_kph"] / 3.6,  # Convert to m/s
                    "wind_direction": current["wind_degree"],
                    "visibility": current["vis_km"],
                    "description": current["condition"]["text"],
                    "icon": current["condition"]["icon"]
                },
                "farming_insights": self._generate_farming_insights(current["temp_c"], current["humidity"], current["condition"]["text"]),
                "last_updated": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "cache_duration": 1800  # 30 minutes
            }
    
    def _get_enhanced_fallback_weather(self, lat: float, lon: float, district: Optional[str] = None) -> Dict[str, Any]:
        """Generate realistic fallback weather data for Jharkhand."""
        
        patterns = self.jharkhand_weather_patterns
        base_temp = patterns["base_temperature"]
        
        # Apply district-specific variations
        district_adjustment = {"temp_offset": 0, "humidity_offset": 0}
        if district and district in patterns["district_variations"]:
            district_adjustment = patterns["district_variations"][district]
        
        # Generate realistic weather values
        current_temp = random.uniform(
            base_temp["min"] + district_adjustment["temp_offset"],
            base_temp["max"] + district_adjustment["temp_offset"]
        )
        
        humidity = max(20, min(95, base_temp["humidity"] + district_adjustment["humidity_offset"] + random.randint(-10, 10)))
        
        # Generate weather conditions based on season
        weather_conditions = self._get_seasonal_weather_condition(patterns["rain_probability"])
        
        current_time = datetime.now()
        
        return {
            "status": "success",
            "data_source": "enhanced_fallback_jharkhand",
            "location": {
                "latitude": lat,
                "longitude": lon,
                "district": district or "Jharkhand",
                "city": district or "Unknown"
            },
            "current": {
                "temperature": round(current_temp, 1),
                "feels_like": round(current_temp + random.uniform(-2, 3), 1),
                "humidity": int(humidity),
                "pressure": random.randint(1008, 1018),
                "wind_speed": round(random.uniform(2, 12), 1),
                "wind_direction": random.randint(0, 360),
                "visibility": round(random.uniform(8, 15), 1),
                "description": weather_conditions["description"],
                "icon": weather_conditions["icon"]
            },
            "farming_insights": self._generate_farming_insights(current_temp, humidity, weather_conditions["description"]),
            "seasonal_info": {
                "season": patterns["season_description"],
                "farming_phase": self._get_farming_phase(),
                "recommended_activities": self._get_seasonal_farming_activities()
            },
            "last_updated": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "cache_duration": 1800  # 30 minutes
        }
    
    def _get_seasonal_weather_condition(self, rain_chance: int) -> Dict[str, str]:
        """Get appropriate weather condition based on season."""
        
        if random.randint(1, 100) <= rain_chance:
            # Rainy conditions
            conditions = [
                {"description": "Light Rain", "icon": "10d"},
                {"description": "Moderate Rain", "icon": "10d"},
                {"description": "Heavy Rain", "icon": "09d"},
                {"description": "Thunderstorm", "icon": "11d"}
            ]
        else:
            # Clear/cloudy conditions
            conditions = [
                {"description": "Clear Sky", "icon": "01d"},
                {"description": "Partly Cloudy", "icon": "02d"},
                {"description": "Scattered Clouds", "icon": "03d"},
                {"description": "Overcast", "icon": "04d"}
            ]
        
        return random.choice(conditions)
    
    def _get_farming_phase(self) -> str:
        """Get current farming phase based on season."""
        month = datetime.now().month
        
        if 3 <= month <= 5:
            return "Summer crop preparation"
        elif 6 <= month <= 9:
            return "Kharif season (monsoon crops)"
        elif 10 <= month <= 11:
            return "Harvest season"
        else:
            return "Rabi season (winter crops)"
    
    def _get_seasonal_farming_activities(self) -> List[str]:
        """Get recommended farming activities for current season."""
        month = datetime.now().month
        
        if 3 <= month <= 5:  # Summer
            return [
                "Prepare fields for kharif crops",
                "Install irrigation systems",
                "Summer plowing",
                "Soil testing and preparation"
            ]
        elif 6 <= month <= 9:  # Monsoon
            return [
                "Plant rice and other kharif crops",
                "Ensure proper drainage",
                "Monitor pest and diseases",
                "Apply organic fertilizers"
            ]
        elif 10 <= month <= 11:  # Post-monsoon
            return [
                "Harvest kharif crops",
                "Prepare for rabi season",
                "Store harvested crops",
                "Plan winter crop varieties"
            ]
        else:  # Winter
            return [
                "Plant wheat and other rabi crops",
                "Irrigation management",
                "Winter crop maintenance",
                "Market preparation for harvest"
            ]
    
    def _generate_farming_insights(self, temperature: float, humidity: int, condition: str) -> Dict[str, Any]:
        """Generate farming-specific insights based on weather conditions."""
        
        insights = {
            "irrigation_recommendation": "moderate",
            "pest_risk": "low",
            "disease_risk": "low",
            "field_work_suitability": "good",
            "recommendations": []
        }
        
        # Temperature-based insights
        if temperature > 35:
            insights["irrigation_recommendation"] = "high"
            insights["field_work_suitability"] = "poor"
            insights["recommendations"].append("Avoid midday field work due to high temperature")
            insights["recommendations"].append("Increase irrigation frequency")
        elif temperature < 10:
            insights["field_work_suitability"] = "limited"
            insights["recommendations"].append("Protect crops from cold")
        
        # Humidity-based insights
        if humidity > 80:
            insights["disease_risk"] = "high"
            insights["recommendations"].append("Monitor for fungal diseases")
            insights["irrigation_recommendation"] = "low"
        elif humidity < 30:
            insights["irrigation_recommendation"] = "high"
            insights["recommendations"].append("Increase irrigation due to low humidity")
        
        # Condition-based insights
        if "rain" in condition.lower():
            insights["field_work_suitability"] = "poor"
            insights["irrigation_recommendation"] = "none"
            insights["recommendations"].append("Avoid field operations during rain")
            insights["recommendations"].append("Ensure proper drainage")
        
        if "thunderstorm" in condition.lower():
            insights["field_work_suitability"] = "dangerous"
            insights["recommendations"].append("Stay indoors during thunderstorm")
        
        return insights
    
    async def get_weather_forecast(self, latitude: float, longitude: float, days: int = 7, district: Optional[str] = None) -> Dict[str, Any]:
        """
        Get weather forecast with multiple provider fallback.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of days (1-7)
            district: Optional district name
            
        Returns:
            Weather forecast data
        """
        logger.info(f"Getting {days}-day forecast for {latitude}, {longitude}")
        
        # Try OpenWeatherMap One Call API (if available)
        forecast_data = await self._try_openweather_forecast(latitude, longitude, days)
        
        if forecast_data:
            logger.info("✅ Got forecast from OpenWeatherMap")
            return self._format_forecast_response(forecast_data, "openweathermap", district, days)
        
        # If no real API forecast available, return error instead of fallback
        logger.warning("❌ NO REAL forecast API data available")
        return {
            "status": "no_data",
            "message": "Weather forecast services unavailable - no real-time data",
            "district": district or "Unknown", 
            "latitude": latitude,
            "longitude": longitude,
            "days": days,
            "timestamp": datetime.now().isoformat(),
            "error": "Weather forecast APIs not configured or failed"
        }
    
    async def _try_openweather_forecast(self, lat: float, lon: float, days: int) -> Optional[Dict[str, Any]]:
        """Try getting forecast from OpenWeatherMap (5-day forecast)."""
        try:
            # Skip if no API key available
            if not self.openweather_key:
                logger.info("OpenWeatherMap API key not configured, skipping forecast")
                return None
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.openweather_base}/forecast",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.openweather_key,
                        "units": "metric"
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"OpenWeatherMap forecast API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.warning(f"OpenWeatherMap forecast failed: {str(e)}")
            return None
            logger.warning(f"OpenWeatherMap forecast API failed: {str(e)}")
            return None
    
    def _format_forecast_response(self, raw_data: Dict[str, Any], source: str, district: Optional[str], days: int) -> Dict[str, Any]:
        """Format forecast data into unified response."""
        
        if source == "openweathermap":
            forecasts = []
            for item in raw_data["list"][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                forecast_time = datetime.fromtimestamp(item["dt"])
                if forecast_time.hour == 12:  # Noon forecast for daily summary
                    forecasts.append({
                        "date": forecast_time.strftime("%Y-%m-%d"),
                        "temperature_max": round(item["main"]["temp_max"], 1),
                        "temperature_min": round(item["main"]["temp_min"], 1),
                        "humidity": item["main"]["humidity"],
                        "description": item["weather"][0]["description"].title(),
                        "icon": item["weather"][0]["icon"],
                        "rain_probability": int(item.get("pop", 0) * 100)
                    })
            
            return {
                "status": "success",
                "data_source": "openweathermap_forecast",
                "location": {
                    "latitude": raw_data["city"]["coord"]["lat"],
                    "longitude": raw_data["city"]["coord"]["lon"],
                    "district": district or "Unknown",
                    "city": raw_data["city"]["name"]
                },
                "forecast": forecasts[:days],
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _get_enhanced_fallback_forecast(self, lat: float, lon: float, days: int, district: Optional[str]) -> Dict[str, Any]:
        """Generate realistic forecast fallback data for Jharkhand."""
        
        patterns = self.jharkhand_weather_patterns
        base_temp = patterns["base_temperature"]
        
        # Apply district-specific variations
        district_adjustment = {"temp_offset": 0, "humidity_offset": 0}
        if district and district in patterns["district_variations"]:
            district_adjustment = patterns["district_variations"][district]
        
        forecasts = []
        base_date = datetime.now()
        
        for day in range(days):
            forecast_date = base_date + timedelta(days=day)
            
            # Add daily variations
            daily_temp_variation = random.uniform(-3, 3)
            daily_humidity_variation = random.randint(-10, 10)
            
            temp_max = base_temp["max"] + district_adjustment["temp_offset"] + daily_temp_variation
            temp_min = base_temp["min"] + district_adjustment["temp_offset"] + daily_temp_variation
            humidity = max(20, min(95, base_temp["humidity"] + district_adjustment["humidity_offset"] + daily_humidity_variation))
            
            # Weather condition for the day
            weather_conditions = self._get_seasonal_weather_condition(patterns["rain_probability"])
            
            forecasts.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "temperature_max": round(temp_max, 1),
                "temperature_min": round(temp_min, 1),
                "humidity": int(humidity),
                "description": weather_conditions["description"],
                "icon": weather_conditions["icon"],
                "rain_probability": patterns["rain_probability"]
            })
        
        return {
            "status": "success",
            "data_source": "enhanced_fallback_jharkhand_forecast",
            "location": {
                "latitude": lat,
                "longitude": lon,
                "district": district or "Jharkhand",
                "city": district or "Unknown"
            },
            "forecast": forecasts,
            "seasonal_info": {
                "season": patterns["season_description"],
                "farming_phase": self._get_farming_phase()
            },
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


# Create global instance
enhanced_weather_service = EnhancedWeatherService()
