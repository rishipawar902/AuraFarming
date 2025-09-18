"""
🌾 AuraFarming - Smart Advisory System
Advanced crop rotation optimization, economic intelligence, and climate adaptation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CropInfo:
    """Information about a specific crop for rotation planning."""
    name: str
    nutrient_demand: Dict[str, float]  # N, P, K requirements
    nutrient_contribution: Dict[str, float]  # N, P, K additions (e.g., legumes add N)
    soil_type_preference: List[str]
    season: str  # Kharif, Rabi, Zaid
    water_requirement: float  # mm
    profit_per_hectare: float  # INR
    market_volatility: float  # 0-1 scale
    pest_susceptibility: Dict[str, float]  # pest type -> susceptibility score
    disease_resistance: float  # 0-1 scale
    growth_period: int  # days

@dataclass
class RotationPlan:
    """3-year crop rotation plan with optimization metrics."""
    years: List[Dict[str, Any]]  # Year-by-year plan
    total_profit: float
    soil_health_score: float
    sustainability_index: float
    risk_assessment: Dict[str, float]
    recommendations: List[str]

class CropRotationOptimizer:
    """Intelligent crop rotation optimization for 3-year cycles."""
    
    def __init__(self):
        self.crop_database = self._initialize_crop_database()
        self.rotation_rules = self._initialize_rotation_rules()
        
    def _initialize_crop_database(self) -> Dict[str, CropInfo]:
        """Initialize comprehensive crop database for Indian agriculture."""
        return {
            'rice': CropInfo(
                name='rice',
                nutrient_demand={'N': 120, 'P': 60, 'K': 40},
                nutrient_contribution={'N': 0, 'P': 10, 'K': 20},
                soil_type_preference=['clay', 'loamy'],
                season='Kharif',
                water_requirement=1200,
                profit_per_hectare=45000,
                market_volatility=0.3,
                pest_susceptibility={'stem_borer': 0.7, 'brown_planthopper': 0.6},
                disease_resistance=0.6,
                growth_period=120
            ),
            'wheat': CropInfo(
                name='wheat',
                nutrient_demand={'N': 100, 'P': 50, 'K': 30},
                nutrient_contribution={'N': 0, 'P': 5, 'K': 15},
                soil_type_preference=['loamy', 'clay'],
                season='Rabi',
                water_requirement=450,
                profit_per_hectare=38000,
                market_volatility=0.25,
                pest_susceptibility={'aphid': 0.5, 'rust': 0.4},
                disease_resistance=0.7,
                growth_period=110
            ),
            'maize': CropInfo(
                name='maize',
                nutrient_demand={'N': 80, 'P': 40, 'K': 35},
                nutrient_contribution={'N': 0, 'P': 8, 'K': 12},
                soil_type_preference=['loamy', 'sandy'],
                season='Kharif',
                water_requirement=600,
                profit_per_hectare=42000,
                market_volatility=0.4,
                pest_susceptibility={'fall_armyworm': 0.8, 'stem_borer': 0.5},
                disease_resistance=0.65,
                growth_period=90
            ),
            'chickpea': CropInfo(
                name='chickpea',
                nutrient_demand={'N': 30, 'P': 60, 'K': 40},
                nutrient_contribution={'N': 80, 'P': 15, 'K': 10},  # Nitrogen fixing
                soil_type_preference=['loamy', 'sandy'],
                season='Rabi',
                water_requirement=300,
                profit_per_hectare=35000,
                market_volatility=0.35,
                pest_susceptibility={'pod_borer': 0.6, 'aphid': 0.4},
                disease_resistance=0.8,
                growth_period=100
            ),
            'cotton': CropInfo(
                name='cotton',
                nutrient_demand={'N': 150, 'P': 75, 'K': 60},
                nutrient_contribution={'N': 0, 'P': 5, 'K': 25},
                soil_type_preference=['clay', 'loamy'],
                season='Kharif',
                water_requirement=800,
                profit_per_hectare=55000,
                market_volatility=0.5,
                pest_susceptibility={'bollworm': 0.9, 'whitefly': 0.7},
                disease_resistance=0.5,
                growth_period=180
            ),
            'sugarcane': CropInfo(
                name='sugarcane',
                nutrient_demand={'N': 200, 'P': 100, 'K': 150},
                nutrient_contribution={'N': 0, 'P': 20, 'K': 40},
                soil_type_preference=['loamy', 'clay'],
                season='Kharif',
                water_requirement=2000,
                profit_per_hectare=80000,
                market_volatility=0.2,
                pest_susceptibility={'shoot_borer': 0.6, 'scale_insect': 0.5},
                disease_resistance=0.7,
                growth_period=365
            ),
            'soybean': CropInfo(
                name='soybean',
                nutrient_demand={'N': 20, 'P': 60, 'K': 70},
                nutrient_contribution={'N': 100, 'P': 20, 'K': 15},  # Nitrogen fixing
                soil_type_preference=['loamy', 'sandy'],
                season='Kharif',
                water_requirement=500,
                profit_per_hectare=40000,
                market_volatility=0.45,
                pest_susceptibility={'pod_borer': 0.7, 'aphid': 0.5},
                disease_resistance=0.75,
                growth_period=95
            ),
            'mustard': CropInfo(
                name='mustard',
                nutrient_demand={'N': 60, 'P': 30, 'K': 20},
                nutrient_contribution={'N': 0, 'P': 8, 'K': 5},
                soil_type_preference=['loamy', 'sandy'],
                season='Rabi',
                water_requirement=250,
                profit_per_hectare=32000,
                market_volatility=0.4,
                pest_susceptibility={'aphid': 0.8, 'flea_beetle': 0.6},
                disease_resistance=0.7,
                growth_period=120
            )
        }
    
    def _initialize_rotation_rules(self) -> Dict[str, Any]:
        """Initialize crop rotation rules and constraints."""
        return {
            'avoid_same_family': {
                'cereals': ['rice', 'wheat', 'maize'],
                'legumes': ['chickpea', 'soybean'],
                'cash_crops': ['cotton', 'sugarcane'],
                'oilseeds': ['mustard']
            },
            'beneficial_sequences': [
                ('legumes', 'cereals'),  # Nitrogen fixation benefit
                ('cereals', 'cash_crops'),  # Soil structure improvement
                ('cash_crops', 'oilseeds')  # Pest break cycle
            ],
            'minimum_gap_years': {
                'rice': 1,
                'wheat': 1,
                'cotton': 2,
                'sugarcane': 3
            },
            'soil_improvement_crops': ['chickpea', 'soybean'],  # Legumes
            'pest_break_crops': ['mustard', 'chickpea']  # Break pest cycles
        }
    
    def optimize_rotation(self, 
                         farm_conditions: Dict[str, Any],
                         preferences: Dict[str, Any] = None) -> RotationPlan:
        """
        Optimize 3-year crop rotation plan.
        
        Args:
            farm_conditions: Soil type, climate, water availability, etc.
            preferences: Farmer preferences for risk, profit focus, etc.
            
        Returns:
            RotationPlan with optimized 3-year sequence
        """
        if preferences is None:
            preferences = {
                'profit_weight': 0.4,
                'sustainability_weight': 0.3,
                'risk_weight': 0.3
            }
        
        # Filter suitable crops based on farm conditions
        suitable_crops = self._filter_suitable_crops(farm_conditions)
        
        # Generate and evaluate rotation combinations
        best_rotation = self._evaluate_rotations(suitable_crops, farm_conditions, preferences)
        
        # Create detailed rotation plan
        rotation_plan = self._create_rotation_plan(best_rotation, farm_conditions)
        
        return rotation_plan
    
    def _filter_suitable_crops(self, farm_conditions: Dict[str, Any]) -> List[str]:
        """Filter crops suitable for given farm conditions."""
        suitable = []
        soil_type = farm_conditions.get('soil_type', 'loamy')
        water_availability = farm_conditions.get('water_availability', 'medium')
        
        for crop_name, crop_info in self.crop_database.items():
            # Check soil type compatibility
            if soil_type in crop_info.soil_type_preference:
                # Check water requirement compatibility
                water_multiplier = {'low': 0.7, 'medium': 1.0, 'high': 1.3}
                available_water = water_multiplier.get(water_availability, 1.0) * 800
                
                if crop_info.water_requirement <= available_water:
                    suitable.append(crop_name)
        
        return suitable
    
    def _evaluate_rotations(self, 
                          suitable_crops: List[str],
                          farm_conditions: Dict[str, Any],
                          preferences: Dict[str, Any]) -> List[str]:
        """Evaluate different rotation combinations and select the best."""
        from itertools import permutations
        
        # Generate 3-year rotation combinations
        best_score = -1
        best_rotation = []
        
        # Consider different crop combinations for 3 years
        for rotation in permutations(suitable_crops, min(3, len(suitable_crops))):
            if self._is_valid_rotation(rotation):
                score = self._calculate_rotation_score(rotation, farm_conditions, preferences)
                if score > best_score:
                    best_score = score
                    best_rotation = list(rotation)
        
        # If no 3-crop rotation, try 2-crop alternating
        if not best_rotation and len(suitable_crops) >= 2:
            for i, crop1 in enumerate(suitable_crops):
                for crop2 in suitable_crops[i+1:]:
                    rotation = [crop1, crop2, crop1]
                    if self._is_valid_rotation(rotation):
                        score = self._calculate_rotation_score(rotation, farm_conditions, preferences)
                        if score > best_score:
                            best_score = score
                            best_rotation = rotation
        
        return best_rotation if best_rotation else suitable_crops[:3]
    
    def _is_valid_rotation(self, rotation: List[str]) -> bool:
        """Check if rotation follows agronomic rules."""
        rules = self.rotation_rules
        
        # Check minimum gap requirements
        for i, crop in enumerate(rotation):
            min_gap = rules['minimum_gap_years'].get(crop, 0)
            if min_gap > 0:
                # Check if same crop appears too soon
                for j in range(i + 1, min(i + 1 + min_gap, len(rotation))):
                    if j < len(rotation) and rotation[j] == crop:
                        return False
        
        # Check family diversity
        families = rules['avoid_same_family']
        for family, crops in families.items():
            family_count = sum(1 for crop in rotation if crop in crops)
            if family_count > 2:  # Max 2 from same family in 3 years
                return False
        
        return True
    
    def _calculate_rotation_score(self, 
                                rotation: List[str],
                                farm_conditions: Dict[str, Any],
                                preferences: Dict[str, Any]) -> float:
        """Calculate overall score for a rotation plan."""
        
        # Economic score
        total_profit = sum(self.crop_database[crop].profit_per_hectare for crop in rotation)
        avg_volatility = np.mean([self.crop_database[crop].market_volatility for crop in rotation])
        economic_score = total_profit / 150000 * (1 - avg_volatility)  # Normalize to 0-1
        
        # Sustainability score
        sustainability_score = self._calculate_sustainability_score(rotation)
        
        # Risk score
        risk_score = self._calculate_risk_score(rotation, farm_conditions)
        
        # Weighted total score
        total_score = (
            preferences['profit_weight'] * economic_score +
            preferences['sustainability_weight'] * sustainability_score +
            preferences['risk_weight'] * (1 - risk_score)  # Lower risk is better
        )
        
        return total_score
    
    def _calculate_sustainability_score(self, rotation: List[str]) -> float:
        """Calculate sustainability score based on soil health and nutrient balance."""
        
        # Nutrient balance calculation
        total_demand = {'N': 0, 'P': 0, 'K': 0}
        total_contribution = {'N': 0, 'P': 0, 'K': 0}
        
        for crop in rotation:
            crop_info = self.crop_database[crop]
            for nutrient in ['N', 'P', 'K']:
                total_demand[nutrient] += crop_info.nutrient_demand[nutrient]
                total_contribution[nutrient] += crop_info.nutrient_contribution[nutrient]
        
        # Calculate nutrient balance (contribution/demand ratio)
        nutrient_balance = np.mean([
            min(total_contribution[n] / max(total_demand[n], 1), 1.0)
            for n in ['N', 'P', 'K']
        ])
        
        # Diversity bonus
        diversity_score = len(set(rotation)) / 3.0
        
        # Soil improvement bonus
        soil_improvement_crops = sum(1 for crop in rotation 
                                   if crop in self.rotation_rules['soil_improvement_crops'])
        soil_improvement_score = min(soil_improvement_crops / 3.0, 1.0)
        
        return 0.4 * nutrient_balance + 0.3 * diversity_score + 0.3 * soil_improvement_score
    
    def _calculate_risk_score(self, rotation: List[str], farm_conditions: Dict[str, Any]) -> float:
        """Calculate risk score based on pest pressure, disease susceptibility, and climate."""
        
        # Pest and disease risk
        avg_disease_resistance = np.mean([
            self.crop_database[crop].disease_resistance for crop in rotation
        ])
        
        # Market volatility risk
        avg_volatility = np.mean([
            self.crop_database[crop].market_volatility for crop in rotation
        ])
        
        # Climate risk (simplified)
        climate_risk = farm_conditions.get('climate_risk', 0.3)
        
        # Combine risks (lower is better)
        risk_score = 0.4 * (1 - avg_disease_resistance) + 0.3 * avg_volatility + 0.3 * climate_risk
        
        return min(risk_score, 1.0)
    
    def _create_rotation_plan(self, rotation: List[str], farm_conditions: Dict[str, Any]) -> RotationPlan:
        """Create detailed rotation plan with year-by-year breakdown."""
        
        years = []
        cumulative_profit = 0
        
        for year, crop in enumerate(rotation, 1):
            crop_info = self.crop_database[crop]
            
            year_plan = {
                'year': year,
                'crop': crop,
                'season': crop_info.season,
                'expected_profit': crop_info.profit_per_hectare,
                'water_requirement': crop_info.water_requirement,
                'nutrient_needs': crop_info.nutrient_demand,
                'nutrient_contribution': crop_info.nutrient_contribution,
                'growth_period': crop_info.growth_period,
                'market_volatility': crop_info.market_volatility,
                'recommendations': self._generate_year_recommendations(crop, year, farm_conditions)
            }
            
            years.append(year_plan)
            cumulative_profit += crop_info.profit_per_hectare
        
        # Calculate overall metrics
        soil_health_score = self._calculate_sustainability_score(rotation)
        sustainability_index = soil_health_score
        risk_assessment = {
            'market_risk': np.mean([self.crop_database[crop].market_volatility for crop in rotation]),
            'climate_risk': farm_conditions.get('climate_risk', 0.3),
            'pest_disease_risk': 1 - np.mean([self.crop_database[crop].disease_resistance for crop in rotation])
        }
        
        # Generate overall recommendations
        recommendations = self._generate_overall_recommendations(rotation, farm_conditions)
        
        return RotationPlan(
            years=years,
            total_profit=cumulative_profit,
            soil_health_score=soil_health_score,
            sustainability_index=sustainability_index,
            risk_assessment=risk_assessment,
            recommendations=recommendations
        )
    
    def _generate_year_recommendations(self, crop: str, year: int, farm_conditions: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations for each year."""
        recommendations = []
        crop_info = self.crop_database[crop]
        
        # Nutrient management
        if crop_info.nutrient_demand['N'] > 100:
            recommendations.append(f"Apply nitrogen in 2-3 splits for {crop}")
        
        # Water management
        if crop_info.water_requirement > 800:
            recommendations.append(f"Install drip irrigation for water-intensive {crop}")
        
        # Pest management
        if crop == 'cotton':
            recommendations.append("Monitor for bollworm and whitefly; use IPM practices")
        elif crop == 'rice':
            recommendations.append("Monitor water levels to prevent stem borer infestation")
        
        # Soil health
        if year > 1:
            recommendations.append("Apply compost or organic matter before sowing")
        
        return recommendations
    
    def _generate_overall_recommendations(self, rotation: List[str], farm_conditions: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations for the rotation plan."""
        recommendations = [
            f"Follow {' → '.join(rotation)} rotation for optimal soil health",
            "Maintain soil organic matter above 2% through compost application",
            "Test soil nutrients annually and adjust fertilizer accordingly"
        ]
        
        # Add legume benefits
        legumes = [crop for crop in rotation if crop in self.rotation_rules['soil_improvement_crops']]
        if legumes:
            recommendations.append(f"Legume crops ({', '.join(legumes)}) will improve soil nitrogen")
        
        # Add water management
        high_water_crops = [crop for crop in rotation if self.crop_database[crop].water_requirement > 800]
        if high_water_crops:
            recommendations.append(f"Plan water storage for high-requirement crops: {', '.join(high_water_crops)}")
        
        return recommendations

class EconomicIntelligence:
    """Economic intelligence engine for profit optimization and market analysis."""
    
    def __init__(self):
        self.market_data = self._initialize_market_data()
        self.cost_data = self._initialize_cost_data()
    
    def _initialize_market_data(self) -> Dict[str, Any]:
        """Initialize market price trends and predictions."""
        return {
            'rice': {
                'current_price': 2500,  # INR per quintal
                'seasonal_variation': 0.15,
                'trend': 'stable',
                'demand_forecast': 'high'
            },
            'wheat': {
                'current_price': 2200,
                'seasonal_variation': 0.12,
                'trend': 'increasing',
                'demand_forecast': 'stable'
            },
            'maize': {
                'current_price': 1800,
                'seasonal_variation': 0.20,
                'trend': 'volatile',
                'demand_forecast': 'increasing'
            },
            'cotton': {
                'current_price': 6000,
                'seasonal_variation': 0.25,
                'trend': 'increasing',
                'demand_forecast': 'high'
            }
        }
    
    def _initialize_cost_data(self) -> Dict[str, Any]:
        """Initialize production cost data."""
        return {
            'rice': {'seed': 3000, 'fertilizer': 8000, 'pesticide': 4000, 'labor': 15000, 'other': 5000},
            'wheat': {'seed': 2500, 'fertilizer': 6000, 'pesticide': 3000, 'labor': 12000, 'other': 4000},
            'maize': {'seed': 2000, 'fertilizer': 5000, 'pesticide': 3500, 'labor': 10000, 'other': 3500},
            'cotton': {'seed': 4000, 'fertilizer': 12000, 'pesticide': 8000, 'labor': 20000, 'other': 8000}
        }
    
    def calculate_profit_projection(self, rotation_plan: RotationPlan) -> Dict[str, Any]:
        """Calculate detailed profit projections for rotation plan."""
        projections = []
        total_profit = 0
        total_cost = 0
        
        for year_plan in rotation_plan.years:
            crop = year_plan['crop']
            
            # Calculate costs
            costs = self.cost_data.get(crop, {})
            year_cost = sum(costs.values())
            
            # Calculate revenue with market variations
            market_info = self.market_data.get(crop, {})
            base_price = market_info.get('current_price', 2000)
            seasonal_var = market_info.get('seasonal_variation', 0.15)
            
            # Simulate price variations
            price_range = {
                'min': base_price * (1 - seasonal_var),
                'expected': base_price,
                'max': base_price * (1 + seasonal_var)
            }
            
            # Assume 40 quintals per hectare average yield
            yield_per_hectare = 40
            revenue_range = {
                'min': price_range['min'] * yield_per_hectare,
                'expected': price_range['expected'] * yield_per_hectare,
                'max': price_range['max'] * yield_per_hectare
            }
            
            profit_range = {
                'min': revenue_range['min'] - year_cost,
                'expected': revenue_range['expected'] - year_cost,
                'max': revenue_range['max'] - year_cost
            }
            
            year_projection = {
                'year': year_plan['year'],
                'crop': crop,
                'costs': costs,
                'total_cost': year_cost,
                'price_range': price_range,
                'revenue_range': revenue_range,
                'profit_range': profit_range,
                'roi': profit_range['expected'] / year_cost if year_cost > 0 else 0
            }
            
            projections.append(year_projection)
            total_profit += profit_range['expected']
            total_cost += year_cost
        
        return {
            'yearly_projections': projections,
            'total_profit_3year': total_profit,
            'total_cost_3year': total_cost,
            'average_roi': total_profit / total_cost if total_cost > 0 else 0,
            'risk_analysis': self._analyze_economic_risk(projections)
        }
    
    def _analyze_economic_risk(self, projections: List[Dict]) -> Dict[str, Any]:
        """Analyze economic risks in the rotation plan."""
        profit_volatility = np.std([p['profit_range']['expected'] for p in projections])
        avg_profit = np.mean([p['profit_range']['expected'] for p in projections])
        
        risk_score = profit_volatility / avg_profit if avg_profit > 0 else 1.0
        
        return {
            'volatility_score': min(risk_score, 1.0),
            'risk_level': 'High' if risk_score > 0.3 else 'Medium' if risk_score > 0.15 else 'Low',
            'diversification_benefit': len(set(p['crop'] for p in projections)) / 3.0,
            'recommendations': [
                "Consider crop insurance for high-value crops",
                "Monitor market prices for optimal selling timing",
                "Maintain emergency fund for input cost fluctuations"
            ]
        }

class ClimateAdaptationSystem:
    """Climate adaptation algorithms for weather resilience and risk mitigation."""
    
    def __init__(self):
        self.climate_data = self._initialize_climate_data()
        self.adaptation_strategies = self._initialize_adaptation_strategies()
    
    def _initialize_climate_data(self) -> Dict[str, Any]:
        """Initialize climate patterns and risk data."""
        return {
            'jharkhand': {
                'annual_rainfall': 1400,  # mm
                'rainfall_variability': 0.25,
                'temperature_trend': 'increasing',
                'extreme_events': ['drought', 'flood', 'heatwave'],
                'monsoon_reliability': 0.75
            }
        }
    
    def _initialize_adaptation_strategies(self) -> Dict[str, List[str]]:
        """Initialize climate adaptation strategies."""
        return {
            'drought': [
                "Select drought-tolerant crop varieties",
                "Implement water harvesting systems",
                "Use mulching to conserve soil moisture",
                "Adjust sowing dates based on rainfall forecast"
            ],
            'flood': [
                "Choose flood-tolerant varieties",
                "Improve field drainage systems",
                "Practice raised bed cultivation",
                "Plan for quick-draining alternative crops"
            ],
            'heatwave': [
                "Select heat-tolerant varieties",
                "Provide shade nets for sensitive crops",
                "Adjust irrigation timing to early morning/evening",
                "Use reflective mulches to reduce soil temperature"
            ],
            'irregular_monsoon': [
                "Diversify crop portfolio",
                "Invest in irrigation infrastructure",
                "Use weather-based crop insurance",
                "Adopt climate-smart farming practices"
            ]
        }
    
    def assess_climate_risk(self, farm_location: str, rotation_plan: RotationPlan) -> Dict[str, Any]:
        """Assess climate risks and provide adaptation recommendations."""
        
        climate_info = self.climate_data.get(farm_location.lower(), self.climate_data['jharkhand'])
        
        # Assess risks for each crop in rotation
        crop_risks = []
        for year_plan in rotation_plan.years:
            crop = year_plan['crop']
            
            # Water stress risk
            water_req = year_plan['water_requirement']
            rainfall = climate_info['annual_rainfall']
            water_stress_risk = max(0, (water_req - rainfall) / water_req)
            
            # Heat stress risk (simplified)
            heat_stress_risk = 0.3 if climate_info['temperature_trend'] == 'increasing' else 0.1
            
            # Extreme event risk
            extreme_risk = 0.4 if len(climate_info['extreme_events']) > 2 else 0.2
            
            overall_risk = (water_stress_risk + heat_stress_risk + extreme_risk) / 3
            
            crop_risk = {
                'year': year_plan['year'],
                'crop': crop,
                'water_stress_risk': water_stress_risk,
                'heat_stress_risk': heat_stress_risk,
                'extreme_event_risk': extreme_risk,
                'overall_risk': overall_risk,
                'risk_level': 'High' if overall_risk > 0.6 else 'Medium' if overall_risk > 0.3 else 'Low'
            }
            
            crop_risks.append(crop_risk)
        
        # Generate adaptation recommendations
        adaptations = self._generate_adaptation_plan(crop_risks, climate_info)
        
        return {
            'climate_assessment': climate_info,
            'crop_risks': crop_risks,
            'overall_risk_score': np.mean([cr['overall_risk'] for cr in crop_risks]),
            'adaptation_plan': adaptations,
            'emergency_protocols': self._create_emergency_protocols(climate_info)
        }
    
    def _generate_adaptation_plan(self, crop_risks: List[Dict], climate_info: Dict) -> Dict[str, List[str]]:
        """Generate comprehensive adaptation plan."""
        adaptation_plan = {
            'immediate_actions': [],
            'infrastructure_investments': [],
            'crop_management': [],
            'risk_mitigation': []
        }
        
        # Analyze dominant risks
        high_risk_crops = [cr for cr in crop_risks if cr['overall_risk'] > 0.6]
        
        if high_risk_crops:
            adaptation_plan['immediate_actions'].extend([
                "Review crop selection for high-risk years",
                "Implement early warning systems for weather monitoring",
                "Prepare contingency crop plans"
            ])
        
        # Infrastructure based on climate patterns
        if climate_info['rainfall_variability'] > 0.2:
            adaptation_plan['infrastructure_investments'].extend([
                "Install rainwater harvesting systems",
                "Develop farm ponds for water storage",
                "Upgrade irrigation infrastructure"
            ])
        
        # Crop management adaptations
        adaptation_plan['crop_management'].extend([
            "Select climate-resilient varieties",
            "Adjust sowing windows based on weather forecasts",
            "Implement integrated pest management for changing pest patterns"
        ])
        
        # Risk mitigation strategies
        adaptation_plan['risk_mitigation'].extend([
            "Diversify income sources beyond agriculture",
            "Participate in crop insurance schemes",
            "Form farmer producer organizations for collective risk management"
        ])
        
        return adaptation_plan
    
    def _create_emergency_protocols(self, climate_info: Dict) -> Dict[str, List[str]]:
        """Create emergency response protocols for extreme events."""
        protocols = {}
        
        for event in climate_info.get('extreme_events', []):
            protocols[event] = self.adaptation_strategies.get(event, [
                f"Monitor weather alerts for {event}",
                f"Implement emergency response plan for {event}",
                f"Contact agricultural extension services for {event} management"
            ])
        
        return protocols

# Main Smart Advisory Service
class SmartAdvisoryService:
    """Comprehensive smart advisory service integrating all components."""
    
    def __init__(self):
        self.rotation_optimizer = CropRotationOptimizer()
        self.economic_intelligence = EconomicIntelligence()
        self.climate_adaptation = ClimateAdaptationSystem()
    
    def generate_comprehensive_advisory(self, 
                                      farm_conditions: Dict[str, Any],
                                      preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive advisory covering all aspects."""
        
        # Generate optimal rotation plan
        rotation_plan = self.rotation_optimizer.optimize_rotation(farm_conditions, preferences)
        
        # Calculate economic projections
        economic_analysis = self.economic_intelligence.calculate_profit_projection(rotation_plan)
        
        # Assess climate risks and adaptations
        farm_location = farm_conditions.get('location', 'jharkhand')
        climate_analysis = self.climate_adaptation.assess_climate_risk(farm_location, rotation_plan)
        
        # Generate integrated recommendations
        integrated_recommendations = self._generate_integrated_recommendations(
            rotation_plan, economic_analysis, climate_analysis
        )
        
        return {
            'rotation_plan': rotation_plan,
            'economic_analysis': economic_analysis,
            'climate_analysis': climate_analysis,
            'integrated_recommendations': integrated_recommendations,
            'advisory_summary': self._create_advisory_summary(
                rotation_plan, economic_analysis, climate_analysis
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_integrated_recommendations(self, 
                                           rotation_plan: RotationPlan,
                                           economic_analysis: Dict,
                                           climate_analysis: Dict) -> List[str]:
        """Generate integrated recommendations across all domains."""
        recommendations = []
        
        # High-level strategy
        recommendations.append(
            f"Implement {' → '.join([year['crop'] for year in rotation_plan.years])} "
            f"rotation for optimal balance of profit (₹{rotation_plan.total_profit:,.0f} over 3 years) "
            f"and sustainability (score: {rotation_plan.soil_health_score:.2f})"
        )
        
        # Economic priorities
        avg_roi = economic_analysis['average_roi']
        if avg_roi > 0.5:
            recommendations.append("Excellent ROI potential - consider expanding cultivation area")
        elif avg_roi > 0.3:
            recommendations.append("Good profit margins - focus on cost optimization")
        else:
            recommendations.append("Monitor input costs closely and explore value addition")
        
        # Climate adaptation
        overall_climate_risk = climate_analysis['overall_risk_score']
        if overall_climate_risk > 0.6:
            recommendations.append("High climate risk detected - prioritize adaptation strategies")
        elif overall_climate_risk > 0.3:
            recommendations.append("Moderate climate risk - implement preventive measures")
        
        # Soil health focus
        if rotation_plan.soil_health_score > 0.7:
            recommendations.append("Excellent soil health trajectory - maintain current practices")
        else:
            recommendations.append("Focus on soil health improvement through organic matter addition")
        
        return recommendations
    
    def _create_advisory_summary(self, 
                               rotation_plan: RotationPlan,
                               economic_analysis: Dict,
                               climate_analysis: Dict) -> Dict[str, Any]:
        """Create executive summary of the advisory."""
        return {
            'plan_overview': f"3-year rotation: {' → '.join([year['crop'] for year in rotation_plan.years])}",
            'profit_potential': f"₹{rotation_plan.total_profit:,.0f} total, ₹{rotation_plan.total_profit/3:,.0f} annually",
            'sustainability_score': f"{rotation_plan.soil_health_score:.1%}",
            'risk_level': climate_analysis['crop_risks'][0]['risk_level'] if climate_analysis['crop_risks'] else 'Low',
            'key_benefits': [
                f"Soil health improvement: {rotation_plan.soil_health_score:.1%}",
                f"Average ROI: {economic_analysis['average_roi']:.1%}",
                f"Climate adaptation score: {1-climate_analysis['overall_risk_score']:.1%}"
            ],
            'priority_actions': rotation_plan.recommendations[:3]
        }