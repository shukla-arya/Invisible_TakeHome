"""
Handles account-related endpoints such as creating accounts, deposits,
withdrawals, transfers, and fetching account statements for the authorized user.
"""

# Imports
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Account, Transaction
from app.schemas import AccountCreate, AccountOut, BalanceUpdateOut, TransactionOut, TransferRequest
from app.utils.auth_helpers import get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])

# --- Create a new account ---
@router.post("/", response_model=AccountOut)
def create_account(account: AccountCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    new_account = Account(
        user_id=user.id,
        account_type=account.account_type,
        balance=getattr(account, "initial_balance", 0.0)
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


# --- List all accounts for the current user ---
@router.get("/", response_model=List[AccountOut])
def list_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Account).filter(Account.user_id == user.id).all()


# --- Deposit money into an account ---
@router.post("/{account_id}/deposit", response_model=BalanceUpdateOut)
def deposit(account_id: int, amount: float, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")

    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.balance += amount
    transaction = Transaction(account_id=account.id, amount=amount, transaction_type="deposit", description="Deposit")
    db.add(transaction)
    db.commit()
    db.refresh(account)
    return {"account_id": account.id, "new_balance": account.balance}


# --- Withdraw money from an account ---
@router.post("/{account_id}/withdraw", response_model=BalanceUpdateOut)
def withdraw(account_id: int, amount: float, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")

    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
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


# --- Transfer money between accounts ---
@router.post("/transfer", response_model=BalanceUpdateOut)
def transfer(transfer: TransferRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from_account = db.query(Account).filter(Account.id == transfer.from_account_id, Account.user_id == user.id).first()
    to_account = db.query(Account).filter(Account.id == transfer.to_account_id).first()

    if not from_account:
        raise HTTPException(status_code=404, detail="Source account not found or not owned by user")
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    if from_account.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Perform transfer
    from_account.balance -= transfer.amount
    to_account.balance += transfer.amount

    transaction = Transaction(
        account_id=from_account.id,
        amount=transfer.amount,
        transaction_type="transfer",
        description=transfer.description or "Transfer"
    )
    db.add(transaction)
    db.commit()
    db.refresh(from_account)
    return {"account_id": from_account.id, "new_balance": from_account.balance}


# --- Get transactions (statement) for a specific account ---
@router.get("/{account_id}/transactions", response_model=List[TransactionOut])
def get_account_statement(
    account_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or not owned by user")

    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id == account_id)
        .order_by(Transaction.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions