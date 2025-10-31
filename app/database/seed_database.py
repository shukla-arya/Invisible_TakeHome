"""
Populates the database with sample data for testing.
Creates users, accounts, transactions, and cards.
Encrypted card numbers, expiry dates, and CVVs for Fernet decryption compatibility.
"""

# Imports
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database.create_database import SessionLocal, Base, engine
from app.models import User, Account, Card
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()
CARD_ENCRYPTION_KEY = os.getenv("CARD_ENCRYPTION_KEY")
fernet = Fernet(CARD_ENCRYPTION_KEY.encode())

# Utility functions
def encrypt(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

# Reset DB (drop all tables and recreate)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Start session
db: Session = SessionLocal()

try:
    # --- Users ---
    alice = User(
        id=1,
        name="Alice Johnson",
        email="alice@example.com",
        hashed_password=generate_password_hash("alicepassword")
    )
    bob = User(
        id=2,
        name="Bob Smith",
        email="bob@example.com",
        hashed_password=generate_password_hash("bobpassword")
    )
    db.add_all([alice, bob])
    db.commit()

    # --- Accounts ---
    acc1 = Account(id=1, user_id=1, account_type="checking", balance=2500.0)
    acc2 = Account(id=2, user_id=1, account_type="savings", balance=4000.0)
    acc3 = Account(id=3, user_id=2, account_type="checking", balance=1800.0)
    db.add_all([acc1, acc2, acc3])
    db.commit()

    # --- Cards ---
    card1 = Card(
        id=1,
        account_id=1,
        user_id=1,
        card_number=encrypt("1111222233334444"),
        expiry_date=encrypt("12/30"),
        cvv=encrypt("123"),
        is_active=True
    )
    card2 = Card(
        id=2,
        account_id=2,
        user_id=1,
        card_number=encrypt("5555666677778888"),
        expiry_date=encrypt("01/31"),
        cvv=encrypt("456"),
        is_active=True
    )
    db.add_all([card1, card2])
    db.commit()

    print("Database seeded successfully!")

finally:
    db.close()