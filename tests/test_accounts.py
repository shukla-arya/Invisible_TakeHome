'''
Pytest unit test functions for the accounts.py logic.
'''

# Imports
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

# Dependency override for tests
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
    user = User(email="test@example.com", hashed_password="fakehashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture
def auth_header(test_user):
    # Issue a fake JWT with subject = email
    SECRET_KEY = "testsecret"
    ALGORITHM = "HS256"
    token = jwt.encode({"sub": test_user.email}, SECRET_KEY, algorithm=ALGORITHM)
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
    db.close()

    response = client.post(
        f"/accounts/{account.id}/deposit?amount=50",
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
    db.close()

    response = client.post(
        f"/accounts/{account.id}/withdraw?amount=50",
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
    db.close()

    response = client.post(
        f"/accounts/{acc1.id}/transfer/{acc2.id}?amount=40",
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["from_account_balance"] == 60.0
    assert data["to_account_balance"] == 90.0

