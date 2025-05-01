# tests/api/test_auth.py
import pytest
from fastapi.testclient import TestClient


def test_register_new_user(client: TestClient):
    """Test registering a new user."""
    data = {
        "email": "newuser@example.com",
        "password": "password123",
        "first_name": "New",
        "last_name": "User"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    assert response.status_code == 201
    assert response.json()["email"] == data["email"]
    assert "id" in response.json()


def test_register_existing_user(client: TestClient, test_user):
    """Test registering with an existing email."""
    data = {
        "email": test_user.email,
        "password": "password123",
        "first_name": "Existing",
        "last_name": "User"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_login_correct_credentials(client: TestClient, test_user):
    """Test login with correct credentials."""
    data = {
        "username": test_user.email,
        "password": "password"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient, test_user):
    """Test login with incorrect password."""
    data = {
        "username": test_user.email,
        "password": "wrongpassword"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_verify_email(client: TestClient, db, test_user):
    """Test email verification."""
    # Create a verification token
    from app.crud.verification import verification as verification_crud
    verification = verification_crud.create_email_verification(db, user_id=test_user.id)
    
    response = client.post(f"{settings.API_V1_STR}/auth/verify-email/{verification.token}")
    assert response.status_code == 200
    assert response.json()["is_verified"] == True