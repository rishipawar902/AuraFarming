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
    db = DatabaseService()
    
    # Check if farmer already exists
    existing_farmer = await db.get_farmer_by_phone(farmer_data.phone)
    if existing_farmer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(farmer_data.password)
    
    # Create farmer
    farmer_id = str(uuid.uuid4())
    farmer = await db.create_farmer({
        "id": farmer_id,
        "name": farmer_data.name,
        "phone": farmer_data.phone,
        "password": hashed_password,
        "language": farmer_data.language
    })
    
    # Create access token
    access_token = create_farmer_token(farmer_id, farmer_data.phone)
    
    return TokenResponse(
        access_token=access_token,
        expires_in=24 * 3600  # 24 hours in seconds
    )


@auth_router.post("/login", response_model=TokenResponse)
async def login_farmer(login_data: FarmerLogin):
    """
    Authenticate farmer and return access token.
    
    Args:
        login_data: Farmer login credentials
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    db = DatabaseService()
    
    # Get farmer by phone
    farmer = await db.get_farmer_by_phone(login_data.phone)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, farmer["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )
    
    # Create access token
    access_token = create_farmer_token(farmer["id"], farmer["phone"])
    
    return TokenResponse(
        access_token=access_token,
        expires_in=24 * 3600  # 24 hours in seconds
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
    db = DatabaseService()
    farmer = await db.get_farmer_by_id(current_user["user_id"])
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Remove password from response
    farmer_data = {k: v for k, v in farmer.items() if k != "password"}
    
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