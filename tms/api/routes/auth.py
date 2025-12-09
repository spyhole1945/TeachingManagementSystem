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
    auth_service = AuthService(db)
    
    user = auth_service.authenticate_user(
        credentials.username,
        credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Generate simple token (username:user_id)
    # In production, use JWT
    access_token = f"{user.username}:{user.id}"
    
    return LoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
def logout():
    """
    Logout user (client should delete token)
    """
    return {"message": "Successfully logged out"}
