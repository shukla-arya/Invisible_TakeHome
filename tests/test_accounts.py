"""
Pytest unit test functions for the accounts.py logic.
Focuses on creating accounts, deposits, withdrawals, transfers.
"""

# Imports
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import User, Account
from app.main import app
from jose import jwt

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Use a fixed secret key for tests
TEST_SECRET_KEY = "testsecret"
os.environ["JWT_SECRET_KEY"] = TEST_SECRET_KEY

# Fixtures
@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create and drop tables for each test function."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user in the database."""
    db = TestingSessionLocal()
    user = User(email="test@example.com", hashed_password="fakehashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.close()
    user.id = user_id  # keep id accessible
    return user


@pytest.fixture
def auth_header(test_user):
    """Create an Authorization header with a test JWT token."""
    token = jwt.encode({"sub": test_user.email}, TEST_SECRET_KEY, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


# Tests
def test_create_account(test_user, auth_header):
    response = client.post(
        "/accounts/",
        json={"account_type": "checking"},
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["account_type"] == "checking"
    assert data["balance"] == 0.0


def test_deposit_success(test_user, auth_header):
    # Create account
    db = TestingSessionLocal()
    account = Account(user_id=test_user.id, account_type="checking", balance=100.0)
    db.add(account)
    db.commit()
    db.refresh(account)
    account_id = account.id
    db.close()

    response = client.post(
        f"/accounts/{account_id}/deposit?amount=50",
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["new_balance"] == 150.0


def test_withdraw_insufficient_balance(test_user, auth_header):
    db = TestingSessionLocal()
    account = Account(user_id=test_user.id, account_type="checking", balance=20.0)
    db.add(account)
    db.commit()
    db.refresh(account)
    account_id = account.id
    db.close()

    response = client.post(
        f"/accounts/{account_id}/withdraw?amount=50",
        headers=auth_header
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance"


def test_transfer_success(test_user, auth_header):
    db = TestingSessionLocal()
    acc1 = Account(user_id=test_user.id, account_type="checking", balance=100.0)
    acc2 = Account(user_id=test_user.id, account_type="savings", balance=50.0)
    db.add_all([acc1, acc2])
    db.commit()
    db.refresh(acc1)
    db.refresh(acc2)
    acc1_id = acc1.id
    acc2_id = acc2.id
    db.close()

    response = client.post(
        f"/accounts/{acc1_id}/transfer/{acc2_id}?amount=40",
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["from_account_balance"] == 60.0
    assert data["to_account_balance"] == 90.0