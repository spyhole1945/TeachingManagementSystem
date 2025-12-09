"""
Pytest configuration and fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from tms.infra.database import Base
from tms.infra.models import UserRole
from tms.api.main import app
from tms.application.services.auth_service import AuthService


# Test database - use in-memory SQLite
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    from tms.infra import database
    database.get_db = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_admin_user(db_session):
    """Create a test admin user"""
    auth_service = AuthService(db_session)
    user = auth_service.create_user(
        username="test_admin",
        email="admin@test.com",
        password="admin123",
        full_name="Test Admin",
        role=UserRole.ADMIN
    )
    return user


@pytest.fixture(scope="function")
def auth_headers(test_admin_user):
    """Get authentication headers for test admin"""
    token = f"{test_admin_user.username}:{test_admin_user.id}"
    return {"Authorization": f"Bearer {token}"}
