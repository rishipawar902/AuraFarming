# 🤖 XGBoost Model Training Instructions

## Prerequisites

### 1. **Install Dependencies**
```bash
cd backend
pip install xgboost==2.0.3 joblib==1.3.2 GPUtil matplotlib seaborn
```

### 2. **Prepare Your Dataset**
Download the **Kaggle Crop Recommendation Dataset** or prepare your own CSV file with the required format:

**Required CSV Format:**
```csv
N,P,K,temperature,humidity,ph,rainfall,label
90,42,43,20.87,82.00,6.50,202.93,rice
85,58,41,21.77,80.31,7.03,226.65,rice
60,55,44,23.00,82.32,7.84,263.96,rice
74,35,40,26.49,80.15,6.98,242.86,maize
78,42,42,20.13,81.60,7.62,262.71,chickpea
```

**Column Descriptions:**
- `N`: Nitrogen content in soil (0-140)
- `P`: Phosphorus content in soil (5-145) 
- `K`: Potassium content in soil (5-205)
- `temperature`: Temperature in Celsius (8-44°C)
- `humidity`: Relative humidity percentage (14-100%)
- `ph`: Soil pH value (3.5-10.0)
- `rainfall`: Rainfall in mm (20-300mm)
- `label`: Crop name (target variable)

## Training Methods

### 🌐 **Method 1: Web Interface (Recommended)**

#### Step 1: Start the Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 2: Login to Your Account
1. Open browser: `http://localhost:3000`
2. Login with your credentials
3. Navigate to the crop recommendation section

#### Step 3: Check Model Status
```bash
curl -X GET "http://localhost:8000/api/crops/xgboost/info" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Step 4: Upload and Train
1. **Prepare your CSV file** (ensure it matches the format above)
2. **Use the training endpoint**:

```bash
curl -X POST "http://localhost:8000/api/crops/xgboost/train" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@crop_recommendation.csv" \
  -F "test_size=0.2" \
  -F "validation_size=0.15" \
  -F "tune_hyperparameters=true" \
  -F "cross_validation_folds=5"
```

### 🖥️ **Method 2: Python Script**

Create a training script `train_model.py`:

```python
import asyncio
import pandas as pd
from app.services.xgboost_service import get_xgboost_service

async def train_model():
    # Get XGBoost service
    xgb_service = get_xgboost_service()
    
    # Path to your CSV file
    csv_path = "path/to/your/crop_recommendation.csv"
    
    print("Starting XGBoost model training...")
    
    # Train the model
    results = await xgb_service.train_model(
        csv_path=csv_path,
        test_size=0.2,           # 20% for testing
        validation_size=0.15,    # 15% for validation  
        tune_hyperparameters=True,  # Enable hyperparameter tuning
        cv_folds=5              # 5-fold cross-validation
    )
    
    print("Training completed!")
    print(f"Results: {results}")
    
    # Check model info
    model_info = xgb_service.get_model_info()
    print(f"Model Info: {model_info}")

if __name__ == "__main__":
    asyncio.run(train_model())
```

Run the script:
```bash
cd backend
python train_model.py
```

### ⚡ **Method 3: Direct API Testing**

#### Step 1: Get Authorization Token
```bash
# Login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email@example.com",
    "password": "your_password"
  }'
```

#### Step 2: Check Current Model Status
```bash
curl -X GET "http://localhost:8000/api/crops/xgboost/info" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Step 3: Train with Your Dataset
```bash
curl -X POST "http://localhost:8000/api/crops/xgboost/train" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/crop_recommendation.csv" \
  -F "training_params={
    \"test_size\": 0.2,
    \"validation_size\": 0.15,
    \"tune_hyperparameters\": true,
    \"cross_validation_folds\": 5
  }"
```

## Training Configuration Options

### **Basic Configuration**
```json
{
  "test_size": 0.2,              // 20% data for final testing
  "validation_size": 0.15,       // 15% data for validation
  "tune_hyperparameters": false, // Quick training without tuning
  "cross_validation_folds": 3    // Faster cross-validation
}
```

### **Advanced Configuration (Recommended)**
```json
{
  "test_size": 0.2,              // 20% data for final testing
  "validation_size": 0.15,       // 15% data for validation  
  "tune_hyperparameters": true,  // Enable hyperparameter optimization
  "cross_validation_folds": 5    // 5-fold cross-validation
}
```

### **Production Configuration**
```json
{
  "test_size": 0.15,             // 15% data for testing (more training data)
  "validation_size": 0.15,       // 15% data for validation
  "tune_hyperparameters": true,  // Full hyperparameter search
  "cross_validation_folds": 10   // 10-fold cross-validation
}
```

## Expected Training Process

