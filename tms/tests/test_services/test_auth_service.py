"""
Test authentication service
"""
import pytest
from tms.infra.models import UserRole
from tms.application.services.auth_service import AuthService


def test_create_user(db_session):
    """Test creating a new user"""
    auth_service = AuthService(db_session)
    
    user = auth_service.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
        full_name="Test User",
        role=UserRole.STUDENT
    )
    
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == UserRole.STUDENT
    assert user.is_active is True


def test_duplicate_username(db_session):
    """Test that duplicate usernames are rejected"""
    auth_service = AuthService(db_session)
    
    # Create first user
    auth_service.create_user(
        username="testuser",
        email="test1@example.com",
        password="password123",
        full_name="Test User 1",
        role=UserRole.STUDENT
    )
    
    # Try to create second user with same username
    user2 = auth_service.create_user(
        username="testuser",
        email="test2@example.com",
        password="password123",
        full_name="Test User 2",
        role=UserRole.STUDENT
    )
    
    assert user2 is None


def test_authenticate_user(db_session):
    """Test user authentication"""
    auth_service = AuthService(db_session)
    
    # Create user
    auth_service.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
        full_name="Test User",
        role=UserRole.STUDENT
    )
    
    # Authenticate with correct credentials
    user = auth_service.authenticate_user("testuser", "password123")
    assert user is not None
    assert user.username == "testuser"
    
    # Authenticate with wrong password
    user = auth_service.authenticate_user("testuser", "wrongpassword")
    assert user is None


def test_change_password(db_session):
    """Test changing user password"""
    auth_service = AuthService(db_session)
    
    # Create user
    user = auth_service.create_user(
        username="testuser",
        email="test@example.com",
        password="oldpassword",
        full_name="Test User",
        role=UserRole.STUDENT
    )
    
    # Change password
    success = auth_service.change_password(
        user.id,
        "oldpassword",
        "newpassword"
    )
    assert success is True
    
    # Verify old password doesn't work
    auth_user = auth_service.authenticate_user("testuser", "oldpassword")
    assert auth_user is None
    
    # Verify new password works
    auth_user = auth_service.authenticate_user("testuser", "newpassword")
    assert auth_user is not None
