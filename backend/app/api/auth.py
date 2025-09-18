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
    try:
        db = DatabaseService()
        
        # Check if phone number already exists
        existing_farmer = db.supabase.table("farmers").select("id").eq("phone", farmer_data.phone).execute()
        if existing_farmer.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Hash the password
        hashed_password = get_password_hash(farmer_data.password)
        
        # Insert new farmer into database
        farmer_result = db.supabase.table("farmers").insert({
            "name": farmer_data.name,
            "phone": farmer_data.phone,
            "password": hashed_password,
            "language": farmer_data.language  # Now it's a string directly
        }).execute()
        
        if not farmer_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create farmer account"
            )
        
        farmer_id = farmer_result.data[0]['id']
        
        # Create access token
        access_token = create_farmer_token(farmer_id, farmer_data.phone)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400  # 24 hours
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
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
    try:
        db = DatabaseService()
        
        # Find farmer by phone number
        result = db.supabase.table("farmers").select("*").eq("phone", login_data.phone).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number or password"
            )
        
        farmer = result.data[0]
        
        # Verify password
        if not verify_password(login_data.password, farmer['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number or password"
            )
        
        farmer_id = farmer['id']
        
        # Create access token
        access_token = create_farmer_token(farmer_id, farmer['phone'])
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400  # 24 hours
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@auth_router.get("/me")
async def get_current_farmer(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated farmer's profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Farmer profile data including farm information
    """
    try:
        db = DatabaseService()
        farmer_id = current_user.get("user_id")
        
        # Get farmer details
        farmer_result = db.supabase.table("farmers").select("*").eq("id", farmer_id).execute()
        
        if not farmer_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer not found"
            )
        
        farmer = farmer_result.data[0]
        
        # Get farm details for this farmer
        farm = await db.get_farm_by_farmer_id(farmer_id)
        
        farmer_data = {
            "id": farmer["id"],
            "name": farmer["name"],
            "phone": farmer["phone"],
            "language": farmer["language"],
            "created_at": farmer["created_at"],
            "farm": farm  # Include farm data if available
        }
        
        return APIResponse(
            success=True,
            message="Farmer profile retrieved successfully",
            data=farmer_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve farmer profile: {str(e)}"
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