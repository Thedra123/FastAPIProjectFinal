import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from main import app







# --- Test database setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)

# --- Override dependency ---
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- Fixtures ---
@pytest.fixture
def register_user():
    payload = {
        "email": "test@example.com",
        "password": "secret123",
        "role": "user"
    }
    response = client.post("/api/auth/register", json=payload)
    return response

@pytest.fixture
def login_user():
    payload = {
        "email": "test@example.com",
        "password": "secret123"
    }
    response = client.post("/api/auth/login", json=payload)
    return response


# --- Tests ---
def test_register_user_success():
    payload = {
        "email": "test@example.com",
        "password": "secret123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data


def test_register_duplicate_email():
    payload = {
        "email": "dup@example.com",
        "password": "abc123"
    }
    res1 = client.post("/api/auth/register", json=payload)
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Email already registered"


def test_login_success(register_user):
    payload = {
        "email": "test@example.com",
        "password": "secret123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(register_user):
    payload = {
        "email": "test@example.com",
        "password": "wrongpass"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_me_endpoint(login_user):
    token = login_user.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


def test_me_unauthorized():
    response = client.get("/api/auth/me")
    assert response.status_code == 401
