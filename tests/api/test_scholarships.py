# tests/api/test_scholarships.py
import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.db.models.scholarship import Scholarship


def test_create_scholarship(authorized_client: TestClient, db, test_user):
    """Test creating a new scholarship."""
    data = {
        "title": "Test Scholarship",
        "description": "This is a test scholarship",
        "amount": 5000.0,
        "deadline": str(date.today()),
        "eligibility_criteria": "Open to all test users",
        "provider": "Test University",
        "country": "Test Country",
        "education_level": "Undergraduate"
    }
    response = authorized_client.post(
        f"{settings.API_V1_STR}/scholarships/", 
        json=data
    )
    assert response.status_code == 201
    assert response.json()["title"] == data["title"]
    assert "id" in response.json()


def test_get_scholarships(client: TestClient, db, test_user):
    """Test getting all scholarships."""
    # Add test scholarship
    scholarship = Scholarship(
        title="Test Scholarship",
        description="This is a test scholarship",
        amount=5000.0,
        deadline=date.today(),
        eligibility_criteria="Open to all test users",
        provider="Test University",
        country="Test Country",
        education_level="Undergraduate",
        user_id=test_user.id
    )
    db.add(scholarship)
    db.commit()
    db.refresh(scholarship)
    
    # Get scholarships
    response = client.get(f"{settings.API_V1_STR}/scholarships/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    
    # Clean up
    db.delete(scholarship)
    db.commit()


def test_get_scholarship_by_id(client: TestClient, db, test_user):
    """Test getting a scholarship by ID."""
    # Add test scholarship
    scholarship = Scholarship(
        title="Test Scholarship",
        description="This is a test scholarship",
        amount=5000.0,
        deadline=date.today(),
        eligibility_criteria="Open to all test users",
        provider="Test University",
        country="Test Country",
        education_level="Undergraduate",
        user_id=test_user.id
    )
    db.add(scholarship)
    db.commit()
    db.refresh(scholarship)
    
    # Get scholarship by ID
    response = client.get(f"{settings.API_V1_STR}/scholarships/{scholarship.id}")
    assert response.status_code == 200
    assert response.json()["id"] == scholarship.id
    assert response.json()["title"] == scholarship.title
    
    # Clean up
    db.delete(scholarship)
    db.commit()


def test_update_scholarship(authorized_client: TestClient, db, test_user):
    """Test updating a scholarship."""
    # Add test scholarship
    scholarship = Scholarship(
        title="Test Scholarship",
        description="This is a test scholarship",
        amount=5000.0,
        deadline=date.today(),
        eligibility_criteria="Open to all test users",
        provider="Test University",
        country="Test Country",
        education_level="Undergraduate",
        user_id=test_user.id
    )
    db.add(scholarship)
    db.commit()
    db.refresh(scholarship)
    
    # Update scholarship
    update_data = {
        "title": "Updated Test Scholarship",
        "amount": 6000.0
    }
    response = authorized_client.put(
        f"{settings.API_V1_STR}/scholarships/{scholarship.id}", 
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]
    assert response.json()["amount"] == update_data["amount"]
    
    # Clean up
    db.delete(scholarship)
    db.commit()


def test_delete_scholarship(authorized_client: TestClient, db, test_user):
    """Test deleting a scholarship."""
    # Add test scholarship
    scholarship = Scholarship(
        title="Test Scholarship",
        description="This is a test scholarship",
        amount=5000.0,
        deadline=date.today(),
        eligibility_criteria="Open to all test users",
        provider="Test University",
        country="Test Country",
        education_level="Undergraduate",
        user_id=test_user.id
    )
    db.add(scholarship)
    db.commit()
    db.refresh(scholarship)
    
    # Delete scholarship
    response = authorized_client.delete(f"{settings.API_V1_STR}/scholarships/{scholarship.id}")
    assert response.status_code == 204
    
    # Check if scholarship is deleted
    deleted_scholarship = db.query(Scholarship).filter(Scholarship.id == scholarship.id).first()
    assert deleted_scholarship is None