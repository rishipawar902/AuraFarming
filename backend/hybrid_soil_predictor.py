"""
Strategy 4: Hybrid Approach - Rule-Based + ML
Combine XGBoost predictions with soil-specific agricultural knowledge
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class CropSuitability:
    """Crop suitability score with reasoning."""
    crop: str
    ml_score: float
    rule_score: float
    combined_score: float
    reasoning: List[str]
    soil_compatibility: float

class HybridSoilCropPredictor:
    """Hybrid predictor combining ML and agricultural rules."""
    
    def __init__(self):
        """Initialize hybrid predictor."""
        
        # Detailed soil-crop compatibility rules
        self.soil_crop_rules = {
            'Clay Soil': {
                'rice': {
                    'suitability': 0.95,
                    'reasons': ['Excellent water retention for rice', 'Good for puddling', 'High nutrient holding'],
                    'npk_preference': {'N': 1.1, 'P': 1.0, 'K': 1.2},
                    'ph_range': (5.5, 7.0)
                },
                'wheat': {
                    'suitability': 0.75,
                    'reasons': ['Good nutrient retention', 'May have drainage issues', 'Requires good tillage'],
                    'npk_preference': {'N': 1.0, 'P': 1.1, 'K': 1.0},
                    'ph_range': (6.0, 7.5)
                },
                'cotton': {
                    'suitability': 0.85,
                    'reasons': ['Good water retention', 'High nutrient availability', 'Black cotton soil ideal'],
                    'npk_preference': {'N': 1.2, 'P': 1.1, 'K': 1.3},
                    'ph_range': (5.8, 8.0)
                },
                'maize': {
                    'suitability': 0.70,
                    'reasons': ['Adequate nutrients', 'May face waterlogging', 'Requires good drainage'],
                    'npk_preference': {'N': 1.1, 'P': 1.0, 'K': 1.1},
                    'ph_range': (6.0, 7.0)
                },
                'sugarcane': {
                    'suitability': 0.80,
                    'reasons': ['Excellent water retention', 'High nutrient holding', 'Good for long duration crop'],
                    'npk_preference': {'N': 1.2, 'P': 1.0, 'K': 1.2},
                    'ph_range': (6.5, 7.5)
                }
            },
            
            'Loamy Soil': {
                'wheat': {
                    'suitability': 0.95,
                    'reasons': ['Ideal soil texture', 'Perfect drainage', 'Excellent workability'],
                    'npk_preference': {'N': 1.0, 'P': 1.0, 'K': 1.0},
                    'ph_range': (6.0, 7.5)
                },
                'maize': {
                    'suitability': 0.90,
                    'reasons': ['Optimal drainage', 'Good aeration', 'Easy cultivation'],
                    'npk_preference': {'N': 1.0, 'P': 1.0, 'K': 1.0},
                    'ph_range': (6.0, 7.0)
                },
                'rice': {
                    'suitability': 0.75,
                    'reasons': ['Good fertility', 'May need irrigation management', 'Versatile soil'],
                    'npk_preference': {'N': 1.0, 'P': 1.0, 'K': 1.0},
                    'ph_range': (5.5, 7.0)
                },
                'cotton': {
                    'suitability': 0.80,
                    'reasons': ['Good drainage', 'Adequate nutrients', 'Easy management'],
                    'npk_preference': {'N': 1.0, 'P': 1.0, 'K': 1.1},
                    'ph_range': (6.0, 7.5)
                },
                'vegetables': {
                    'suitability': 0.95,
                    'reasons': ['Perfect for vegetables', 'Easy cultivation', 'Good water management'],
                    'npk_preference': {'N': 1.1, 'P': 1.2, 'K': 1.1},
                    'ph_range': (6.0, 7.0)
                }
            },
            
            'Sandy Soil': {
                'groundnut': {
                    'suitability': 0.90,
                    'reasons': ['Excellent drainage', 'Good for pod development', 'Easy harvesting'],
                    'npk_preference': {'N': 0.8, 'P': 1.1, 'K': 1.0},
                    'ph_range': (6.0, 7.0)
                },
                'millets': {
                    'suitability': 0.85,
                    'reasons': ['Drought tolerant match', 'Good drainage', 'Low water requirement'],
                    'npk_preference': {'N': 0.8, 'P': 0.9, 'K': 0.9},
                    'ph_range': (5.5, 7.5)
                },
                'cotton': {
                    'suitability': 0.65,
                    'reasons': ['Needs frequent irrigation', 'Nutrient leaching possible', 'Good aeration'],
                    'npk_preference': {'N': 1.2, 'P': 1.3, 'K': 1.1},
                    'ph_range': (6.0, 7.5)
                },
                'watermelon': {
                    'suitability': 0.85,
                    'reasons': ['Excellent drainage prevents root rot', 'Good for vine crops', 'Easy cultivation'],
                    'npk_preference': {'N': 1.0, 'P': 1.1, 'K': 1.2},
                    'ph_range': (6.0, 7.0)
                }
            },
            
            'Black Soil': {
                'cotton': {
                    'suitability': 0.98,
                    'reasons': ['Legendary black cotton soil', 'Perfect moisture retention', 'Ideal texture'],
                    'npk_preference': {'N': 1.1, 'P': 1.0, 'K': 1.2},
                    'ph_range': (7.0, 8.5)
                },
                'sugarcane': {
                    'suitability': 0.90,
                    'reasons': ['High water retention', 'Rich in nutrients', 'Good for long duration'],
                    'npk_preference': {'N': 1.1, 'P': 1.0, 'K': 1.1},
                    'ph_range': (6.5, 8.0)
                },
                'soybean': {
                    'suitability': 0.85,
                    'reasons': ['Good nitrogen fixation support', 'Adequate drainage', 'High fertility'],
                    'npk_preference': {'N': 0.8, 'P': 1.1, 'K': 1.0},
                    'ph_range': (6.0, 7.5)
                },
                'wheat': {
                    'suitability': 0.75,
                    'reasons': ['High fertility', 'May need drainage management', 'Good nutrient supply'],
                    'npk_preference': {'N': 0.9, 'P': 1.0, 'K': 1.0},
                    'ph_range': (6.5, 7.5)
                }
            },
            
            'Red Soil': {
                'groundnut': {
                    'suitability': 0.85,
                    'reasons': ['Good drainage', 'Suitable acidity', 'Good for oil seeds'],
                    'npk_preference': {'N': 1.1, 'P': 1.2, 'K': 1.0},
                    'ph_range': (5.5, 6.5)
                },
                'millets': {
                    'suitability': 0.80,
                    'reasons': ['Drought tolerance match', 'Adapts to low fertility', 'Good drainage'],
                    'npk_preference': {'N': 1.0, 'P': 1.1, 'K': 0.9},
                    'ph_range': (5.0, 7.0)
                },
                'cotton': {
                    'suitability': 0.70,
                    'reasons': ['Needs nutrient supplementation', 'Good drainage', 'Requires management'],
                    'npk_preference': {'N': 1.3, 'P': 1.2, 'K': 1.1},
                    'ph_range': (6.0, 7.0)
                },
                'cashew': {
                    'suitability': 0.90,
                    'reasons': ['Perfect for tree crops', 'Good drainage', 'Suitable acidity'],
                    'npk_preference': {'N': 0.9, 'P': 1.0, 'K': 1.1},
                    'ph_range': (5.0, 6.5)
                }
            },
            
            'Alluvial Soil': {
                'rice': {
                    'suitability': 0.90,
                    'reasons': ['Excellent for rice', 'Good water retention', 'High fertility'],
                    'npk_preference': {'N': 1.0, 'P': 1.0, 'K': 1.0},
                    'ph_range': (6.0, 7.5)
                },
                'wheat': {
                    'suitability': 0.85,
                    'reasons': ['Very suitable', 'Good drainage', 'High productivity'],
                    'npk_preference': {'N': 1.0, 'P': 1.0, 'K': 1.0},
                    'ph_range': (6.5, 7.5)
                },
                'sugarcane': {
                    'suitability': 0.88,
                    'reasons': ['Excellent fertility', 'Good water retention', 'High yielding'],
                    'npk_preference': {'N': 1.1, 'P': 1.0, 'K': 1.1},
                    'ph_range': (6.5, 7.5)
                },
                'maize': {
                    'suitability': 0.80,
                    'reasons': ['Good fertility', 'Adequate drainage', 'Versatile soil'],
                    'npk_preference': {'N': 1.0, 'P': 1.0, 'K': 1.0},
                    'ph_range': (6.0, 7.0)
                }
            }
        }
    
    def evaluate_crop_with_rules(self, crop: str, soil_type: str, farm_data: Dict[str, Any]) -> CropSuitability:
        """Evaluate crop suitability using agricultural rules."""
        
        # Get soil-crop rules
        soil_rules = self.soil_crop_rules.get(soil_type, {})
        crop_rules = soil_rules.get(crop.lower(), None)
        
        if not crop_rules:
            # Default evaluation for unknown combinations
            return CropSuitability(
                crop=crop,
                ml_score=0.5,
                rule_score=0.5,
                combined_score=0.5,
                reasoning=['No specific rules available'],
                soil_compatibility=0.5
            )
        
        base_suitability = crop_rules['suitability']
        reasoning = crop_rules['reasons'].copy()
        
        # Evaluate based on farm conditions
        rule_score = base_suitability
        
        # pH evaluation
        ph_range = crop_rules['ph_range']
        current_ph = farm_data.get('ph', 6.5)
        
        if ph_range[0] <= current_ph <= ph_range[1]:
            ph_bonus = 0.1
            reasoning.append(f'pH {current_ph:.1f} is optimal')
        elif abs(current_ph - np.mean(ph_range)) < 1.0:
            ph_bonus = 0.05
            reasoning.append(f'pH {current_ph:.1f} is acceptable')
        else:
            ph_bonus = -0.1
            reasoning.append(f'pH {current_ph:.1f} needs adjustment')
        
        rule_score += ph_bonus
        
        # NPK evaluation
        npk_prefs = crop_rules['npk_preference']
        npk_score = 0
        
        for nutrient in ['N', 'P', 'K']:
            if nutrient in farm_data:
                expected = npk_prefs.get(nutrient, 1.0) * 75  # Base expectation
                actual = farm_data[nutrient]
                
                if actual >= expected * 0.8:  # Within 20% is good
                    npk_score += 0.02
                    reasoning.append(f'{nutrient} levels adequate')
                else:
                    npk_score -= 0.02
                    reasoning.append(f'{nutrient} supplementation needed')
        
        rule_score += npk_score
        
        # Climate evaluation
        temp = farm_data.get('temperature', 25)
        humidity = farm_data.get('humidity', 65)
        rainfall = farm_data.get('rainfall', 500)
        
        # Basic climate suitability (this can be expanded)
        if crop.lower() == 'rice' and rainfall > 800:
            rule_score += 0.05
            reasoning.append('Adequate rainfall for rice')
        elif crop.lower() == 'wheat' and 15 <= temp <= 25:
            rule_score += 0.05
            reasoning.append('Optimal temperature for wheat')
        elif crop.lower() in ['groundnut', 'millets'] and rainfall < 600:
            rule_score += 0.05
            reasoning.append('Suitable for low rainfall crops')
        
        # Cap the rule score
        rule_score = max(0.0, min(1.0, rule_score))
        
        return CropSuitability(
            crop=crop,
            ml_score=0.0,  # Will be filled by ML model
            rule_score=rule_score,
            combined_score=0.0,  # Will be calculated
            reasoning=reasoning,
            soil_compatibility=base_suitability
        )
    
    def combine_ml_and_rules(self, ml_predictions: List[Dict], soil_type: str, 
                           farm_data: Dict[str, Any], alpha: float = 0.7) -> List[CropSuitability]:
        """Combine ML predictions with rule-based evaluation."""
        
        combined_results = []
        
        for ml_pred in ml_predictions:
            crop = ml_pred['crop']
            ml_score = ml_pred['confidence']
            
            # Get rule-based evaluation
            rule_eval = self.evaluate_crop_with_rules(crop, soil_type, farm_data)
            rule_eval.ml_score = ml_score
            
            # Combine scores (weighted average)
            combined_score = alpha * ml_score + (1 - alpha) * rule_eval.rule_score
            
            # Apply soil compatibility boost
            if rule_eval.soil_compatibility > 0.8:
                combined_score *= 1.1  # 10% boost for highly compatible combinations
                rule_eval.reasoning.append('High soil compatibility bonus')
            
            rule_eval.combined_score = min(1.0, combined_score)
            combined_results.append(rule_eval)
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x.combined_score, reverse=True)
        
        return combined_results
    
    def get_soil_specific_recommendations(self, farm_data: Dict[str, Any], 
                                        soil_type: str, ml_predictions: List[Dict]) -> List[Dict]:
        """Get final recommendations combining ML and rules."""
        
        # Combine ML predictions with rules
        combined_results = self.combine_ml_and_rules(ml_predictions, soil_type, farm_data)
        
        # Format final recommendations
        recommendations = []
        
        for result in combined_results:
            recommendations.append({
                'crop': result.crop,
                'confidence': result.combined_score,
                'ml_confidence': result.ml_score,
                'rule_confidence': result.rule_score,
                'soil_compatibility': result.soil_compatibility,
                'reasoning': result.reasoning,
                'soil_type': soil_type,
                'prediction_method': 'hybrid_ml_rules'
            })
        
        return recommendations

# Integration function for existing XGBoost service
def integrate_hybrid_soil_prediction(xgb_service, farm_data: Dict[str, Any], 
                                   soil_type: str, top_k: int = 3) -> List[Dict]:
    """Integrate hybrid prediction with existing XGBoost service."""
    
    # Get ML predictions from existing model
    try:
        ml_predictions = []
        # This would call your existing XGBoost prediction method
        # For now, using mock data
        mock_crops = ['rice', 'wheat', 'cotton', 'maize', 'sugarcane']
        for i, crop in enumerate(mock_crops[:top_k]):
            ml_predictions.append({
                'crop': crop,
                'confidence': 0.8 - i * 0.1  # Mock decreasing confidence
            })
    except Exception as e:
        print(f"ML prediction failed: {e}")
        return []
    
    # Apply hybrid approach
    hybrid_predictor = HybridSoilCropPredictor()
    final_recommendations = hybrid_predictor.get_soil_specific_recommendations(
        farm_data, soil_type, ml_predictions
    )
    
    return final_recommendations[:top_k]

# Usage example
if __name__ == "__main__":
    # Test the hybrid approach
    predictor = HybridSoilCropPredictor()
    
    test_data = {
        'N': 90, 'P': 42, 'K': 43,
        'temperature': 27, 'humidity': 80, 
        'ph': 6.5, 'rainfall': 1200
    }
    
    # Mock ML predictions
    ml_preds = [
        {'crop': 'rice', 'confidence': 0.85},
        {'crop': 'cotton', 'confidence': 0.70},
        {'crop': 'wheat', 'confidence': 0.60}
    ]
    
    results = predictor.get_soil_specific_recommendations(
        test_data, 'Clay Soil', ml_preds
    )
    
    print("Hybrid Predictions for Clay Soil:")
    for result in results:
        print(f"\n{result['crop']}:")
        print(f"  Combined Score: {result['confidence']:.3f}")
        print(f"  ML Score: {result['ml_confidence']:.3f}")
        print(f"  Rule Score: {result['rule_confidence']:.3f}")
        print(f"  Reasoning: {', '.join(result['reasoning'][:3])}")