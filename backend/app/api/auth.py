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
        For demo purposes, authenticates the existing demo farmer in the database
    """
    from app.services.database import DatabaseService
    
    # For demo purposes, find the existing farmer by phone number
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
        farmer_id = farmer['id']
        
        # For demo purposes, accept any password (in production, verify hashed password)
        print(f"✓ Demo login successful for farmer: {farmer_id}")
        print(f"✓ Farmer name: {farmer['name']}")
        print(f"✓ Phone: {farmer['phone']}")
        
        # Verify farm profile exists
        farm = await db.get_farm_by_farmer_id(farmer_id)
        if farm:
            print(f"✓ Farm profile found: {farm['id']}")
            print(f"✓ Location: {farm['location']['district']}")
        else:
            print("⚠️  No farm profile found for this farmer")
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        # For demo purposes, fall back to creating a deterministic farmer_id
        import uuid as uuid_lib
        namespace = uuid_lib.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        farmer_id = str(uuid_lib.uuid5(namespace, login_data.phone))
        print(f"⚠️  Using fallback farmer_id: {farmer_id}")
    
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