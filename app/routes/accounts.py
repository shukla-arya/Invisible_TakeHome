'''
Handles account-related endpoints such as creating new accounts and listing
accounts for the authorized user.
'''

# Imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Account, User
from app.schemas import AccountCreate, AccountOut
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

router = APIRouter(prefix="/accounts", tags=["Accounts"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth helper
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Endpoints

# Create account
@router.post("/", response_model=AccountOut)
def create_account(
    account: AccountCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    db_account = Account(user_id=user.id, account_type=account.account_type, balance=0.0)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


# Get all accounts for current user
@router.get("/", response_model=list[AccountOut])
def get_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Account).filter(Account.user_id == user.id).all()


# Deposit
@router.post("/{account_id}/deposit")
def deposit(
    account_id: int, 
    amount: float, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")

    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.balance += amount
    db.commit()
    db.refresh(account)
    return {"message": "Deposit successful", "new_balance": account.balance}


# Withdraw
@router.post("/{account_id}/withdraw")
def withdraw(
    account_id: int, 
    amount: float, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")

    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    account.balance -= amount
    db.commit()
    db.refresh(account)
    return {"message": "Withdrawal successful", "new_balance": account.balance}


# Transfer
@router.post("/{from_account_id}/transfer/{to_account_id}")
def transfer(
    from_account_id: int, 
    to_account_id: int, 
    amount: float,
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")

    from_account = db.query(Account).filter(Account.id == from_account_id, Account.user_id == user.id).first()
    to_account = db.query(Account).filter(Account.id == to_account_id).first()

    if not from_account:
        raise HTTPException(status_code=404, detail="Source account not found")
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    if from_account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    from_account.balance -= amount
    to_account.balance += amount
    db.commit()
    return {
        "message": "Transfer successful",
        "from_account_balance": from_account.balance,
        "to_account_balance": to_account.balance
    }