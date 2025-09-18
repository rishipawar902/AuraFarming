"""
🌾 Smart Advisory API Endpoints
Advanced crop rotation, economic intelligence, and climate adaptation endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from ..services.smart_advisory_service import SmartAdvisoryService

logger = logging.getLogger(__name__)

# Initialize the smart advisory service
smart_advisory_service = SmartAdvisoryService()

# Pydantic models for request/response
class FarmConditions(BaseModel):
    """Farm conditions for advisory generation."""
    soil_type: str = Field(..., description="Soil type: loamy, clay, sandy, silt")
    location: str = Field(default="jharkhand", description="Farm location")
    water_availability: str = Field(default="medium", description="Water availability: low, medium, high")
    farm_size: float = Field(default=1.0, description="Farm size in hectares")
    climate_risk: float = Field(default=0.3, description="Climate risk factor (0-1)")
    
    # Soil parameters
    soil_ph: float = Field(default=6.5, description="Soil pH")
    organic_matter: float = Field(default=2.5, description="Organic matter percentage")
    
    # Current conditions
    current_crop: Optional[str] = Field(default=None, description="Currently grown crop")
    previous_crops: List[str] = Field(default=[], description="Previously grown crops")

class AdvisoryPreferences(BaseModel):
    """Farmer preferences for advisory generation."""
    profit_weight: float = Field(default=0.4, description="Importance of profit (0-1)")
    sustainability_weight: float = Field(default=0.3, description="Importance of sustainability (0-1)")
    risk_weight: float = Field(default=0.3, description="Importance of risk mitigation (0-1)")
    
    preferred_crops: List[str] = Field(default=[], description="Preferred crops")
    avoided_crops: List[str] = Field(default=[], description="Crops to avoid")
    
    max_investment: float = Field(default=100000, description="Maximum investment capacity")
    risk_tolerance: str = Field(default="medium", description="Risk tolerance: low, medium, high")

class RotationPlanResponse(BaseModel):
    """Response model for rotation plan."""
    years: List[Dict[str, Any]]
    total_profit: float
    soil_health_score: float
    sustainability_index: float
    risk_assessment: Dict[str, float]
    recommendations: List[str]

class EconomicAnalysisResponse(BaseModel):
    """Response model for economic analysis."""
    yearly_projections: List[Dict[str, Any]]
    total_profit_3year: float
    total_cost_3year: float
    average_roi: float
    risk_analysis: Dict[str, Any]

class ClimateAnalysisResponse(BaseModel):
    """Response model for climate analysis."""
    climate_assessment: Dict[str, Any]
    crop_risks: List[Dict[str, Any]]
    overall_risk_score: float
    adaptation_plan: Dict[str, List[str]]
    emergency_protocols: Dict[str, List[str]]

class ComprehensiveAdvisoryResponse(BaseModel):
    """Complete advisory response."""
    rotation_plan: RotationPlanResponse
    economic_analysis: EconomicAnalysisResponse
    climate_analysis: ClimateAnalysisResponse
    integrated_recommendations: List[str]
    advisory_summary: Dict[str, Any]
    timestamp: str

class CropRotationRequest(BaseModel):
    """Request for crop rotation optimization."""
    farm_conditions: FarmConditions
    preferences: Optional[AdvisoryPreferences] = None

# Create router
smart_advisory_router = APIRouter()

@smart_advisory_router.post("/rotation/optimize", response_model=RotationPlanResponse)
async def optimize_crop_rotation(request: CropRotationRequest):
    """
    Generate optimized 3-year crop rotation plan.
    
    Returns intelligent crop rotation sequence optimizing:
    - Soil health and nutrient balance
    - Economic returns and risk management
    - Sustainability and environmental impact
    """
    try:
        logger.info("🌾 Generating optimized crop rotation plan...")
        
        # Convert Pydantic models to dictionaries
        farm_conditions = request.farm_conditions.dict()
        preferences = request.preferences.dict() if request.preferences else None
        
        # Generate rotation plan
        rotation_plan = smart_advisory_service.rotation_optimizer.optimize_rotation(
            farm_conditions, preferences
        )
        
        # Convert to response format
        response_data = {
            "years": rotation_plan.years,
            "total_profit": rotation_plan.total_profit,
            "soil_health_score": rotation_plan.soil_health_score,
            "sustainability_index": rotation_plan.sustainability_index,
            "risk_assessment": rotation_plan.risk_assessment,
            "recommendations": rotation_plan.recommendations
        }
        
        logger.info(f"✅ Generated rotation plan: {' → '.join([year['crop'] for year in rotation_plan.years])}")
        return RotationPlanResponse(**response_data)
        
    except Exception as e:
        logger.error(f"❌ Rotation optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Rotation optimization failed: {str(e)}")

@smart_advisory_router.post("/economic/analysis", response_model=EconomicAnalysisResponse)
async def analyze_economic_potential(request: CropRotationRequest):
    """
    Analyze economic potential and market intelligence.
    
    Provides detailed economic analysis including:
    - Profit projections and ROI calculations
    - Market risk assessment
    - Cost-benefit analysis
    - Investment recommendations
    """
    try:
        logger.info("💰 Analyzing economic potential...")
        
        # Convert request to dictionaries
        farm_conditions = request.farm_conditions.dict()
        preferences = request.preferences.dict() if request.preferences else None
        
        # Generate rotation plan first
        rotation_plan = smart_advisory_service.rotation_optimizer.optimize_rotation(
            farm_conditions, preferences
        )
        
        # Calculate economic analysis
        economic_analysis = smart_advisory_service.economic_intelligence.calculate_profit_projection(
            rotation_plan
        )
        
        logger.info(f"✅ Economic analysis complete. 3-year profit: ₹{economic_analysis['total_profit_3year']:,.0f}")
        return EconomicAnalysisResponse(**economic_analysis)
        
    except Exception as e:
        logger.error(f"❌ Economic analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Economic analysis failed: {str(e)}")

@smart_advisory_router.post("/climate/adaptation", response_model=ClimateAnalysisResponse)
async def assess_climate_adaptation(request: CropRotationRequest):
    """
    Assess climate risks and adaptation strategies.
    
    Provides comprehensive climate analysis including:
    - Weather pattern analysis and risk assessment
    - Crop vulnerability evaluation
    - Adaptation strategy recommendations
    - Emergency response protocols
    """
    try:
        logger.info("🌡️ Assessing climate adaptation needs...")
        
        # Convert request to dictionaries
        farm_conditions = request.farm_conditions.dict()
        preferences = request.preferences.dict() if request.preferences else None
        
        # Generate rotation plan first
        rotation_plan = smart_advisory_service.rotation_optimizer.optimize_rotation(
            farm_conditions, preferences
        )
        
        # Assess climate risks
        farm_location = farm_conditions.get('location', 'jharkhand')
        climate_analysis = smart_advisory_service.climate_adaptation.assess_climate_risk(
            farm_location, rotation_plan
        )
        
        logger.info(f"✅ Climate analysis complete. Risk score: {climate_analysis['overall_risk_score']:.2f}")
        return ClimateAnalysisResponse(**climate_analysis)
        
    except Exception as e:
        logger.error(f"❌ Climate analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Climate analysis failed: {str(e)}")

@smart_advisory_router.post("/comprehensive", response_model=ComprehensiveAdvisoryResponse)
async def generate_comprehensive_advisory(request: CropRotationRequest):
    """
    Generate comprehensive smart advisory report.
    
    Provides complete agricultural advisory including:
    - Optimized 3-year crop rotation plan
    - Economic intelligence and profit projections
    - Climate adaptation strategies
    - Integrated recommendations across all domains
    - Executive summary and action plan
    """
    try:
        logger.info("🚀 Generating comprehensive smart advisory...")
        
        # Convert request to dictionaries
        farm_conditions = request.farm_conditions.dict()
        preferences = request.preferences.dict() if request.preferences else None
        
        # Generate comprehensive advisory
        advisory = smart_advisory_service.generate_comprehensive_advisory(
            farm_conditions, preferences
        )
        
        # Convert to response format
        response_data = {
            "rotation_plan": RotationPlanResponse(
                years=advisory['rotation_plan'].years,
                total_profit=advisory['rotation_plan'].total_profit,
                soil_health_score=advisory['rotation_plan'].soil_health_score,
                sustainability_index=advisory['rotation_plan'].sustainability_index,
                risk_assessment=advisory['rotation_plan'].risk_assessment,
                recommendations=advisory['rotation_plan'].recommendations
            ),
            "economic_analysis": EconomicAnalysisResponse(**advisory['economic_analysis']),
            "climate_analysis": ClimateAnalysisResponse(**advisory['climate_analysis']),
            "integrated_recommendations": advisory['integrated_recommendations'],
            "advisory_summary": advisory['advisory_summary'],
            "timestamp": advisory['timestamp']
        }
        
        rotation_crops = ' → '.join([year['crop'] for year in advisory['rotation_plan'].years])
        total_profit = advisory['rotation_plan'].total_profit
        
        logger.info(f"✅ Comprehensive advisory generated!")
        logger.info(f"📊 Rotation: {rotation_crops}")
        logger.info(f"💰 3-year profit: ₹{total_profit:,.0f}")
        logger.info(f"🌱 Sustainability score: {advisory['rotation_plan'].soil_health_score:.1%}")
        
        return ComprehensiveAdvisoryResponse(**response_data)
        
    except Exception as e:
        logger.error(f"❌ Comprehensive advisory failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive advisory failed: {str(e)}")

@smart_advisory_router.get("/crops/database")
async def get_crop_database():
    """
    Get available crop database information.
    
    Returns information about all crops in the system including:
    - Nutrient requirements and contributions
    - Soil and climate preferences
    - Economic parameters
    - Growth characteristics
    """
    try:
        logger.info("📚 Retrieving crop database...")
        
        crop_db = smart_advisory_service.rotation_optimizer.crop_database
        
        # Convert CropInfo objects to dictionaries
        database = {}
        for crop_name, crop_info in crop_db.items():
            database[crop_name] = {
                'name': crop_info.name,
                'nutrient_demand': crop_info.nutrient_demand,
                'nutrient_contribution': crop_info.nutrient_contribution,
                'soil_type_preference': crop_info.soil_type_preference,
                'season': crop_info.season,
                'water_requirement': crop_info.water_requirement,
                'profit_per_hectare': crop_info.profit_per_hectare,
                'market_volatility': crop_info.market_volatility,
                'pest_susceptibility': crop_info.pest_susceptibility,
                'disease_resistance': crop_info.disease_resistance,
                'growth_period': crop_info.growth_period
            }
        
        logger.info(f"✅ Retrieved {len(database)} crops from database")
        return {
            "crops": database,
            "total_crops": len(database),
            "categories": {
                "cereals": ["rice", "wheat", "maize"],
                "legumes": ["chickpea", "soybean"],
                "cash_crops": ["cotton", "sugarcane"],
                "oilseeds": ["mustard"]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve crop database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database retrieval failed: {str(e)}")

@smart_advisory_router.get("/market/trends")
async def get_market_trends():
    """
    Get current market trends and price forecasts.
    
    Returns market intelligence including:
    - Current crop prices
    - Seasonal price variations
    - Market trends and demand forecasts
    - Trading recommendations
    """
    try:
        logger.info("📈 Retrieving market trends...")
        
        market_data = smart_advisory_service.economic_intelligence.market_data
        
        # Add trend analysis
        trends_analysis = {
            "market_data": market_data,
            "price_outlook": {
                "bullish_crops": [crop for crop, data in market_data.items() 
                                if data.get('trend') == 'increasing'],
                "stable_crops": [crop for crop, data in market_data.items() 
                               if data.get('trend') == 'stable'],
                "volatile_crops": [crop for crop, data in market_data.items() 
                                 if data.get('trend') == 'volatile']
            },
            "recommendations": [
                "Focus on cotton and wheat for price appreciation potential",
                "Monitor maize prices closely due to volatility",
                "Rice offers stable returns with lower market risk"
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info("✅ Market trends retrieved successfully")
        return trends_analysis
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve market trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Market trends retrieval failed: {str(e)}")

@smart_advisory_router.get("/status")
async def get_advisory_system_status():
    """Get the status of the smart advisory system."""
    try:
        return {
            "status": "operational",
            "services": {
                "crop_rotation_optimizer": "active",
                "economic_intelligence": "active", 
                "climate_adaptation": "active"
            },
            "capabilities": [
                "3-year crop rotation optimization",
                "Economic intelligence and profit projections",
                "Climate risk assessment and adaptation",
                "Integrated agricultural advisory"
            ],
            "supported_regions": ["jharkhand"],
            "crop_database_size": len(smart_advisory_service.rotation_optimizer.crop_database),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

class SeasonalAdvisoryRequest(BaseModel):
    """Request model for seasonal advisory."""
    location: str = Field(..., description="Farm location")
    soil_type: str = Field(..., description="Soil type")
    current_season: str = Field(..., description="Current season: Kharif, Rabi, Zaid")
    climate_conditions: Optional[Dict[str, float]] = Field(default={}, description="Climate data")

@smart_advisory_router.post("/seasonal")
async def generate_seasonal_advisory(request: SeasonalAdvisoryRequest):
    """
    Generate seasonal farming advisory based on current conditions.
    
    Provides season-specific recommendations including:
    - Suitable crops for the current season
    - Seasonal farming practices
    - Weather-specific precautions
    - Market timing advice
    """
    try:
        logger.info(f"🌱 Generating seasonal advisory for {request.current_season} season")
        
        # Mock seasonal advisory data for now
        seasonal_recommendations = {
            "Kharif": {
                "suitable_crops": ["Rice", "Maize", "Sugarcane", "Cotton", "Arhar"],
                "practices": [
                    "Prepare fields before monsoon arrival",
                    "Ensure proper drainage systems",
                    "Monitor for pest infestations during humid conditions"
                ],
                "precautions": [
                    "Watch for waterlogging in low-lying areas",
                    "Apply appropriate fungicides during monsoon",
                    "Maintain seed beds at proper elevation"
                ]
            },
            "Rabi": {
                "suitable_crops": ["Wheat", "Barley", "Mustard", "Peas", "Gram"],
                "practices": [
                    "Sow crops after monsoon withdrawal",
                    "Ensure adequate irrigation facilities",
                    "Apply winter-appropriate fertilizers"
                ],
                "precautions": [
                    "Protect crops from frost damage",
                    "Monitor soil moisture levels",
                    "Watch for aphid infestations"
                ]
            },
            "Zaid": {
                "suitable_crops": ["Fodder Crops", "Vegetables", "Watermelon", "Muskmelon"],
                "practices": [
                    "Ensure reliable irrigation",
                    "Use heat-resistant varieties",
                    "Provide adequate shade for sensitive crops"
                ],
                "precautions": [
                    "Monitor water stress indicators",
                    "Protect from heat waves",
                    "Apply mulching to conserve moisture"
                ]
            }
        }
        
        season_data = seasonal_recommendations.get(request.current_season, seasonal_recommendations["Kharif"])
        
        # Generate climate-specific advice
        climate_advice = []
        if request.climate_conditions:
            temp = request.climate_conditions.get('temperature', 25)
            humidity = request.climate_conditions.get('humidity', 70)
            rainfall = request.climate_conditions.get('rainfall', 0)
            
            if temp > 35:
                climate_advice.append("High temperature alert: Provide shade and increase irrigation frequency")
            if humidity > 80:
                climate_advice.append("High humidity: Monitor for fungal diseases")
            if rainfall > 100:
                climate_advice.append("Heavy rainfall expected: Ensure proper drainage")
        
        response = {
            "season": request.current_season,
            "location": request.location,
            "suitable_crops": season_data["suitable_crops"],
            "seasonal_practices": season_data["practices"],
            "precautions": season_data["precautions"],
            "climate_specific_advice": climate_advice,
            "market_timing": {
                "best_sowing_time": f"Early {request.current_season} season",
                "expected_harvest": f"End of {request.current_season} season",
                "market_outlook": "Favorable based on seasonal demand patterns"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Seasonal advisory generated for {request.current_season}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Seasonal advisory failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Seasonal advisory failed: {str(e)}")