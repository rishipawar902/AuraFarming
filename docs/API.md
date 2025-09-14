# AuraFarming API Documentation

## Overview

AuraFarming provides a RESTful API built with FastAPI for agricultural data management and machine learning services.

**Base URL:** `http://localhost:8000/api/v1`

**Authentication:** JWT Bearer Token

## Authentication

### Register Farmer

```http
POST /auth/register
Content-Type: application/json

{
  "phone": "string",
  "password": "string",
  "name": "string",
  "district": "string"
}
```

**Response:**
```json
{
  "message": "Registration successful",
  "farmer_id": "uuid"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "phone": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "farmer": {
    "id": "uuid",
    "name": "string",
    "phone": "string",
    "district": "string"
  }
}
```

### Get Current User

```http
GET /auth/me
Authorization: Bearer {token}
```

## Machine Learning

### Get Crop Recommendations

```http
POST /crops/ml/recommend
Content-Type: application/json
Authorization: Bearer {token}

{
  "district": "Ranchi",
  "season": "Kharif",
  "soil_type": "Loamy Soil",
  "soil_ph": 6.5,
  "irrigation_type": "Drip irrigation",
  "field_size": 2.0,
  "rainfall": 1200,
  "temperature": 28,
  "nitrogen": 300,
  "humidity": 70
}
```

**Response:**
```json
[
  {
    "crop": "Rice",
    "confidence": 0.85,
    "expected_yield": 4.2,
    "suitability_score": 0.92,
    "profit_estimate": 45000
  },
  {
    "crop": "Wheat",
    "confidence": 0.78,
    "expected_yield": 3.8,
    "suitability_score": 0.88,
    "profit_estimate": 38000
  }
]
```

### Get ML Model Information

```http
GET /crops/ml/model-info
Authorization: Bearer {token}
```

**Response:**
```json
{
  "model_type": "RandomForestClassifier",
  "accuracy": 0.72,
  "training_samples": 2000,
  "features": [
    "soil_type_encoded",
    "soil_ph",
    "rainfall",
    "temperature",
    "nitrogen",
    "field_size"
  ],
  "target_classes": [
    "Rice", "Wheat", "Maize", "Sugarcane", 
    "Cotton", "Jute", "Pulses"
  ],
  "last_trained": "2025-09-14T12:00:00Z"
}
```

## Farm Management

### Get User Farms

```http
GET /farms
Authorization: Bearer {token}
```

**Response:**
```json
{
  "farms": [
    {
      "id": "uuid",
      "name": "Main Farm",
      "location": "Ranchi, Jharkhand",
      "size": 2.5,
      "soil_type": "Loamy",
      "crops": ["Rice", "Wheat"]
    }
  ]
}
```

### Create New Farm

```http
POST /farms
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "string",
  "location": "string",
  "size": 2.5,
  "soil_type": "string"
}
```

### Get Farm Details

```http
GET /farms/{farm_id}
Authorization: Bearer {token}
```

## Weather Services

### Get Current Weather

```http
GET /weather/current?location=Ranchi
Authorization: Bearer {token}
```

**Response:**
```json
{
  "location": "Ranchi",
  "temperature": 28.5,
  "humidity": 75,
  "rainfall": 0,
  "wind_speed": 12,
  "description": "Partly cloudy"
}
```

### Get Weather Forecast

```http
GET /weather/forecast?location=Ranchi&days=7
Authorization: Bearer {token}
```

## Market Data

### Get Mandi Prices

```http
GET /market/prices?crop=Rice&district=Ranchi
Authorization: Bearer {token}
```

**Response:**
```json
{
  "crop": "Rice",
  "district": "Ranchi",
  "current_price": 2800,
  "price_trend": "increasing",
  "last_updated": "2025-09-14T10:00:00Z"
}
```

## Admin Analytics

### Get Dashboard Statistics

```http
GET /admin/dashboard
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "total_farmers": 1250,
  "total_farms": 2100,
  "recommendations_generated": 5600,
  "ml_model_accuracy": 0.72,
  "district_stats": {
    "Ranchi": {
      "farmers": 300,
      "farms": 450
    }
  }
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- **General API**: 100 requests per minute per IP
- **ML Endpoints**: 10 requests per minute per user
- **Auth Endpoints**: 5 requests per minute per IP

## SDK Examples

### Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"phone": "9876543210", "password": "password"}
)
token = response.json()["access_token"]

# Get recommendations
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/api/v1/crops/ml/recommend",
    json={
        "district": "Ranchi",
        "soil_type": "Loamy Soil",
        "soil_ph": 6.5,
        "rainfall": 1200,
        "temperature": 28,
        "nitrogen": 300,
        "field_size": 2.0,
        "humidity": 70
    },
    headers=headers
)
recommendations = response.json()
```

### JavaScript

```javascript
// Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '9876543210',
    password: 'password'
  })
});
const { access_token } = await loginResponse.json();

// Get recommendations
const response = await fetch('/api/v1/crops/ml/recommend', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    district: 'Ranchi',
    soil_type: 'Loamy Soil',
    soil_ph: 6.5,
    rainfall: 1200,
    temperature: 28,
    nitrogen: 300,
    field_size: 2.0,
    humidity: 70
  })
});
const recommendations = await response.json();
```

## Testing

The API includes comprehensive test coverage. Run tests with:

```bash
cd backend
python -m pytest tests/ -v
```

For interactive API testing, visit `http://localhost:8000/docs` when the server is running.