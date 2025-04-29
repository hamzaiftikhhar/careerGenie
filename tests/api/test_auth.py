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
    response = client.post("/api/v1/auth/register", json=data)
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
    response = client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_login_correct_credentials(client: TestClient, test_user):
    """Test login with correct credentials."""
    data = {
        "username": test_user.email,
        "password": "password"
    }
    response = client.post("/api/v1/auth/login", data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient, test_user):
    """Test login with incorrect password."""
    data = {
        "username": test_user.email,
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", data=data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client: TestClient):
    """Test login with nonexistent user."""
    data = {
        "username": "nonexistent@example.com",
        "password": "password"
    }
    response = client.post("/api/v1/auth/login", data=data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]