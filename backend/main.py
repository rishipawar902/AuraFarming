"""
Main FastAPI application entry point for AuraFarming SIH-2025 prototype.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.core.config import settings
from app.api.auth import auth_router
from app.api.farms import farms_router
from app.api.crops import crops_router
from app.api.weather import weather_router
from app.api.market import market_router
from app.api.finance import finance_router
from app.api.admin import admin_router
from app.api.sustainability import sustainability_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AuraFarming API",
    description="SIH-2025: AI-Based Crop Recommendation System for Jharkhand",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(farms_router, prefix="/api/v1/farms", tags=["Farm Management"])
app.include_router(crops_router, prefix="/api/v1/crops", tags=["Crop Recommendations"])
app.include_router(weather_router, prefix="/api/v1/weather", tags=["Weather Services"])
app.include_router(market_router, prefix="/api/v1/market", tags=["Market Data"])
app.include_router(finance_router, prefix="/api/v1/finance", tags=["Financial Services"])
app.include_router(sustainability_router, prefix="/api/v1/sustainability", tags=["Sustainability"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin Dashboard"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "message": "AuraFarming API is running",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "AuraFarming API - SIH 2025 Prototype",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url),
            "debug_info": str(exc) if settings.DEBUG else "Error details hidden"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )