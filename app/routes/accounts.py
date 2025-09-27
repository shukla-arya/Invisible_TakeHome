'''
Handles account-related endpoints such as creating new accounts and listing
accounts for the authorized user.
'''

# Imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Account, Transaction
from app.schemas import AccountCreate, AccountOut, BalanceUpdateOut
from app.utils.auth_helpers import get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("/", response_model=AccountOut)
def create_account(account: AccountCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    new_account = Account(user_id=user_id, balance=account.initial_balance)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@router.get("/", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    return db.query(Account).filter(Account.user_id == user_id).all()


@router.post("/{account_id}/deposit", response_model=BalanceUpdateOut)
def deposit(account_id: int, amount: float, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")

    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.balance += amount
    transaction = Transaction(account_id=account.id, amount=amount, transaction_type="deposit", description="Deposit")
    db.add(transaction)
    db.commit()
    db.refresh(account)
    return {"account_id": account.id, "new_balance": account.balance}


@router.post("/{account_id}/withdraw", response_model=BalanceUpdateOut)
def withdraw(account_id: int, amount: float, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")

    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    account.balance -= amount
    transaction = Transaction(account_id=account.id, amount=amount, transaction_type="withdraw", description="Withdrawal")
    db.add(transaction)
    db.commit()
    db.refresh(account)
    return {"account_id": account.id, "new_balance": account.balance}