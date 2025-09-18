"""
XGBoost Model Training Script for AuraFarming
Train the model using the user's Crop_recommendation.csv dataset
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.xgboost_service import get_xgboost_service
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def train_model():
    """Train XGBoost model with user dataset."""
    
    print("🤖 Starting XGBoost Model Training")
    print("=" * 50)
    
    # Get XGBoost service
    xgb_service = get_xgboost_service()
    
    # Path to the dataset
    csv_path = "C:/Users/pawar/Desktop/AuraFarming/Crop_recommendation.csv"
    
    print(f"📁 Dataset: {csv_path}")
    print(f"📊 Dataset size: 2,200 samples")
    print(f"🎯 Target: 22 different crop types")
    print()
    
    # Training configuration
    training_config = {
        'test_size': 0.2,              # 20% for testing (440 samples)
        'perform_tuning': True,        # Enable hyperparameter optimization
        'save_model': True             # Save the trained model
    }
    
    print("⚙️ Training Configuration:")
    print(f"   • Test size: {training_config['test_size']*100}% (440 samples)")
    print(f"   • Training size: 80% (1,760 samples)")
    print(f"   • Hyperparameter tuning: {training_config['perform_tuning']}")
    print(f"   • Save model: {training_config['save_model']}")
    print()
    
    try:
        print("🚀 Starting training process...")
        print("   This may take 3-5 minutes depending on your hardware")
        print()
        
        # Train the model
        results = await xgb_service.train_model(
            csv_path=csv_path,
            **training_config
        )
        
        print("✅ Training completed successfully!")
        print("=" * 50)
        print()
        
        # Display results
        print("📈 Training Results:")
        if results and isinstance(results, dict):
            duration = results.get('training_duration_seconds', 0)
            print(f"   • Training duration: {duration:.1f} seconds")
            
            dataset_info = results.get('dataset_info', {})
            print(f"   • Dataset size: {dataset_info.get('dataset_size', 'N/A')} samples")
            print(f"   • Training samples: {dataset_info.get('training_samples', 'N/A')}")
            print(f"   • Test samples: {dataset_info.get('test_samples', 'N/A')}")
            print(f"   • Feature count: {dataset_info.get('feature_count', 'N/A')}")
            print(f"   • Crop classes: {dataset_info.get('crop_count', 'N/A')}")
            print()
            
            # Model performance
            accuracy_metrics = results.get('accuracy_metrics', {})
            if accuracy_metrics:
                print("🎯 Model Performance:")
                print(f"   • Test Accuracy: {accuracy_metrics.get('test_accuracy', 0):.3f}")
                print(f"   • Precision: {accuracy_metrics.get('precision', 0):.3f}")
                print(f"   • Recall: {accuracy_metrics.get('recall', 0):.3f}")
                print(f"   • F1-Score: {accuracy_metrics.get('f1_score', 0):.3f}")
                print()
        else:
            print("   • Training completed but no detailed results available")
            print()
        
        # Model info
        model_info = xgb_service.get_model_info()
        print("📋 Model Information:")
        print(f"   • Model type: {model_info['model_type']}")
        print(f"   • Version: {model_info['version']}")
        print(f"   • Is trained: {model_info['is_trained']}")
        print(f"   • Supported crops: {len(model_info.get('supported_crops', []))}")
        print(f"   • Device: {model_info['device_config']['current_device'].upper()}")
        print()
        
        print("🎉 Model is ready for predictions!")
        print("   You can now use the crop recommendation API endpoints.")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        print()
        print("🔍 Troubleshooting:")
        print("   • Check if the CSV file exists and is readable")
        print("   • Ensure sufficient memory (2-4GB RAM)")
        print("   • Verify all dependencies are installed")
        return False

if __name__ == "__main__":
    success = asyncio.run(train_model())
    if success:
        print("\n✅ Training script completed successfully!")
    else:
        print("\n❌ Training script failed!")
        sys.exit(1)