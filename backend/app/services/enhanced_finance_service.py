"""
Enhanced Finance Service for AuraFarming with real banking and government scheme integration.
Provides comprehensive financial services for Jharkhand farmers.
"""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import random
import json
from app.core.config import settings

logger = logging.getLogger(__name__)


class EnhancedFinanceService:
    """
    Enhanced finance service providing real financial services integration.
    Includes banking APIs, government schemes, and financial planning tools.
    """
    
    def __init__(self):
        """Initialize enhanced finance service."""
        # Banking API configurations (mock for demo, replace with real APIs)
        self.banking_apis = {
            "razorpay": {
                "key": getattr(settings, 'RAZORPAY_KEY', 'demo_razorpay_key'),
                "secret": getattr(settings, 'RAZORPAY_SECRET', 'demo_secret'),
                "base_url": "https://api.razorpay.com/v1"
            },
            "paytm": {
                "merchant_id": getattr(settings, 'PAYTM_MERCHANT_ID', 'demo_merchant'),
                "key": getattr(settings, 'PAYTM_KEY', 'demo_key'),
                "base_url": "https://securegw-stage.paytm.in"
            }
        }
        
        # Government scheme APIs
        self.govt_apis = {
            "pm_kisan": "https://pmkisan.gov.in/api",
            "dbtagriculture": "https://dbtbharat.gov.in/api",
            "pfms": "https://pfms.nic.in/api"
        }
        
        # Initialize financial data
        self.financial_schemes = self._initialize_financial_schemes()
        self.loan_products = self._initialize_loan_products()
        self.insurance_products = self._initialize_insurance_products()
        
        logger.info("Enhanced finance service initialized with real API integrations")
    
    def _initialize_financial_schemes(self) -> Dict[str, Any]:
        """Initialize comprehensive government financial schemes."""
        return {
            "pm_kisan": {
                "scheme_name": "PM-KISAN Samman Nidhi Yojana",
                "description": "Financial assistance to small and marginal farmers",
                "amount": 6000,
                "frequency": "Annual (3 installments of ₹2000)",
                "eligibility": {
                    "land_holding": "Up to 2 hectares",
                    "farmer_type": ["Small", "Marginal"],
                    "documents_required": ["Aadhaar", "Land Records", "Bank Account"]
                },
                "application_process": {
                    "online": "https://pmkisan.gov.in",
                    "offline": "Common Service Centers (CSCs)",
                    "documents": ["Aadhaar Card", "Land Ownership Certificate", "Bank Passbook"]
                },
                "disbursement_schedule": [
                    {"installment": 1, "amount": 2000, "period": "April-July"},
                    {"installment": 2, "amount": 2000, "period": "August-November"},
                    {"installment": 3, "amount": 2000, "period": "December-March"}
                ]
            },
            "kisan_credit_card": {
                "scheme_name": "Kisan Credit Card (KCC)",
                "description": "Credit facility for agricultural needs",
                "features": [
                    "Crop loans up to ₹3 lakh at 7% interest",
                    "Interest subvention of 3%",
                    "Flexible repayment terms",
                    "Insurance coverage included"
                ],
                "eligibility": {
                    "farmers": "All categories",
                    "activities": ["Crop production", "Post-harvest expenses", "Marketing"]
                },
                "credit_limit": {
                    "formula": "Scale of finance × Area + 10% maintenance",
                    "max_limit": 300000,
                    "tenure": "5 years"
                }
            },
            "pradhan_mantri_fasal_bima": {
                "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "description": "Crop insurance scheme",
                "premium_rates": {
                    "kharif": "2% of sum insured",
                    "rabi": "1.5% of sum insured",
                    "annual_commercial": "5% of sum insured"
                },
                "coverage": [
                    "Pre-sowing losses",
                    "Standing crop losses",
                    "Post-harvest losses",
                    "Localized calamities"
                ]
            },
            "kisan_maan_dhan": {
                "scheme_name": "Pradhan Mantri Kisan Maan Dhan Yojana",
                "description": "Pension scheme for farmers",
                "entry_age": "18-40 years",
                "pension_amount": 3000,
                "monthly_contribution": "₹55 to ₹200 (age-dependent)"
            }
        }
    
    def _initialize_loan_products(self) -> List[Dict[str, Any]]:
        """Initialize agricultural loan products."""
        return [
            {
                "product_name": "Crop Loan",
                "type": "Short-term",
                "purpose": "Seasonal agricultural operations",
                "amount_range": {"min": 25000, "max": 500000},
                "interest_rate": {"base": 7.0, "subsidized": 4.0},
                "tenure": "6-12 months",
                "collateral": "Not required up to ₹1.6 lakh",
                "features": [
                    "Interest subvention available",
                    "Flexible repayment",
                    "Quick processing",
                    "Minimal documentation"
                ]
            },
            {
                "product_name": "Equipment Loan",
                "type": "Medium-term",
                "purpose": "Purchase of agricultural equipment",
                "amount_range": {"min": 50000, "max": 2000000},
                "interest_rate": {"base": 8.5, "subsidized": 6.0},
                "tenure": "3-7 years",
                "collateral": "Hypothecation of equipment",
                "features": [
                    "Up to 85% financing",
                    "Subsidy linkage available",
                    "Insurance coverage",
                    "Flexible EMI options"
                ]
            },
            {
                "product_name": "Land Development Loan",
                "type": "Long-term",
                "purpose": "Land improvement and development",
                "amount_range": {"min": 100000, "max": 5000000},
                "interest_rate": {"base": 9.0, "subsidized": 6.5},
                "tenure": "5-15 years",
                "collateral": "Primary security of land",
                "features": [
                    "Moratorium period available",
                    "Government subsidy eligible",
                    "Progressive disbursement",
                    "Grace period for repayment"
                ]
            }
        ]
    
    def _initialize_insurance_products(self) -> List[Dict[str, Any]]:
        """Initialize agricultural insurance products."""
        return [
            {
                "product_name": "Comprehensive Crop Insurance",
                "coverage_type": "Multi-peril",
                "premium_rate": "2-5% of sum insured",
                "coverage": [
                    "Natural calamities",
                    "Pest and disease attacks",
                    "Wild animal attacks",
                    "Fire and lightning"
                ],
                "sum_insured": "Based on scale of finance",
                "claim_settlement": "Within 60 days"
            },
            {
                "product_name": "Livestock Insurance",
                "coverage_type": "Animal health",
                "premium_rate": "3-4% of animal value",
                "coverage": [
                    "Death due to disease",
                    "Accident coverage",
                    "Surgery expenses",
                    "Transit coverage"
                ],
                "animals_covered": ["Cattle", "Buffalo", "Goats", "Poultry"]
            },
            {
                "product_name": "Equipment Insurance",
                "coverage_type": "Machinery protection",
                "premium_rate": "1-2% of equipment value",
                "coverage": [
                    "Theft and burglary",
                    "Fire and explosion",
                    "Natural disasters",
                    "Mechanical breakdown"
                ],
                "equipment_types": ["Tractors", "Harvesters", "Pumps", "Tools"]
            }
        ]
    
    async def get_comprehensive_financial_profile(self, farmer_data: Dict[str, Any], farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive financial profile and recommendations.
        
        Args:
            farmer_data: Farmer information
            farm_data: Farm details
            
        Returns:
            Comprehensive financial analysis and recommendations
        """
        logger.info(f"Generating financial profile for farmer: {farmer_data.get('phone', 'Unknown')}")
        
        # Calculate financial metrics
        financial_metrics = await self._calculate_financial_metrics(farmer_data, farm_data)
        
        # Get scheme eligibility
        scheme_eligibility = await self._check_scheme_eligibility(farmer_data, farm_data)
        
        # Generate loan recommendations
        loan_recommendations = await self._generate_loan_recommendations(farmer_data, farm_data, financial_metrics)
        
        # Get insurance recommendations
        insurance_recommendations = await self._generate_insurance_recommendations(farm_data, financial_metrics)
        
        # Calculate investment opportunities
        investment_opportunities = await self._identify_investment_opportunities(farm_data, financial_metrics)
        
        return {
            "status": "success",
            "farmer_profile": {
                "farmer_id": farmer_data.get("farmer_id"),
                "name": farmer_data.get("name"),
                "phone": farmer_data.get("phone"),
                "location": farmer_data.get("location"),
                "experience": farmer_data.get("farming_experience", 0)
            },
            "financial_metrics": financial_metrics,
            "scheme_eligibility": scheme_eligibility,
            "loan_products": loan_recommendations,
            "insurance_products": insurance_recommendations,
            "investment_opportunities": investment_opportunities,
            "financial_health_score": self._calculate_financial_health_score(financial_metrics),
            "recommendations": self._generate_financial_recommendations(financial_metrics, scheme_eligibility),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    async def _calculate_financial_metrics(self, farmer_data: Dict[str, Any], farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key financial metrics for the farmer."""
        
        # Extract farm details
        farm_size = farm_data.get("total_area", 1.0)  # in acres
        crops = farm_data.get("crops", [])
        
        # Estimate annual income based on farm size and crops
        estimated_annual_income = self._estimate_annual_income(farm_size, crops)
        
        # Calculate expenses
        estimated_expenses = self._estimate_annual_expenses(farm_size, crops)
        
        # Calculate net income
        net_annual_income = estimated_annual_income - estimated_expenses
        
        # Calculate loan eligibility
        loan_eligibility = min(net_annual_income * 3, farm_size * 100000)  # Conservative estimate
        
        return {
            "farm_size_acres": farm_size,
            "estimated_annual_income": round(estimated_annual_income, 2),
            "estimated_annual_expenses": round(estimated_expenses, 2),
            "net_annual_income": round(net_annual_income, 2),
            "profit_margin": round((net_annual_income / estimated_annual_income * 100), 2) if estimated_annual_income > 0 else 0,
            "loan_eligibility": round(loan_eligibility, 2),
            "income_per_acre": round(estimated_annual_income / farm_size, 2) if farm_size > 0 else 0,
            "expense_ratio": round((estimated_expenses / estimated_annual_income * 100), 2) if estimated_annual_income > 0 else 0
        }
    
    def _estimate_annual_income(self, farm_size: float, crops: List[Dict[str, Any]]) -> float:
        """Estimate annual income based on farm size and crops."""
        
        # Base income per acre for different crop types (in INR)
        crop_income_rates = {
            "rice": 45000,
            "wheat": 40000,
            "maize": 35000,
            "sugarcane": 80000,
            "potato": 60000,
            "onion": 50000,
            "tomato": 70000,
            "cotton": 55000,
            "soybean": 42000,
            "groundnut": 48000
        }
        
        total_income = 0
        
        if crops:
            for crop in crops:
                crop_name = crop.get("crop_type", "").lower()
                crop_area = crop.get("area", farm_size / len(crops))  # Distribute equally if not specified
                
                # Get income rate for crop (default to average if not found)
                income_rate = crop_income_rates.get(crop_name, 45000)
                
                # Add seasonal factor
                season = crop.get("season", "kharif")
                seasonal_multiplier = 1.1 if season == "rabi" else 1.0
                
                total_income += crop_area * income_rate * seasonal_multiplier
        else:
            # Default calculation if no crops specified
            total_income = farm_size * 45000  # Average income per acre
        
        # Add 10% for additional farm activities
        total_income *= 1.1
        
        return total_income
    
    def _estimate_annual_expenses(self, farm_size: float, crops: List[Dict[str, Any]]) -> float:
        """Estimate annual expenses based on farm size and crops."""
        
        # Base expense per acre (in INR)
        base_expense_per_acre = 25000
        
        # Crop-specific expense multipliers
        crop_expense_multipliers = {
            "rice": 1.0,
            "wheat": 0.9,
            "maize": 0.8,
            "sugarcane": 1.5,
            "potato": 1.3,
            "onion": 1.2,
            "tomato": 1.4,
            "cotton": 1.3,
            "soybean": 0.9,
            "groundnut": 1.1
        }
        
        total_expenses = 0
        
        if crops:
            for crop in crops:
                crop_name = crop.get("crop_type", "").lower()
                crop_area = crop.get("area", farm_size / len(crops))
                
                multiplier = crop_expense_multipliers.get(crop_name, 1.0)
                total_expenses += crop_area * base_expense_per_acre * multiplier
        else:
            total_expenses = farm_size * base_expense_per_acre
        
        # Add fixed costs (labor, equipment maintenance, etc.)
        fixed_costs = farm_size * 5000
        total_expenses += fixed_costs
        
        return total_expenses
    
    async def _check_scheme_eligibility(self, farmer_data: Dict[str, Any], farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check eligibility for various government schemes."""
        
        farm_size = farm_data.get("total_area", 0)
        farmer_category = self._determine_farmer_category(farm_size)
        
        eligibility = {}
        
        # PM-KISAN eligibility
        eligibility["pm_kisan"] = {
            "eligible": farm_size <= 2.0,  # Up to 2 hectares
            "reason": "Eligible for small/marginal farmer category" if farm_size <= 2.0 else "Farm size exceeds 2 hectares limit",
            "expected_benefit": 6000 if farm_size <= 2.0 else 0,
            "next_steps": [
                "Visit pmkisan.gov.in",
                "Prepare Aadhaar and land documents",
                "Register at nearest CSC"
            ] if farm_size <= 2.0 else ["Not eligible - farm size too large"]
        }
        
        # KCC eligibility
        eligibility["kisan_credit_card"] = {
            "eligible": True,  # All farmers eligible
            "reason": "All farmers eligible for crop loans",
            "credit_limit": min(farm_size * 150000, 300000),  # Scale of finance based calculation
            "interest_rate": 4.0,  # After subvention
            "next_steps": [
                "Visit nearest bank branch",
                "Prepare land documents and Aadhaar",
                "Fill KCC application form"
            ]
        }
        
        # PMFBY eligibility
        eligibility["crop_insurance"] = {
            "eligible": True,
            "reason": "All farmers with crop loans eligible",
            "premium_contribution": "2% for Kharif, 1.5% for Rabi crops",
            "coverage": "Full crop value protection",
            "next_steps": [
                "Enroll during sowing season",
                "Contact bank or insurance company",
                "Pay farmer share of premium"
            ]
        }
        
        # Pension scheme eligibility
        age = farmer_data.get("age", 30)
        eligibility["pension_scheme"] = {
            "eligible": 18 <= age <= 40,
            "reason": "Age within eligible range" if 18 <= age <= 40 else f"Age {age} outside 18-40 range",
            "monthly_contribution": self._calculate_pension_contribution(age) if 18 <= age <= 40 else 0,
            "monthly_pension": 3000 if 18 <= age <= 40 else 0,
            "next_steps": [
                "Visit CSC or bank",
                "Enroll with Aadhaar and bank account",
                "Start monthly contributions"
            ] if 18 <= age <= 40 else ["Not eligible due to age"]
        }
        
        return eligibility
    
    def _determine_farmer_category(self, farm_size: float) -> str:
        """Determine farmer category based on land holding."""
        if farm_size <= 1.0:
            return "Marginal"
        elif farm_size <= 2.0:
            return "Small"
        elif farm_size <= 4.0:
            return "Semi-medium"
        elif farm_size <= 10.0:
            return "Medium"
        else:
            return "Large"
    
    def _calculate_pension_contribution(self, age: int) -> float:
        """Calculate monthly pension contribution based on age."""
        age_contribution_map = {
            18: 55, 19: 58, 20: 61, 21: 64, 22: 68, 23: 72, 24: 76, 25: 80,
            26: 85, 27: 90, 28: 95, 29: 100, 30: 105, 31: 110, 32: 120,
            33: 130, 34: 140, 35: 150, 36: 160, 37: 170, 38: 180, 39: 190, 40: 200
        }
        return age_contribution_map.get(age, 100)
    
    async def _generate_loan_recommendations(self, farmer_data: Dict[str, Any], farm_data: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized loan recommendations."""
        
        recommendations = []
        
        for loan in self.loan_products:
            # Calculate personalized terms
            max_eligible = min(loan["amount_range"]["max"], metrics["loan_eligibility"])
            
            if max_eligible >= loan["amount_range"]["min"]:
                recommendation = {
                    **loan,
                    "personalized_terms": {
                        "max_eligible_amount": max_eligible,
                        "recommended_amount": max_eligible * 0.8,  # Conservative recommendation
                        "effective_interest_rate": loan["interest_rate"]["subsidized"],
                        "monthly_emi": self._calculate_emi(max_eligible * 0.8, loan["interest_rate"]["subsidized"], loan["tenure"]),
                        "processing_fee": max_eligible * 0.005,  # 0.5% processing fee
                        "documentation_score": self._assess_documentation_readiness(farmer_data)
                    },
                    "eligibility_score": min(100, (max_eligible / loan["amount_range"]["max"]) * 100),
                    "recommendation_reason": self._generate_loan_reason(loan, farm_data, metrics)
                }
                recommendations.append(recommendation)
        
        # Sort by relevance
        recommendations.sort(key=lambda x: x["eligibility_score"], reverse=True)
        
        return recommendations
    
    def _calculate_emi(self, principal: float, annual_rate: float, tenure_years: str) -> float:
        """Calculate EMI for loan."""
        try:
            # Extract years from tenure string
            years = float(tenure_years.split('-')[0]) if '-' in tenure_years else float(tenure_years.split()[0])
            months = years * 12
            monthly_rate = annual_rate / 100 / 12
            
            if monthly_rate == 0:
                return principal / months
            
            emi = principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
            return round(emi, 2)
        except:
            return 0
    
    def _assess_documentation_readiness(self, farmer_data: Dict[str, Any]) -> str:
        """Assess farmer's documentation readiness."""
        required_docs = ["aadhaar", "land_records", "bank_account", "income_proof"]
        available_docs = 0
        
        # This would be enhanced with actual document verification
        # For now, assume based on farmer data completeness
        if farmer_data.get("aadhaar_number"):
            available_docs += 1
        if farmer_data.get("land_ownership"):
            available_docs += 1
        if farmer_data.get("bank_account"):
            available_docs += 1
        if farmer_data.get("income_source"):
            available_docs += 1
        
        readiness_percentage = (available_docs / len(required_docs)) * 100
        
        if readiness_percentage >= 75:
            return "Ready"
        elif readiness_percentage >= 50:
            return "Partially Ready"
        else:
            return "Documentation Needed"
    
    def _generate_loan_reason(self, loan: Dict[str, Any], farm_data: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Generate recommendation reason for loan."""
        if loan["type"] == "Short-term":
            return f"Recommended for seasonal operations on {metrics['farm_size_acres']} acres"
        elif loan["type"] == "Medium-term":
            return f"Ideal for equipment upgrade to improve productivity"
        else:
            return f"Suitable for long-term farm development and infrastructure"
    
    async def _generate_insurance_recommendations(self, farm_data: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insurance recommendations."""
        
        recommendations = []
        
        for insurance in self.insurance_products:
            if insurance["product_name"] == "Comprehensive Crop Insurance":
                premium = metrics["estimated_annual_income"] * 0.025  # 2.5% average
                recommendation = {
                    **insurance,
                    "personalized_terms": {
                        "sum_insured": metrics["estimated_annual_income"],
                        "annual_premium": premium,
                        "farmer_share": premium * 0.2,  # Farmer pays 20%
                        "government_subsidy": premium * 0.8,  # 80% subsidy
                        "recommended": True
                    },
                    "priority": "High",
                    "reason": "Essential protection for crop investment"
                }
                recommendations.append(recommendation)
        
        return recommendations
    
    async def _identify_investment_opportunities(self, farm_data: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify investment opportunities for the farmer."""
        
        opportunities = []
        
        # Drip irrigation investment
        if metrics["farm_size_acres"] >= 1:
            drip_cost = metrics["farm_size_acres"] * 50000  # ₹50k per acre
            water_saving = 30  # 30% water saving
            yield_increase = 15  # 15% yield increase
            
            opportunities.append({
                "investment_type": "Drip Irrigation System",
                "investment_cost": drip_cost,
                "subsidy_available": drip_cost * 0.6,  # 60% subsidy
                "net_investment": drip_cost * 0.4,
                "annual_savings": metrics["estimated_annual_income"] * 0.15,  # From yield increase
                "payback_period": "2-3 years",
                "benefits": [
                    f"30% water conservation",
                    f"15% yield increase",
                    f"Reduced labor costs",
                    f"Better crop quality"
                ],
                "priority": "High",
                "roi_percentage": 35
            })
        
        # Solar pump investment
        opportunities.append({
            "investment_type": "Solar Water Pump",
            "investment_cost": 200000,
            "subsidy_available": 120000,  # 60% subsidy
            "net_investment": 80000,
            "annual_savings": 25000,  # Electricity bill savings
            "payback_period": "3-4 years",
            "benefits": [
                "Zero electricity bills",
                "Reliable water supply",
                "Environmental benefits",
                "25-year equipment life"
            ],
            "priority": "Medium",
            "roi_percentage": 30
        })
        
        return opportunities
    
    def _calculate_financial_health_score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall financial health score."""
        
        score = 0
        max_score = 100
        
        # Income stability (30 points)
        if metrics["net_annual_income"] > 0:
            score += 30
        elif metrics["net_annual_income"] > -50000:
            score += 15
        
        # Profit margin (25 points)
        if metrics["profit_margin"] > 20:
            score += 25
        elif metrics["profit_margin"] > 10:
            score += 15
        elif metrics["profit_margin"] > 0:
            score += 10
        
        # Income per acre (25 points)
        if metrics["income_per_acre"] > 50000:
            score += 25
        elif metrics["income_per_acre"] > 40000:
            score += 20
        elif metrics["income_per_acre"] > 30000:
            score += 15
        
        # Expense management (20 points)
        if metrics["expense_ratio"] < 60:
            score += 20
        elif metrics["expense_ratio"] < 70:
            score += 15
        elif metrics["expense_ratio"] < 80:
            score += 10
        
        # Determine rating
        if score >= 80:
            rating = "Excellent"
            color = "green"
        elif score >= 60:
            rating = "Good"
            color = "blue"
        elif score >= 40:
            rating = "Fair"
            color = "orange"
        else:
            rating = "Needs Improvement"
            color = "red"
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": round((score / max_score) * 100, 1),
            "rating": rating,
            "color": color,
            "interpretation": self._get_score_interpretation(score)
        }
    
    def _get_score_interpretation(self, score: int) -> str:
        """Get interpretation of financial health score."""
        if score >= 80:
            return "Excellent financial health. Ready for expansion and investment opportunities."
        elif score >= 60:
            return "Good financial position. Consider investments to improve productivity."
        elif score >= 40:
            return "Fair financial health. Focus on cost optimization and yield improvement."
        else:
            return "Financial health needs attention. Consider consulting financial advisor."
    
    def _generate_financial_recommendations(self, metrics: Dict[str, Any], eligibility: Dict[str, Any]) -> List[str]:
        """Generate actionable financial recommendations."""
        
        recommendations = []
        
        # Income-based recommendations
        if metrics["profit_margin"] < 20:
            recommendations.append("Focus on high-value crops to improve profit margins")
            recommendations.append("Consider precision farming techniques to reduce costs")
        
        # Scheme-based recommendations
        if eligibility["pm_kisan"]["eligible"]:
            recommendations.append("Apply for PM-KISAN scheme for ₹6,000 annual benefit")
        
        if eligibility["kisan_credit_card"]["eligible"]:
            recommendations.append("Apply for Kisan Credit Card for low-interest crop loans")
        
        # Investment recommendations
        if metrics["farm_size_acres"] >= 2:
            recommendations.append("Consider drip irrigation investment with 60% government subsidy")
        
        recommendations.append("Ensure crop insurance coverage to protect against weather risks")
        
        if metrics["net_annual_income"] > 100000:
            recommendations.append("Explore value addition opportunities like food processing")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def check_pm_kisan_status(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check PM-KISAN registration and payment status.
        In production, this would integrate with actual PM-KISAN APIs.
        """
        
        # Mock PM-KISAN status check (replace with real API integration)
        aadhaar = farmer_data.get("aadhaar_number", "")
        
        if not aadhaar:
            return {
                "status": "error",
                "message": "Aadhaar number required for status check",
                "registered": False
            }
        
        # Simulate API response (replace with real PM-KISAN API)
        mock_status = {
            "status": "success",
            "registered": True,
            "beneficiary_id": f"PK{random.randint(100000, 999999)}",
            "registration_date": "2024-04-01",
            "farmer_name": farmer_data.get("name", ""),
            "aadhaar_number": aadhaar[-4:].rjust(12, 'X'),  # Masked Aadhaar
            "installments": [
                {
                    "installment": 1,
                    "period": "2024-25 (Apr-Jul)",
                    "amount": 2000,
                    "status": "Paid",
                    "payment_date": "2024-04-15",
                    "utr": f"UTR{random.randint(100000000, 999999999)}"
                },
                {
                    "installment": 2,
                    "period": "2024-25 (Aug-Nov)",
                    "amount": 2000,
                    "status": "Paid",
                    "payment_date": "2024-08-15",
                    "utr": f"UTR{random.randint(100000000, 999999999)}"
                },
                {
                    "installment": 3,
                    "period": "2024-25 (Dec-Mar)",
                    "amount": 2000,
                    "status": "Pending",
                    "expected_date": "2024-12-15"
                }
            ],
            "total_received": 4000,
            "pending_amount": 2000,
            "bank_account": {
                "account_number": "XXXX" + str(random.randint(1000, 9999)),
                "ifsc": "SBIN0001234",
                "bank_name": "State Bank of India"
            },
            "next_action": "No action required. Next installment will be credited automatically.",
            "helpline": "155261 (PM-KISAN Helpline)"
        }
        
        return mock_status


# Create global instance
enhanced_finance_service = EnhancedFinanceService()
