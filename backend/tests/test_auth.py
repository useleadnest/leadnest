import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

def test_register_user(client, test_data):
    """Test user registration with trial setup"""
    user_data = test_data["mock_users"][0]
    response = client.post("/auth/register", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["subscription_status"] == "trial"
    assert data["trial_ends_at"] is not None

def test_register_duplicate_email(client, test_data):
    """Test registration with duplicate email"""
    user_data = test_data["mock_users"][0]
    
    # Register first time
    client.post("/auth/register", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    # Try to register again
    response = client.post("/auth/register", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success(client, test_data):
    """Test successful login"""
    user_data = test_data["mock_users"][0]
    
    # Register user first
    client.post("/auth/register", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    # Login
    response = client.post("/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, test_data):
    """Test login with invalid credentials"""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_get_current_user(client, test_data):
    """Test getting current user info"""
    user_data = test_data["mock_users"][0]
    
    # Register user
    client.post("/auth/register", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]

def test_trial_expiration_logic(client, test_data, db_session):
    """Test trial expiration behavior"""
    from database import User
    from auth import get_password_hash
    
    # Create user with expired trial
    expired_user = User(
        email="expired@test.com",
        hashed_password=get_password_hash("password"),
        trial_ends_at=datetime.utcnow() - timedelta(days=1),
        subscription_status="trial"
    )
    db_session.add(expired_user)
    db_session.commit()
    
    # Login
    login_response = client.post("/auth/login", json={
        "email": "expired@test.com",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    
    # Try to create search (should fail)
    response = client.post("/searches", 
        json={"location": "Austin, TX", "trade": "roofing"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 402
    assert "Trial expired" in response.json()["detail"]
