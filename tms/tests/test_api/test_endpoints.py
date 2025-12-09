"""
Test API endpoints
"""
import pytest


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_login_success(client, test_admin_user):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        json={
            "username": "test_admin",
            "password": "admin123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["username"] == "test_admin"


def test_login_failure(client):
    """Test failed login with wrong credentials"""
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401


def test_list_courses_unauthorized(client):
    """Test that listing courses without auth fails"""
    response = client.get("/courses/")
    # Actually should succeed for listing, but let's test authentication for create
    response = client.post(
        "/courses/",
        json={
            "course_code": "TEST101",
            "name": "Test Course",
            "teacher_id": 1,
            "credits": 3.0,
            "capacity": 30,
            "semester": "2024 Spring"
        }
    )
    assert response.status_code == 401
