"""
Unit and integration testing for account information.
"""

# Imports
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base, User
from app.database.create_database import get_db
from app.routes.auth_helpers import get_current_user

# Use a file-based DB for tests (or a shared in-memory connection)
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

# -----------------------
# Tests
# -----------------------

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Banking API"}


def test_create_account():
    payload = {"account_type": "checking", "initial_balance": 300}
    response = client.post("/accounts/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["account_type"] == "checking"
    assert data["balance"] == 300
    assert "id" in data


def test_list_accounts():
    # Ensure at least one account exists
    client.post("/accounts/", json={"account_type": "savings", "initial_balance": 200})
    response = client.get("/accounts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_deposit():
    resp = client.post("/accounts/", json={"account_type": "savings", "initial_balance": 200})
    account_id = resp.json()["id"]
    deposit_resp = client.post(f"/accounts/{account_id}/deposit", params={"amount": 100})
    assert deposit_resp.status_code == 200
    data = deposit_resp.json()
    assert data["new_balance"] == 300


def test_withdraw():
    resp = client.post("/accounts/", json={"account_type": "checking", "initial_balance": 500})
    account_id = resp.json()["id"]
    withdraw_resp = client.post(f"/accounts/{account_id}/withdraw", params={"amount": 200})
    assert withdraw_resp.status_code == 200
    data = withdraw_resp.json()
    assert data["new_balance"] == 300


def test_transfer():
    from_resp = client.post("/accounts/", json={"account_type": "checking", "initial_balance": 500})
    to_resp = client.post("/accounts/", json={"account_type": "savings", "initial_balance": 300})
    from_id = from_resp.json()["id"]
    to_id = to_resp.json()["id"]

    transfer_payload = {
        "from_account_id": from_id,
        "to_account_id": to_id,
        "amount": 150,
        "description": "Test transfer"
    }

    transfer_resp = client.post("/accounts/transfer", json=transfer_payload)
    assert transfer_resp.status_code == 200
    data = transfer_resp.json()
    assert data["new_balance"] == 350  # 500 - 150