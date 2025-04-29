# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models.user import User

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test database engine
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after tests
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    
    # Clear dependency override
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def test_user(db):
    # Create test user
    user_in_db = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True,
    )
    db.add(user_in_db)
    db.commit()
    db.refresh(user_in_db)
    
    # Return test user
    yield user_in_db
    
    # Clean up
    db.delete(user_in_db)
    db.commit()


@pytest.fixture(scope="module")
def test_user_token(client, test_user):
    # Get token for test user
    login_data = {
        "username": test_user.email,
        "password": "password",
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    token = response.json()["access_token"]
    return token


@pytest.fixture(scope="module")
def authorized_client(client, test_user_token):
    # Create a copy of the client
    authorized_client = TestClient(app)
    # Set authorization header
    authorized_client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_user_token}"
    }
    return authorized_client