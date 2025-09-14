"""
Finance service for financial recommendations and PM-KISAN integration.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import random


class FinanceService:
    """
    Finance service for providing financial recommendations and government scheme information.
    """
    
    def __init__(self):
        """Initialize finance service."""
        self.schemes_data = self._initialize_schemes_data()
        self.loan_schemes = self._initialize_loan_schemes()
        self.insurance_schemes = self._initialize_insurance_schemes()
    
    def _initialize_schemes_data(self) -> Dict[str, Any]:
        """Initialize government schemes data."""
        return {
            "pm_kisan": {
                "name": "PM-KISAN Samman Nidhi",
                "amount": 6000,
                "frequency": "Annual (3 installments of ₹2000)",
                "eligibility": "Small and marginal farmers with landholding up to 2 hectares",
                "application": "Online at pmkisan.gov.in or Common Service Centers"
            },
            "subsidies": [
                {
                    "name": "Fertilizer Subsidy",
                    "benefit": "Subsidized rates on fertilizers",
                    "eligibility": "All farmers",
                    "savings": "30-50% on fertilizer costs"
                },
                {
                    "name": "Seed Subsidy",
                    "benefit": "High-quality seeds at subsidized rates",
                    "eligibility": "Small and marginal farmers",
                    "savings": "25-40% on seed costs"
                },
                {
                    "name": "Drip Irrigation Subsidy",
                    "benefit": "50-80% subsidy on drip irrigation systems",
                    "eligibility": "All farmers with valid land documents",
                    "savings": "₹50,000 - ₹2,00,000"
                }
            ]
        }
    
    def _initialize_loan_schemes(self) -> List[Dict[str, Any]]:
        """Initialize agricultural loan schemes."""
        return [
            {
                "name": "Kisan Credit Card (KCC)",
                "amount_limit": "₹3,00,000",
                "interest_rate": "7% (with 3% subvention)",
                "tenure": "5 years",
                "purpose": "Crop production, post-harvest expenses, maintenance of farm assets",
                "eligibility": "All farmers with land ownership/tenancy",
                "documents": ["Land records", "Identity proof", "Address proof"]
            },
            {
                "name": "Agriculture Term Loan",
                "amount_limit": "₹50,00,000",
                "interest_rate": "8-10%",
                "tenure": "5-10 years",
                "purpose": "Farm mechanization, land development, irrigation",
                "eligibility": "Farmers with collateral security",
                "documents": ["Land documents", "Project report", "Income proof"]
            },
            {
                "name": "Self Help Group (SHG) Loans",
                "amount_limit": "₹10,00,000",
                "interest_rate": "6-8%",
                "tenure": "3-5 years",
                "purpose": "Income generation, agriculture activities",
                "eligibility": "Members of registered SHGs",
                "documents": ["SHG registration", "Group savings record"]
            }
        ]
    
    def _initialize_insurance_schemes(self) -> List[Dict[str, Any]]:
        """Initialize crop insurance schemes."""
        return [
            {
                "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "premium": "2% for Kharif, 1.5% for Rabi crops",
                "coverage": "Up to sum insured based on scale of finance",
                "risks_covered": ["Natural disasters", "Pest attacks", "Disease"],
                "claim_process": "Automatic settlement through technology",
                "eligibility": "All farmers including sharecroppers and tenant farmers"
            },
            {
                "name": "Weather Based Crop Insurance (WBCIS)",
                "premium": "1-3% of sum insured",
                "coverage": "Weather parameter based",
                "risks_covered": ["Rainfall deficit/excess", "Temperature variations"],
                "claim_process": "Automatic based on weather data",
                "eligibility": "All farmers in notified areas"
            }
        ]
    
    async def get_recommendations(
        self, 
        farmer_data: Dict[str, Any], 
        farm_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get personalized financial recommendations.
        
        Args:
            farmer_data: Farmer profile data
            farm_data: Farm profile data
            
        Returns:
            Comprehensive financial recommendations
        """
        recommendations = []
        
        # PM-KISAN eligibility check
        if farm_data and farm_data.get("field_size", 0) <= 2.0:
            recommendations.append({
                "type": "Government Scheme",
                "scheme_name": "PM-KISAN Samman Nidhi",
                "eligibility": "Eligible - Small/marginal farmer",
                "benefits": "₹6,000 annually in 3 installments",
                "application_process": "Online registration at pmkisan.gov.in",
                "priority": "High",
                "estimated_benefit": 6000
            })
        
        # Loan recommendations based on farm size
        if farm_data:
            field_size = farm_data.get("field_size", 0)
            
            if field_size > 0:
                # Always recommend KCC
                recommendations.append({
                    "type": "Credit",
                    "scheme_name": "Kisan Credit Card (KCC)",
                    "eligibility": "Eligible",
                    "benefits": f"Credit limit up to ₹{min(300000, field_size * 50000):,}",
                    "application_process": "Apply at nearest bank branch",
                    "priority": "High",
                    "estimated_benefit": min(300000, field_size * 50000)
                })
            
            if field_size >= 2.0:
                recommendations.append({
                    "type": "Credit",
                    "scheme_name": "Agriculture Term Loan",
                    "eligibility": "Eligible for farm development",
                    "benefits": "Low interest loans for mechanization",
                    "application_process": "Submit project proposal to bank",
                    "priority": "Medium",
                    "estimated_benefit": field_size * 100000
                })
        
        # Insurance recommendations
        recommendations.append({
            "type": "Insurance",
            "scheme_name": "Pradhan Mantri Fasal Bima Yojana",
            "eligibility": "All farmers eligible",
            "benefits": "Crop loss protection with minimal premium",
            "application_process": "Apply through bank or Common Service Center",
            "priority": "High",
            "estimated_benefit": "Risk mitigation"
        })
        
        # Subsidy recommendations
        recommendations.extend([
            {
                "type": "Subsidy",
                "scheme_name": "Fertilizer Subsidy",
                "eligibility": "All farmers eligible",
                "benefits": "30-50% savings on fertilizer costs",
                "application_process": "Available at all fertilizer dealers",
                "priority": "High",
                "estimated_benefit": "₹5,000 - ₹15,000 annually"
            },
            {
                "type": "Subsidy",
                "scheme_name": "Drip Irrigation Subsidy",
                "eligibility": "Land ownership required",
                "benefits": "50-80% subsidy on irrigation systems",
                "application_process": "Apply through Agriculture Department",
                "priority": "Medium",
                "estimated_benefit": "₹50,000 - ₹2,00,000"
            }
        ])
        
        return {
            "farmer_id": farmer_data.get("id"),
            "recommendations": recommendations,
            "total_potential_benefits": sum(
                r.get("estimated_benefit", 0) for r in recommendations 
                if isinstance(r.get("estimated_benefit"), (int, float))
            ),
            "priority_actions": [
                r for r in recommendations if r.get("priority") == "High"
            ],
            "generated_at": datetime.utcnow()
        }
    
    async def check_pm_kisan_status(
        self, 
        farmer_data: Dict[str, Any], 
        farm_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check PM-KISAN scheme status and eligibility.
        
        Args:
            farmer_data: Farmer profile data
            farm_data: Farm profile data
            
        Returns:
            PM-KISAN status and information
        """
        # Mock PM-KISAN status check
        phone = farmer_data.get("phone", "")
        is_eligible = farm_data and farm_data.get("field_size", 0) <= 2.0
        
        # Simulate registration status
        is_registered = random.choice([True, False])
        
        status_data = {
            "scheme_name": "PM-KISAN Samman Nidhi",
            "farmer_phone": phone,
            "eligibility_status": "Eligible" if is_eligible else "Not eligible (land > 2 hectares)",
            "registration_status": "Registered" if is_registered and is_eligible else "Not registered",
            "benefits": {
                "amount_per_year": 6000,
                "installments": 3,
                "amount_per_installment": 2000
            }
        }
        
        if is_eligible and is_registered:
            # Mock payment history
            status_data["payment_history"] = [
                {"installment": 1, "amount": 2000, "date": "2024-04-01", "status": "Paid"},
                {"installment": 2, "amount": 2000, "date": "2024-08-01", "status": "Paid"},
                {"installment": 3, "amount": 2000, "date": "2024-12-01", "status": "Pending"}
            ]
            status_data["total_received"] = 4000
            status_data["next_installment"] = "December 2024"
        
        elif is_eligible and not is_registered:
            status_data["action_required"] = {
                "message": "You are eligible but not registered",
                "steps": [
                    "Visit pmkisan.gov.in",
                    "Click on 'New Farmer Registration'",
                    "Fill in required details",
                    "Upload land documents",
                    "Submit application"
                ],
                "documents_needed": [
                    "Aadhaar card",
                    "Bank account details",
                    "Land ownership documents"
                ]
            }
        
        return {
            "pm_kisan_data": status_data,
            "last_updated": datetime.utcnow()
        }
    
    async def get_agriculture_loans(
        self, 
        farmer_data: Dict[str, Any], 
        farm_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get applicable agriculture loan schemes.
        
        Args:
            farmer_data: Farmer profile data
            farm_data: Farm profile data
            
        Returns:
            List of applicable loan schemes
        """
        applicable_loans = []
        
        for loan in self.loan_schemes:
            # Basic eligibility assessment
            eligibility_score = random.uniform(0.7, 1.0)  # Mock eligibility assessment
            
            loan_info = loan.copy()
            loan_info["eligibility_assessment"] = {
                "score": round(eligibility_score, 2),
                "status": "Likely eligible" if eligibility_score > 0.8 else "May be eligible",
                "factors": [
                    "Land ownership documents required",
                    "Credit history will be checked",
                    "Income proof may be needed"
                ]
            }
            
            # Estimate loan amount based on farm size
            if farm_data and "field_size" in farm_data:
                field_size = farm_data["field_size"]
                if loan["name"] == "Kisan Credit Card (KCC)":
                    estimated_amount = min(300000, field_size * 50000)
                elif loan["name"] == "Agriculture Term Loan":
                    estimated_amount = min(5000000, field_size * 200000)
                else:
                    estimated_amount = min(1000000, field_size * 100000)
                
                loan_info["estimated_loan_amount"] = f"₹{estimated_amount:,}"
            
            applicable_loans.append(loan_info)
        
        return {
            "farmer_id": farmer_data.get("id"),
            "applicable_loans": applicable_loans,
            "recommendations": [
                "Start with KCC for immediate working capital needs",
                "Consider term loan for long-term investments",
                "Maintain good repayment record for future loans"
            ],
            "generated_at": datetime.utcnow()
        }
    
    async def get_crop_insurance(
        self, 
        farmer_data: Dict[str, Any], 
        farm_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get crop insurance options.
        
        Args:
            farmer_data: Farmer profile data
            farm_data: Farm profile data
            
        Returns:
            Available crop insurance schemes
        """
        insurance_options = []
        
        for insurance in self.insurance_schemes:
            insurance_info = insurance.copy()
            
            # Calculate estimated premium based on farm size
            if farm_data and "field_size" in farm_data:
                field_size = farm_data["field_size"]
                sum_insured = field_size * 50000  # ₹50,000 per acre
                
                if insurance["name"] == "Pradhan Mantri Fasal Bima Yojana (PMFBY)":
                    premium_rate = 0.02  # 2% for Kharif
                else:
                    premium_rate = 0.025  # 2.5% average
                
                premium_amount = sum_insured * premium_rate
                
                insurance_info["cost_estimate"] = {
                    "sum_insured": f"₹{sum_insured:,}",
                    "annual_premium": f"₹{premium_amount:,}",
                    "government_subsidy": f"₹{premium_amount * 0.8:,}",  # 80% subsidy
                    "farmer_contribution": f"₹{premium_amount * 0.2:,}"  # 20% farmer share
                }
            
            insurance_options.append(insurance_info)
        
        return {
            "farmer_id": farmer_data.get("id"),
            "insurance_options": insurance_options,
            "benefits": [
                "Protection against natural calamities",
                "Minimal premium with government subsidy",
                "Quick claim settlement process"
            ],
            "generated_at": datetime.utcnow()
        }
    
    async def get_subsidies(
        self, 
        farmer_data: Dict[str, Any], 
        farm_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get available government subsidies.
        
        Args:
            farmer_data: Farmer profile data
            farm_data: Farm profile data
            
        Returns:
            List of applicable subsidies
        """
        applicable_subsidies = self.schemes_data["subsidies"].copy()
        
        # Add estimated savings based on farm size
        if farm_data and "field_size" in farm_data:
            field_size = farm_data["field_size"]
            
            for subsidy in applicable_subsidies:
                if subsidy["name"] == "Fertilizer Subsidy":
                    annual_savings = field_size * 5000  # ₹5,000 per acre
                    subsidy["estimated_annual_savings"] = f"₹{annual_savings:,}"
                
                elif subsidy["name"] == "Drip Irrigation Subsidy":
                    if field_size >= 1.0:  # Minimum 1 acre for drip irrigation
                        system_cost = field_size * 80000  # ₹80,000 per acre
                        subsidy_amount = system_cost * 0.6  # 60% subsidy
                        subsidy["estimated_subsidy"] = f"₹{subsidy_amount:,}"
                        subsidy["total_investment"] = f"₹{system_cost:,}"
                        subsidy["farmer_contribution"] = f"₹{system_cost - subsidy_amount:,}"
        
        return {
            "farmer_id": farmer_data.get("id"),
            "applicable_subsidies": applicable_subsidies,
            "application_tips": [
                "Apply early in the season for input subsidies",
                "Keep all purchase receipts for claim processing",
                "Ensure land documents are up to date"
            ],
            "generated_at": datetime.utcnow()
        }
    
    async def calculate_projected_income(
        self, 
        crop: str, 
        area: float, 
        farm_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate projected income for a crop.
        
        Args:
            crop: Crop name
            area: Cultivation area in acres
            farm_data: Farm data for location-based calculations
            
        Returns:
            Detailed income projection
        """
        # Mock yield and price data
        crop_data = {
            "Rice": {"yield_per_acre": 18, "price_per_quintal": 2000},
            "Wheat": {"yield_per_acre": 22, "price_per_quintal": 2100},
            "Maize": {"yield_per_acre": 25, "price_per_quintal": 1600},
            "Potato": {"yield_per_acre": 180, "price_per_quintal": 1000},
            "Arhar": {"yield_per_acre": 12, "price_per_quintal": 6000},
            "Groundnut": {"yield_per_acre": 15, "price_per_quintal": 5000}
        }
        
        crop_info = crop_data.get(crop, {"yield_per_acre": 15, "price_per_quintal": 2000})
        
        # Calculate production and revenue
        total_yield = crop_info["yield_per_acre"] * area
        gross_revenue = total_yield * crop_info["price_per_quintal"]
        
        # Calculate costs
        cost_per_acre = {
            "seeds": 2000,
            "fertilizers": 5000,
            "pesticides": 1500,
            "labor": 8000,
            "machinery": 3000,
            "irrigation": 2000,
            "miscellaneous": 1500
        }
        
        total_cost_per_acre = sum(cost_per_acre.values())
        total_cost = total_cost_per_acre * area
        
        # Calculate profit
        net_profit = gross_revenue - total_cost
        profit_margin = (net_profit / gross_revenue) * 100 if gross_revenue > 0 else 0
        
        return {
            "crop": crop,
            "cultivation_area": area,
            "production_estimate": {
                "yield_per_acre": crop_info["yield_per_acre"],
                "total_yield_quintals": total_yield,
                "market_price_per_quintal": crop_info["price_per_quintal"]
            },
            "financial_projection": {
                "gross_revenue": gross_revenue,
                "total_cost": total_cost,
                "net_profit": net_profit,
                "profit_margin_percentage": round(profit_margin, 2),
                "return_on_investment": round((net_profit / total_cost) * 100, 2) if total_cost > 0 else 0
            },
            "cost_breakdown": {k: v * area for k, v in cost_per_acre.items()},
            "recommendations": [
                "Consider crop insurance to protect investment",
                "Explore value addition for better prices",
                "Join FPO for input cost reduction"
            ],
            "generated_at": datetime.utcnow()
        }
    
    async def get_microfinance_options(
        self, 
        farmer_data: Dict[str, Any], 
        farm_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get microfinance and SHG options.
        
        Args:
            farmer_data: Farmer profile data
            farm_data: Farm profile data
            
        Returns:
            Microfinance options and Self Help Group information
        """
        microfinance_options = [
            {
                "name": "Women Self Help Group (SHG)",
                "loan_amount": "₹10,000 - ₹5,00,000",
                "interest_rate": "6-8%",
                "eligibility": "Women farmers, group membership required",
                "process": "Form/join SHG, maintain savings for 6 months, apply for loan",
                "benefits": ["Low interest", "No collateral", "Skill development programs"]
            },
            {
                "name": "Joint Liability Group (JLG)",
                "loan_amount": "₹25,000 - ₹2,00,000",
                "interest_rate": "8-10%",
                "eligibility": "Group of 4-10 farmers",
                "process": "Form group, get training, apply through bank",
                "benefits": ["Higher loan amounts", "Group guarantee", "Lower documentation"]
            },
            {
                "name": "Farmer Producer Company (FPC)",
                "loan_amount": "₹50,000 - ₹10,00,000",
                "interest_rate": "7-9%",
                "eligibility": "Member of registered FPC",
                "process": "Join FPC, contribute equity, apply for collective loan",
                "benefits": ["Bulk purchasing", "Better market access", "Technical support"]
            }
        ]
        
        return {
            "farmer_id": farmer_data.get("id"),
            "microfinance_options": microfinance_options,
            "local_contacts": [
                {
                    "organization": "Jharkhand State Livelihood Promotion Society",
                    "contact": "+91-651-2446430",
                    "services": ["SHG formation", "Capacity building", "Loan facilitation"]
                },
                {
                    "organization": "National Rural Livelihood Mission",
                    "contact": "Visit nearest Block office",
                    "services": ["Community mobilization", "Skill development", "Market linkage"]
                }
            ],
            "next_steps": [
                "Identify and join suitable group",
                "Participate in training programs",
                "Maintain regular savings habit",
                "Build good credit history"
            ],
            "generated_at": datetime.utcnow()
        }