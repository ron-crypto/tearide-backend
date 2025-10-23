import pytest
from fastapi.testclient import TestClient
from app.schemas.user import UserRegister

def test_register_user(client: TestClient):
    """Test user registration."""
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "password": "password123",
        "role": "passenger"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data

def test_login_user(client: TestClient):
    """Test user login."""
    # First register a user
    user_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": "+1234567891",
        "password": "password123",
        "role": "passenger"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Then login
    login_data = {
        "email": "jane@example.com",
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data

def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

