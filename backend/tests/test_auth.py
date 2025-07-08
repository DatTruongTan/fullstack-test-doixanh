import pytest
from fastapi import status
from app.security import get_password_hash
from app.domain.models.user import User

def test_register_user(client, db):
    """
    Test user registration process.
    """
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "password123",
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    
    # Check database
    created_user = db.query(User).filter(User.username == user_data["username"]).first()
    assert created_user is not None
    assert created_user.email == user_data["email"]
    
def test_register_user_duplicate_email(client, test_user):
    """
    Test registration with duplicate email.
    """
    user_data = {
        "email": "test@example.com",  # Same email as test_user
        "username": "newusername",
        "password": "password123",
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
def test_register_user_duplicate_username(client, test_user):
    """
    Test registration with duplicate username.
    """
    user_data = {
        "email": "another@example.com",
        "username": "testuser",  # Same username as test_user
        "password": "password123",
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
def test_token_successful_login(client, test_user):
    """
    Test successful login and token issuance.
    """
    login_data = {
        "username": "testuser",
        "password": "password"
    }
    
    response = client.post("/api/v1/auth/token", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
def test_token_incorrect_password(client, test_user):
    """
    Test login with incorrect password.
    """
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
def test_token_nonexistent_user(client):
    """
    Test login with non-existent user.
    """
    login_data = {
        "username": "nonexistentuser",
        "password": "password"
    }
    
    response = client.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 