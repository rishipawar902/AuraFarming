#!/usr/bin/env python3
"""Simple test for enhanced finance service."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

print("💰 AuraFarming: Enhanced Finance Integration Test")
print("=" * 60)
print("🎯 Testing comprehensive financial services")
print("🏦 Government schemes & banking integration")
print("=" * 60)

# Test farmer data
test_farmer = {
    "farmer_id": "F001",
    "name": "Ram Kumar",
    "phone": "9876543210",
    "aadhaar_number": "123456789012",
    "age": 32,
    "location": {"district": "Ranchi", "state": "Jharkhand"},
    "farming_experience": 8,
    "bank_account": "12345678901",
    "land_ownership": True,
    "income_source": "farming"
}

test_farm = {
    "farm_id": "FM001",
    "name": "Kumar Farm",
    "total_area": 3.5,
    "location": {"latitude": 23.3441, "longitude": 85.3096},
    "crops": [
        {"crop_type": "Rice", "area": 2.0, "season": "Kharif"},
        {"crop_type": "Wheat", "area": 1.5, "season": "Rabi"}
    ],
    "irrigation_type": "Tubewell",
    "soil_type": "Alluvial"
}

print("📊 Test: Enhanced Finance Service Integration")
print("-" * 40)

try:
    from app.services.enhanced_finance_service import enhanced_finance_service
    print("✅ Enhanced finance service imported successfully")
    
    # Test financial calculations
    result = enhanced_finance_service._calculate_financial_metrics(test_farm, test_farmer)
    print("✅ Financial metrics calculated:")
    print(f"   🏞️ Farm size: {result['farm_size_acres']} acres")
    print(f"   💰 Annual income: ₹{result['estimated_annual_income']:,.0f}")
    print(f"   💸 Annual expenses: ₹{result['estimated_annual_expenses']:,.0f}")
    print(f"   📈 Net income: ₹{result['net_annual_income']:,.0f}")
    print(f"   📊 Profit margin: {result['profit_margin']:.1f}%")
    print(f"   🏦 Loan eligibility: ₹{result['loan_eligibility']:,.0f}")
    
    # Test financial health scoring
    health_score = enhanced_finance_service._calculate_financial_health_score(result, test_farmer)
    print("\n🎯 Financial Health Score:")
    print(f"   📊 Score: {health_score['score']}/{health_score['max_score']} ({health_score['percentage']:.1f}%)")
    print(f"   ⭐ Rating: {health_score['rating']}")
    print(f"   💡 Interpretation: {health_score['interpretation']}")
    
    # Test scheme eligibility
    scheme_eligibility = enhanced_finance_service._check_scheme_eligibility(test_farmer, test_farm, result)
    
    pm_kisan = scheme_eligibility["pm_kisan"]
    print("\n✅ PM-KISAN Scheme:")
    print(f"   🎯 Eligible: {'Yes' if pm_kisan['eligible'] else 'No'}")
    print(f"   💰 Benefit: ₹{pm_kisan['expected_benefit']:,}/year")
    print(f"   📋 Reason: {pm_kisan['reason']}")
    
    kcc = scheme_eligibility["kisan_credit_card"]
    print("\n✅ Kisan Credit Card:")
    print(f"   🎯 Eligible: {'Yes' if kcc['eligible'] else 'No'}")
    print(f"   💰 Credit limit: ₹{kcc['credit_limit']:,}")
    print(f"   📊 Interest rate: {kcc['interest_rate']}%")
    
    # Test loan recommendations  
    loan_products = enhanced_finance_service._get_personalized_loan_products(test_farmer, test_farm, result)
    print(f"\n🏦 Loan Recommendations:")
    print(f"✅ {len(loan_products)} loan products generated")
    
    for i, loan in enumerate(loan_products[:2], 1):  # Show top 2
        terms = loan["personalized_terms"]
        print(f"\n   {i}. {loan['product_name']} ({loan['type']})")
        print(f"      💰 Max eligible: ₹{terms['max_eligible_amount']:,.0f}")
        print(f"      📊 Interest rate: {terms['effective_interest_rate']:.1f}%")
        print(f"      💳 Monthly EMI: ₹{terms['monthly_emi']:,.0f}")
        print(f"      🎯 Eligibility: {loan['eligibility_score']:.0f}%")
    
    # Test investment opportunities
    investments = enhanced_finance_service._get_investment_opportunities(test_farmer, test_farm, result)
    print(f"\n💡 Investment Opportunities:")
    
    for investment in investments[:2]:  # Show top 2
        print(f"✅ {investment['investment_type']}:")
        print(f"   💰 Total cost: ₹{investment['investment_cost']:,.0f}")
        print(f"   🎁 Subsidy: ₹{investment['subsidy_available']:,.0f}")
        print(f"   💸 Your investment: ₹{investment['net_investment']:,.0f}")
        print(f"   📈 ROI: {investment['roi_percentage']}%")
        print(f"   ⏰ Payback: {investment['payback_period']}")
    
    print("\n🚀 Enhanced Finance Integration Summary")
    print("=" * 60)
    print("✅ Financial metrics calculation working")
    print("✅ Financial health scoring operational")
    print("✅ Government scheme eligibility checked")
    print("✅ Loan product recommendations generated")
    print("✅ Investment opportunities identified")
    print("\n🎉 Enhanced finance integration is fully operational!")
    print("   Complete financial intelligence for agricultural success! 💰")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
