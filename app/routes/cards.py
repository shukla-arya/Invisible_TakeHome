"""
Handles card-related endpoints such as card creation,
activation, and deactivation.
"""

# Imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.create_database import get_db
from app.models import Card, Account, User
from app.routes.auth_helpers import get_current_user  # <- shared
from app.schemas import CardCreate, CardOut
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import random

# Load secrets
load_dotenv()
CARD_ENCRYPTION_KEY = os.getenv("CARD_ENCRYPTION_KEY")
fernet = Fernet(CARD_ENCRYPTION_KEY.encode())

router = APIRouter()

# ------------------
# Helpers
# ------------------
def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()

def mask_card_number(card_number: str) -> str:
    return f"**** **** **** {card_number[-4:]}"

def card_to_schema(card: Card) -> CardOut:
    card_number_plain = decrypt_value(card.card_number)
    expiry_plain = decrypt_value(card.expiry_date)
    return CardOut(
        id=card.id,
        account_id=card.account_id,
        card_number=mask_card_number(card_number_plain),
        expiry_date=expiry_plain,
        is_active=card.is_active
    )

# ------------------
# Routes
# ------------------
@router.post("/", response_model=CardOut)
def create_card(card: CardCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == card.account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or not owned by user")

    # Generate card info
    card_number_plain = "".join([str(random.randint(0, 9)) for _ in range(16)])
    db_card = Card(
        account_id=account.id,
        user_id=user.id,
        card_number=encrypt_value(card_number_plain),
        expiry_date=encrypt_value(card.expiry_date),
        cvv=encrypt_value(card.cvv),
        is_active=True
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return card_to_schema(db_card)

@router.get("/", response_model=list[CardOut])
def list_cards(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cards = db.query(Card).filter(Card.user_id == user.id).all()
    return [card_to_schema(c) for c in cards]

@router.patch("/{card_id}/activate", response_model=CardOut)
def activate_card(card_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    card.is_active = True
    db.commit()
    db.refresh(card)
    return card_to_schema(card)

@router.patch("/{card_id}/deactivate", response_model=CardOut)
def deactivate_card(card_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    card.is_active = False
    db.commit()
    db.refresh(card)
    return card_to_schema(card)