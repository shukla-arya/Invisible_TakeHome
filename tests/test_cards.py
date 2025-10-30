"""
Unit and integration testing for card information.
"""

# Imports
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base, User, Account
from app.database.create_database import get_db
from app.routes.auth_helpers import get_current_user

# ------------------
# Test DB setup
# ------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_bank.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Override dependencies
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(id=1, name="Test User", email="test@example.com", hashed_password="fakehashed")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

# ------------------
# Fixtures
# ------------------
@pytest.fixture
def create_test_account():
    db = TestingSessionLocal()
    account = Account(user_id=1, account_type="checking", balance=500)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

# ------------------
# Tests
# ------------------
def test_create_card(create_test_account):
    payload = {
        "account_id": create_test_account.id,
        "expiry_date": "12/30",
        "cvv": "123"
    }
    response = client.post("/cards/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == create_test_account.id
    assert data["is_active"] is True
    assert "card_number" in data

def test_list_cards(create_test_account):
    # Ensure at least one card exists
    client.post("/cards/", json={
        "account_id": create_test_account.id,
        "expiry_date": "12/30",
        "cvv": "123"
    })
    response = client.get("/cards/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_activate_deactivate_card(create_test_account):
    card_resp = client.post("/cards/", json={
        "account_id": create_test_account.id,
        "expiry_date": "12/30",
        "cvv": "123"
    })
    card_id = card_resp.json()["id"]

    # Deactivate
    response = client.patch(f"/cards/{card_id}/deactivate")
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Activate
    response = client.patch(f"/cards/{card_id}/activate")
    assert response.status_code == 200
    assert response.json()["is_active"] is True