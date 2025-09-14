"""
Simple test server for AuraFarming API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="AuraFarming API - Test Server",
    description="SIH-2025: AI-Based Crop Recommendation System for Jharkhand",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LoginRequest(BaseModel):
    phone_number: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    phone_number: str
    password: str
    district: str
    village: str
    age: int
    farming_experience: int

class UserResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    district: str
    village: str

class FarmProfile(BaseModel):
    total_area: float
    district: str
    village: str
    soil_type: str
    irrigation_source: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# Mock data
mock_users = [
    {
        "id": 1,
        "name": "Demo Farmer",
        "phone_number": "9876543210",
        "password": "farmer123",  # In real app, this would be hashed
        "district": "Ranchi",
        "village": "Demo Village",
        "age": 35,
        "farming_experience": 10
    }
]

mock_farms = []

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AuraFarming API Test Server",
        "status": "running",
        "version": "1.0.0"
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-09-13T14:30:00Z"}

# Auth endpoints
@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    user = next((u for u in mock_users if u["phone_number"] == request.phone_number), None)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "access_token": "mock_jwt_token_" + user["phone_number"],
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "phone_number": user["phone_number"],
            "district": user["district"],
            "village": user["village"]
        }
    }

@app.post("/api/v1/auth/register")
async def register(request: RegisterRequest):
    # Check if user already exists
    if any(u["phone_number"] == request.phone_number for u in mock_users):
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    new_user = {
        "id": len(mock_users) + 1,
        "name": request.name,
        "phone_number": request.phone_number,
        "password": request.password,  # In real app, this would be hashed
        "district": request.district,
        "village": request.village,
        "age": request.age,
        "farming_experience": request.farming_experience
    }
    mock_users.append(new_user)
    
    return {
        "access_token": "mock_jwt_token_" + new_user["phone_number"],
        "token_type": "bearer",
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "phone_number": new_user["phone_number"],
            "district": new_user["district"],
            "village": new_user["village"]
        }
    }

@app.get("/api/v1/auth/me")
async def get_current_user():
    # Mock user response
    return {
        "user": {
            "id": 1,
            "name": "Demo Farmer",
            "phone_number": "9876543210",
            "district": "Ranchi",
            "village": "Demo Village"
        }
    }

# Farm endpoints
@app.post("/api/v1/farms/profile")
async def create_farm_profile(profile: FarmProfile):
    farm = {
        "id": len(mock_farms) + 1,
        "farmer_id": 1,
        **profile.dict()
    }
    mock_farms.append(farm)
    return {"message": "Farm profile created successfully", "farm": farm}

@app.get("/api/v1/farms/profile")
async def get_farm_profile():
    if mock_farms:
        return mock_farms[0]
    return None

# Weather endpoint
@app.get("/api/v1/weather/current/{farm_id}")
async def get_current_weather(farm_id: int):
    return {
        "temperature": 28.5,
        "humidity": 75,
        "condition": "Partly Cloudy",
        "wind_speed": 12,
        "rainfall": 0,
        "alerts": []
    }

# Crop recommendations
@app.post("/api/v1/crops/recommend")
async def get_crop_recommendations(request: dict):
    return {
        "recommendations": [
            {
                "crop": "Rice",
                "confidence": 0.92,
                "expected_yield": 4.2,
                "profit_margin": 15000,
                "season": "Kharif",
                "reasons": [
                    "Suitable soil type for rice cultivation",
                    "Optimal rainfall expected",
                    "High market demand in your area"
                ]
            },
            {
                "crop": "Maize",
                "confidence": 0.87,
                "expected_yield": 5.1,
                "profit_margin": 12000,
                "season": "Kharif",
                "reasons": [
                    "Good soil drainage",
                    "Favorable weather conditions",
                    "Growing market prices"
                ]
            }
        ]
    }

# Market prices
@app.get("/api/v1/market/prices/{district}")
async def get_market_prices(district: str):
    return {
        "prices": [
            {"crop": "Rice", "price": 2100, "unit": "quintal", "market": "Ranchi Mandi"},
            {"crop": "Wheat", "price": 2250, "unit": "quintal", "market": "Ranchi Mandi"},
            {"crop": "Maize", "price": 1800, "unit": "quintal", "market": "Ranchi Mandi"}
        ],
        "last_updated": "2025-09-13T10:30:00Z"
    }

# Admin stats
@app.get("/api/v1/admin/stats")
async def get_admin_stats():
    return {
        "total_farmers": 15420,
        "active_farms": 12350,
        "total_recommendations": 45600,
        "avg_yield_increase": 18.5
    }

if __name__ == "__main__":
    uvicorn.run("test_server:app", host="0.0.0.0", port=8000, reload=True)