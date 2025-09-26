'''
Handles monetary transfers and validates the balances.
'''

# Imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Account, Transaction
from app.schemas import TransactionCreate, TransactionOut
from routes.accounts import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/transactions/transfer", response_model=TransactionOut)
def transfer_money(tx: TransactionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from_account = db.query(Account).filter(Account.id == tx.from_account_id, Account.user_id == user.id).first()
    to_account = db.query(Account).filter(Account.id == tx.to_account_id).first()

    if not from_account:
        raise HTTPException(status_code=404, detail="Source account not found or not owned by user")
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    if from_account.balance < tx.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Perform transfer
    from_account.balance -= tx.amount
    to_account.balance += tx.amount

    transaction = Transaction(account_id=from_account.id, amount=tx.amount, transaction_type="transfer", description=tx.description)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
