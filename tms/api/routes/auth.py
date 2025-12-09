"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from tms.infra.database import get_db
from tms.api.schemas.common import UserLogin, LoginResponse, UserResponse
from tms.application.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    """
    print(f"Login attempt for user: {credentials.username}")
    try:
        auth_service = AuthService(db)
        
        user = auth_service.authenticate_user(
            credentials.username,
            credentials.password
        )
        
        if not user:
            print(f"Authentication failed for user: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Generate simple token (username:user_id)
        # In production, use JWT
        access_token = f"{user.username}:{user.id}"
        
        print(f"Login successful for user: {credentials.username}")
        return LoginResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"❌ Login error: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout")
def logout():
    """
    Logout user (client should delete token)
    """
    return {"message": "Successfully logged out"}