### **Phase 1: Data Loading & Preprocessing** (30 seconds)
```
✓ Loading CSV dataset...
✓ Validating required columns...
✓ Cleaning and preprocessing data...
✓ Data shape: (2200, 8) -> 2200 samples, 8 features
```

### **Phase 2: Feature Engineering** (45 seconds)
```
✓ Creating climate indices...
✓ Engineering soil suitability features...
✓ Adding seasonal patterns...
✓ Integrating weather data...
✓ Total features: 25+ engineered features
```

### **Phase 3: Data Splitting** (10 seconds)
```
✓ Train set: 1540 samples (70%)
✓ Validation set: 330 samples (15%)
✓ Test set: 330 samples (15%)
✓ Feature scaling applied...
```

### **Phase 4: Hyperparameter Tuning** (2-5 minutes)
```
✓ Grid search with 5-fold cross-validation...
✓ Testing 162 parameter combinations...
✓ Best parameters found: {n_estimators: 500, max_depth: 8, ...}
✓ Best CV score: 0.9234
```

### **Phase 5: Model Training** (1-2 minutes)
```
✓ Training crop classifier...
✓ Training yield regressors for 22 crops...
✓ Training risk assessment classifier...
✓ Models trained successfully!
```

### **Phase 6: Model Evaluation** (30 seconds)
```
✓ Test accuracy: 92.4%
✓ Top-3 accuracy: 97.8%
✓ Top-5 accuracy: 99.1%
✓ Precision: 0.924, Recall: 0.924, F1: 0.924
```

### **Phase 7: Model Saving** (15 seconds)
```
✓ Saving trained models...
✓ Saving preprocessing components...
✓ Saving metadata and feature names...
✓ Model saved to: models/xgboost_model_20250915_143022
```

## Performance Expectations

### **Training Time**
- **CPU (8 cores)**: 5-8 minutes total
- **GPU (CUDA)**: 2-3 minutes total
- **Basic config**: 50% faster (no hyperparameter tuning)

### **Memory Requirements**
- **RAM**: 2-4GB during training
- **Storage**: 50-100MB for saved model
- **Dataset**: 1-10MB for CSV file

### **Accuracy Targets**
- **Top-1 Accuracy**: 85-95%
- **Top-3 Accuracy**: 95-99%
- **Cross-validation**: 90%+ consistency

## Troubleshooting

### **Common Issues**

#### ❌ **"CSV format incorrect"**
**Solution**: Ensure your CSV has exactly these columns:
```
N,P,K,temperature,humidity,ph,rainfall,label
```

#### ❌ **"Not enough training data"**
**Solution**: Ensure at least:
- 1000+ total samples
- 10+ samples per crop type
- Balanced distribution across crops

#### ❌ **"GPU not detected"**
**Solution**: Install CUDA drivers or train on CPU:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### ❌ **"Memory error during training"**
**Solution**: Reduce batch size or use smaller dataset:
```json
{
  "test_size": 0.3,
  "tune_hyperparameters": false
}
```

#### ❌ **"Authorization failed"**
**Solution**: Get fresh token:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "your_email", "password": "your_password"}'
```

### **Training Progress Monitoring**

Check training logs:
```bash
tail -f backend/logs/training.log
```

Monitor model status:
```bash
curl -X GET "http://localhost:8000/api/crops/xgboost/info" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## After Training

### **Test Your Model**
```bash
curl -X POST "http://localhost:8000/api/crops/xgboost/predict" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "N": 90, "P": 42, "K": 43,
    "temperature": 20.87, "humidity": 82.0,
    "ph": 6.5, "rainfall": 202.9,
    "location": "Jharkhand", "season": "kharif"
  }'
```

### **Expected Response**
```json
{
  "success": true,
  "message": "Crop recommendations generated successfully",
  "data": {
    "recommendations": [
      {
        "crop_name": "Rice",
        "confidence": 94.2,
        "expected_yield": 4.8,
        "risk_level": "Low",
        "reasons": ["XGBoost model confidence: 94.2%", "Expected yield: 4.8 tons/hectare"]
      },
      {
        "crop_name": "Maize", 
        "confidence": 87.1,
        "expected_yield": 5.2,
        "risk_level": "Medium"
      }
    ]
  }
}
```

## Success Checklist

- [ ] ✅ **Dependencies installed** (xgboost, joblib, etc.)
- [ ] ✅ **CSV dataset prepared** (correct format, sufficient data)
- [ ] ✅ **Backend server running** (port 8000)
- [ ] ✅ **Authentication working** (valid token obtained)
- [ ] ✅ **Training completed** (no errors in logs)
- [ ] ✅ **Model predictions working** (test prediction successful)
- [ ] ✅ **Model info accessible** (model metadata available)

Your XGBoost model is now ready for production use! 🎉

---

**Need help?** Check the logs in `backend/logs/` or contact support with your training configuration and error messages.