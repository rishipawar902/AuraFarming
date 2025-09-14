"""
Configuration settings for AuraFarming backend.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database Configuration
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # External API Configuration
    OPENWEATHER_API_KEY: str
    AGMARKNET_API_KEY: Optional[str] = None
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Federated Learning Configuration
    FL_ROUNDS: int = 5
    FL_CLIENTS: int = 10
    DIFFERENTIAL_PRIVACY_EPSILON: float = 1.0
    
    # Application URLs
    BACKEND_URL: Optional[str] = "http://localhost:8000"
    FRONTEND_URL: Optional[str] = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Jharkhand districts for location validation
JHARKHAND_DISTRICTS = [
    "Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum",
    "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara",
    "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu",
    "Ramgarh", "Ranchi", "Sahibganj", "Seraikela Kharsawan", "Simdega", "West Singhbhum"
]

# Supported crops for Jharkhand
JHARKHAND_CROPS = [
    "Rice", "Wheat", "Maize", "Finger Millet", "Arhar", "Moong", "Urad", 
    "Lathyrus", "Groundnut", "Sesame", "Niger", "Sugarcane", "Jute", 
    "Mesta", "Cotton", "Tobacco", "Potato", "Sweet Potato", "Onion", 
    "Garlic", "Tomato", "Brinjal", "Okra", "Bottle Gourd", "Bitter Gourd",
    "Cucumber", "Watermelon", "Mango", "Litchi", "Guava", "Papaya"
]

# Soil types in Jharkhand
JHARKHAND_SOIL_TYPES = [
    "Red Soil", "Laterite Soil", "Alluvial Soil", "Black Soil", 
    "Sandy Soil", "Clay Soil", "Loamy Soil"
]

# Irrigation methods
IRRIGATION_METHODS = [
    "Rain-fed", "Tube well", "Dug well", "Canal", "Tank", "River", 
    "Drip irrigation", "Sprinkler irrigation"
]