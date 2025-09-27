'''
Handles monetary transfers and validates the balances.
'''

# Imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Account, Transaction
from app.schemas import TransferRequest, BalanceUpdateOut
from app.utils.auth_helpers import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/transfer", response_model=BalanceUpdateOut)
def transfer(tx: TransferRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if tx.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")

    from_account = db.query(Account).filter(Account.id == tx.from_account_id, Account.user_id == user_id).first()
    if not from_account:
        raise HTTPException(status_code=404, detail="Source account not found")

    to_account = db.query(Account).filter(Account.id == tx.to_account_id).first()
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")

    if from_account.balance < tx.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Perform transfer
    from_account.balance -= tx.amount
    to_account.balance += tx.amount

    # Record both sides of transfer
    debit = Transaction(
        account_id=from_account.id,
        amount=-tx.amount,
        transaction_type="transfer",
        description=f"Transfer to account {to_account.id}"
    )
    credit = Transaction(
        account_id=to_account.id,
        amount=tx.amount,
        transaction_type="transfer",
        description=f"Transfer from account {from_account.id}"
    )

    db.add_all([debit, credit])
    db.commit()
    db.refresh(from_account)
    return {"account_id": from_account.id, "new_balance": from_account.balance}

