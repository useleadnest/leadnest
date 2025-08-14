import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
import json
from datetime import datetime, timedelta

# Set test environment
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENVIRONMENT"] = "test"

from database import Base, get_db
from main import app
from auth import create_access_token

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_data():
    with open("tests/fixtures/test_data.json", "r") as f:
        return json.load(f)

@pytest.fixture
def auth_headers():
    access_token = create_access_token(data={"sub": "john@roofingpro.com"})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_headers():
    access_token = create_access_token(data={"sub": "admin@leadnest.com"})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["YELP_API_KEY"] = "test-yelp-key"
    yield
    # Cleanup after test
