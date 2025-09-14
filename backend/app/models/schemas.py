"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LanguageEnum(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    HINDI = "hi"


class SoilTypeEnum(str, Enum):
    """Soil types in Jharkhand."""
    RED_SOIL = "Red Soil"
    LATERITE_SOIL = "Laterite Soil"
    ALLUVIAL_SOIL = "Alluvial Soil"
    BLACK_SOIL = "Black Soil"
    SANDY_SOIL = "Sandy Soil"
    CLAY_SOIL = "Clay Soil"
    LOAMY_SOIL = "Loamy Soil"


class IrrigationMethodEnum(str, Enum):
    """Irrigation methods."""
    RAIN_FED = "Rain-fed"
    TUBE_WELL = "Tube well"
    DUG_WELL = "Dug well"
    CANAL = "Canal"
    TANK = "Tank"
    RIVER = "River"
    DRIP_IRRIGATION = "Drip irrigation"
    SPRINKLER_IRRIGATION = "Sprinkler irrigation"


class SeasonEnum(str, Enum):
    """Farming seasons."""
    KHARIF = "Kharif"
    RABI = "Rabi"
    ZAID = "Zaid"


# Authentication Models
class FarmerRegister(BaseModel):
    """Farmer registration request."""
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., regex=r"^[6-9]\d{9}$")
    password: str = Field(..., min_length=6)
    language: LanguageEnum = LanguageEnum.ENGLISH


class FarmerLogin(BaseModel):
    """Farmer login request."""
    phone: str = Field(..., regex=r"^[6-9]\d{9}$")
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Farm Models
class FarmLocation(BaseModel):
    """Farm location coordinates."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    district: str
    village: Optional[str] = None


class FarmProfile(BaseModel):
    """Farm profile creation/update."""
    location: FarmLocation
    soil_type: SoilTypeEnum
    irrigation_method: IrrigationMethodEnum
    field_size: float = Field(..., gt=0, description="Field size in acres")


class FarmResponse(BaseModel):
    """Farm profile response."""
    id: str
    farmer_id: str
    location: FarmLocation
    soil_type: str
    irrigation_method: str
    field_size: float
    created_at: datetime


# Crop Models
class CropHistory(BaseModel):
    """Historical crop data."""
    season: SeasonEnum
    crop: str
    yield_per_acre: Optional[float] = Field(None, ge=0)
    year: int = Field(..., ge=2020, le=2025)


class CropRecommendationRequest(BaseModel):
    """Crop recommendation request."""
    farm_id: str
    season: SeasonEnum
    year: int = Field(default=2024, ge=2024, le=2030)


class CropRecommendation(BaseModel):
    """Single crop recommendation."""
    crop_name: str
    confidence: float = Field(..., ge=0, le=1)
    expected_yield: float
    profit_potential: str
    risk_level: str
    water_requirement: str
    fertilizer_recommendation: Dict[str, Any]
    market_demand: str


class CropRecommendationResponse(BaseModel):
    """Crop recommendation response."""
    farm_id: str
    season: SeasonEnum
    recommendations: List[CropRecommendation]
    generated_at: datetime


class CropRotationRequest(BaseModel):
    """Crop rotation optimization request."""
    farm_id: str
    years: int = Field(default=3, ge=2, le=5)


class CropRotationPlan(BaseModel):
    """Crop rotation plan."""
    year: int
    season: SeasonEnum
    recommended_crop: str
    benefits: List[str]
    considerations: List[str]


class CropRotationResponse(BaseModel):
    """Crop rotation response."""
    farm_id: str
    rotation_plan: List[CropRotationPlan]
    overall_benefits: List[str]
    sustainability_score: float


# Weather Models
class WeatherData(BaseModel):
    """Weather data."""
    temperature: float
    humidity: float
    rainfall: float
    wind_speed: float
    description: str
    date: datetime


class WeatherForecast(BaseModel):
    """Weather forecast response."""
    location: FarmLocation
    current_weather: WeatherData
    forecast: List[WeatherData]
    generated_at: datetime


# Market Models
class MarketPrice(BaseModel):
    """Market price data."""
    crop: str
    market: str
    min_price: float
    max_price: float
    modal_price: float
    unit: str = "per quintal"
    date: datetime


class MarketPriceResponse(BaseModel):
    """Market price response."""
    district: str
    prices: List[MarketPrice]
    last_updated: datetime


# Finance Models
class FinancialRecommendation(BaseModel):
    """Financial recommendation."""
    type: str  # loan, insurance, subsidy
    scheme_name: str
    eligibility: str
    benefits: str
    application_process: str
    contact_info: str


class FinanceResponse(BaseModel):
    """Finance recommendations response."""
    farmer_id: str
    recommendations: List[FinancialRecommendation]
    pm_kisan_status: str
    generated_at: datetime


# Sustainability Models
class SustainabilityMetrics(BaseModel):
    """Sustainability metrics."""
    carbon_footprint: float
    water_efficiency: float
    fertilizer_efficiency: float
    biodiversity_score: float
    soil_health_score: float


class SustainabilityResponse(BaseModel):
    """Sustainability scoring response."""
    farm_id: str
    metrics: SustainabilityMetrics
    overall_score: float = Field(..., ge=0, le=100)
    recommendations: List[str]
    generated_at: datetime


# Admin Models
class AdminStats(BaseModel):
    """Admin dashboard statistics."""
    total_farmers: int
    total_farms: int
    total_recommendations: int
    popular_crops: List[Dict[str, Any]]
    district_wise_adoption: Dict[str, int]


class AdminResponse(BaseModel):
    """Admin dashboard response."""
    stats: AdminStats
    generated_at: datetime


# Common Models
class APIResponse(BaseModel):
    """Standard API response."""
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    status_code: int
    path: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)