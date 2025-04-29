# tests/api/test_users.py
import pytest
from fastapi.testclient import TestClient


def test_read_current_user(authorized_client: TestClient, test_user):
    """Test getting current user."""
    response = authorized_client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
    assert response.json()["id"] == test_user.id


def test_update_current_user(authorized_client: TestClient, test_user):
    """Test updating current user."""
    data = {
        "first_name": "Updated",
        "last_name": "User"
    }
    response = authorized_client.put(f"{settings.API_V1_STR}/users/me", json=data)
    assert response.status_code == 200
    assert response.json()["first_name"] == data["first_name"]
    assert response.json()["last_name"] == data["last_name"]
    assert response.json()["email"] == test_user.email


def test_read_user_unauthorized(client: TestClient):
    """Test accessing user endpoint without authorization."""
    response = client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]