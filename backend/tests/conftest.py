import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Generator

from app.infrastructure.db.session import Base
from app.presentation.dependencies import get_db
from app.main import app
from app.domain.models import user, task

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test.
    """
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clear the database after each test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with a dependency override to use the test database.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear dependency overrides after test
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(client, db):
    """
    Create a test user in the database.
    """
    from app.security import get_password_hash
    from app.domain.models.user import User

    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": get_password_hash("password"),
        "is_active": True,
        "role": "user"
    }
    
    user_obj = User(**user_data)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    
    return user_obj

@pytest.fixture(scope="function")
def token_headers(client, test_user):
    """
    Create authentication headers with a valid token.
    """
    login_data = {
        "username": "testuser",
        "password": "password"
    }
    response = client.post("/api/v1/auth/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"} 