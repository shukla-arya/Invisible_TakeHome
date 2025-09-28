'''
Creates new cards and lists cards that are tied to accounts/users.
Handles card activation and deactivation if specified.
'''

# Imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Card, Account, User
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from datetime import datetime
import random
from app.schemas import CardCreate, CardOut
from cryptography.fernet import Fernet

# Load secret information from .env
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
CARD_ENCRYPTION_KEY = os.getenv("CARD_ENCRYPTION_KEY")

ALGORITHM = "HS256"

fernet = Fernet(CARD_ENCRYPTION_KEY.encode())

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT helper
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

# Mask helper
def mask_card_number(card_number: str) -> str:
    """Show only last 4 digits of card number."""
    return f"**** **** **** {card_number[-4:]}"

# Routes
@router.post("/cards", response_model=CardOut)
def create_card(card: CardCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == card.account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or not owned by user")

    # Generate and encrypt card info
    card_number_plain = "".join([str(random.randint(0, 9)) for _ in range(16)])
    card_number_enc = fernet.encrypt(card_number_plain.encode()).decode()
    expiry_enc = fernet.encrypt(card.expiry_date.encode()).decode()
    cvv_enc = fernet.encrypt(card.cvv.encode()).decode()

    db_card = Card(
        account_id=account.id,
        user_id=user.id,
        card_number=card_number_enc,
        expiry_date=expiry_enc,
        cvv=cvv_enc,
        is_active=True
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)

    return CardOut(
        id=db_card.id,
        account_id=db_card.account_id,
        card_number=mask_card_number(card_number_plain),
        expiry_date=card.expiry_date,
        is_active=db_card.is_active,
    )

@router.get("/cards", response_model=list[CardOut])
def list_cards(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cards = db.query(Card).filter(Card.user_id == user.id).all()
    results = []
    for c in cards:
        # Decrypt card number for masking
        card_number_plain = fernet.decrypt(c.card_number.encode()).decode()
        expiry_plain = fernet.decrypt(c.expiry_date.encode()).decode()
        results.append(CardOut(
            id=c.id,
            account_id=c.account_id,
            card_number=mask_card_number(card_number_plain),
            expiry_date=expiry_plain,
            is_active=c.is_active,
        ))
    return results

@router.patch("/cards/{card_id}/activate", response_model=CardOut)
def activate_card(card_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    card.is_active = True
    db.commit()
    db.refresh(card)

    card_number_plain = fernet.decrypt(card.card_number.encode()).decode()
    expiry_plain = fernet.decrypt(card.expiry_date.encode()).decode()

    return CardOut(
        id=card.id,
        account_id=card.account_id,
        card_number=mask_card_number(card_number_plain),
        expiry_date=expiry_plain,
        is_active=card.is_active,
    )

@router.patch("/cards/{card_id}/deactivate", response_model=CardOut)
def deactivate_card(card_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    card.is_active = False
    db.commit()
    db.refresh(card)

    card_number_plain = fernet.decrypt(card.card_number.encode()).decode()
    expiry_plain = fernet.decrypt(card.expiry_date.encode()).decode()

    return CardOut(
        id=card.id,
        account_id=card.account_id,
        card_number=mask_card_number(card_number_plain),
        expiry_date=expiry_plain,
        is_active=card.is_active,
    )
