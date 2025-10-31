"""
Handles account-related endpoints such as creating accounts, deposits,
withdrawals, transfers, and fetching account statements for the authorized user.
"""

# Imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import Account, User
from app.database.create_database import get_db
from app.routes.auth_helpers import get_current_user
from app.schemas import AccountCreate, AccountOut, BalanceUpdateOut, TransferRequest

router = APIRouter()

# -------------------------
# Routes
# -------------------------

@router.post("/", response_model=AccountOut)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_account = Account(
        user_id=current_user.id,
        account_type=account.account_type,
        balance=account.initial_balance
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@router.get("/", response_model=List[AccountOut])
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    return accounts


@router.post("/{account_id}/deposit", response_model=BalanceUpdateOut)
def deposit(
    account_id: int,
    amount: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account.balance += amount
    db.commit()
    db.refresh(account)
    return BalanceUpdateOut(account_id=account.id, new_balance=account.balance)


@router.post("/{account_id}/withdraw", response_model=BalanceUpdateOut)
def withdraw(
    account_id: int,
    amount: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if amount > account.balance:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    account.balance -= amount
    db.commit()
    db.refresh(account)
    return BalanceUpdateOut(account_id=account.id, new_balance=account.balance)