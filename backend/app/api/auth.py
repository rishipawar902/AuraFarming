"""
Authentication API routes.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import (
    FarmerRegister, FarmerLogin, TokenResponse, APIResponse
)
from app.core.security import (
    create_farmer_token, get_password_hash, verify_password, get_current_user
)
from app.services.database import DatabaseService
import uuid

auth_router = APIRouter()


@auth_router.post("/register", response_model=TokenResponse)
async def register_farmer(farmer_data: FarmerRegister):
    """
    Register a new farmer.
    
    Args:
        farmer_data: Farmer registration data
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If phone number already exists
    """
    # For demo purposes, create a mock farmer without database
    farmer_id = str(uuid.uuid4())
    
    # Create access token
    access_token = create_farmer_token(farmer_id, farmer_data.phone)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400  # 24 hours
    )


@auth_router.post("/login", response_model=TokenResponse)
async def login_farmer(login_data: FarmerLogin):
    """
    Authenticate farmer and return access token.
    
    Args:
        login_data: Farmer login credentials
        
    Returns:
        JWT access token
        
    Note:
        For demo purposes, accepts any valid phone/password combination
    """
    # For demo purposes, create a mock farmer login
    # In production, this would verify against database
    farmer_id = str(uuid.uuid4())
    
    # Create access token
    access_token = create_farmer_token(farmer_id, login_data.phone)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400  # 24 hours
    )


@auth_router.get("/me")
async def get_current_farmer(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated farmer's profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Farmer profile data
    """
    # For demo purposes, return mock farmer data
    farmer_data = {
        "id": current_user.get("user_id"),
        "name": "Demo Farmer",
        "phone": current_user.get("phone"),
        "language": "english",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    return APIResponse(
        success=True,
        message="Farmer profile retrieved successfully",
        data=farmer_data
    )


@auth_router.post("/logout")
async def logout_farmer(current_user: dict = Depends(get_current_user)):
    """
    Logout farmer (client-side token removal).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    return APIResponse(
        success=True,
        message="Logged out successfully"
    )