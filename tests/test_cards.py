"""
Pytest unit test functions for cards.py endpoints.
Focuses on activation and deactivation, creation, and invalid inputs.
"""

# Imports
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import User, Account, Card
from app.main import app
from jose import jwt

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db for tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Fixtures
@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    user = User(email="test@example.com", hashed_password="fakehashed", name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture
def test_account(test_user):
    db = TestingSessionLocal()
    account = Account(user_id=test_user.id, account_type="checking", balance=100.0)
    db.add(account)
    db.commit()
    db.refresh(account)
    db.close()
    return account

@pytest.fixture
def auth_header(test_user):
    SECRET_KEY = "testsecret"
    ALGORITHM = "HS256"
    token = jwt.encode({"sub": test_user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


# Tests
def test_create_card(test_user, test_account, auth_header):
    response = client.post(
        "/cards/cards",
        json={"account_id": test_account.id, "expiry_date": "12/30", "cvv": "123"},
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == test_account.id
    assert data["is_active"] is True
    assert len(data["card_number"]) == 16


def test_list_cards(test_user, test_account, auth_header):
    # Create a card first
    db = TestingSessionLocal()
    card = Card(account_id=test_account.id, user_id=test_user.id, card_number="1234567890123456",
                expiry_date="12/30", cvv="123", is_active=True)
    db.add(card)
    db.commit()
    db.refresh(card)
    db.close()

    response = client.get("/cards/cards", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["account_id"] == test_account.id


def test_activate_deactivate_card(test_user, test_account, auth_header):
    db = TestingSessionLocal()
    card = Card(account_id=test_account.id, user_id=test_user.id, card_number="1234567890123456",
                expiry_date="12/30", cvv="123", is_active=False)
    db.add(card)
    db.commit()
    db.refresh(card)
    db.close()

    # Activate
    response = client.patch(f"/cards/cards/{card.id}/activate", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["is_active"] is True

    # Deactivate
    response = client.patch(f"/cards/cards/{card.id}/deactivate", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_create_card_invalid_account(test_user, auth_header):
    response = client.post(
        "/cards/cards",
        json={"account_id": 999, "expiry_date": "12/30", "cvv": "123"},
        headers=auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found or not owned by user"


def test_create_card_invalid_cvv(test_user, test_account, auth_header):
    response = client.post(
        "/cards/cards",
        json={"account_id": test_account.id, "expiry_date": "12/30", "cvv": "12a"},
        headers=auth_header
    )
    assert response.status_code == 422  # validation error


def test_create_card_invalid_expiry(test_user, test_account, auth_header):
    response = client.post(
        "/cards/cards",
        json={"account_id": test_account.id, "expiry_date": "13/30", "cvv": "123"},
        headers=auth_header
    )
    assert response.status_code == 422  # validation error