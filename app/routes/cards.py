'''
Creates new cards and lists cards that are tied to accounts/users.
Handles card activation and deactivation if specified.
'''

# Imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Card, Account, User
from app.schemas import AccountOut  # optional for reference, can create CardOut if needed
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from datetime import datetime
import random

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Dependency to get DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- JWT helper ---
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

# --- Pydantic Schemas ---
class CardCreate(BaseModel):
    account_id: int
    expiry_date: str  # MM/YY
    cvv: str

class CardOut(BaseModel):
    id: int
    account_id: int
    card_number: str
    expiry_date: str
    is_active: bool

    class Config:
        orm_mode = True

# --- Routes ---
@router.post("/cards", response_model=CardOut)
def create_card(card: CardCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == card.account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or not owned by user")

    # Generate a random card number
    card_number = "".join([str(random.randint(0, 9)) for _ in range(16)])
    
    db_card = Card(
        account_id=account.id,
        user_id=user.id,
        card_number=card_number,
        expiry_date=card.expiry_date,
        cvv=card.cvv,
        is_active=True
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@router.get("/cards", response_model=list[CardOut])
def list_cards(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Card).filter(Card.user_id == user.id).all()

@router.patch("/cards/{card_id}/activate", response_model=CardOut)
def activate_card(card_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    card.is_active = True
    db.commit()
    db.refresh(card)
    return card

@router.patch("/cards/{card_id}/deactivate", response_model=CardOut)
def deactivate_card(card_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    card.is_active = False
    db.commit()
    db.refresh(card)
    return card
