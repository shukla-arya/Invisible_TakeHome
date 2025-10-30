"""
Populates the database with sample data for testing.
Creates users, accounts, transactions, and cards.
"""

from app.database.create_database import SessionLocal, engine
from app.models import Base, User, Account, Transaction, Card
from datetime import datetime
import random

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Open a session
db = SessionLocal()

try:
    # Create sample users
    user1 = User(name="Alice Johnson", email="alice@example.com", hashed_password="hashed_pw_1")
    user2 = User(name="Bob Smith", email="bob@example.com", hashed_password="hashed_pw_2")

    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    # Create sample accounts
    acc1 = Account(user_id=user1.id, account_type="checking", balance=2500.0)
    acc2 = Account(user_id=user1.id, account_type="savings", balance=4000.0)
    acc3 = Account(user_id=user2.id, account_type="checking", balance=1800.0)

    db.add_all([acc1, acc2, acc3])
    db.commit()
    db.refresh(acc1)
    db.refresh(acc2)
    db.refresh(acc3)

    # Create sample transactions
    t1 = Transaction(from_account_id=None, to_account_id=acc1.id, amount=500.0,
                     transaction_type="deposit", description="Initial deposit")
    t2 = Transaction(from_account_id=acc1.id, to_account_id=None, amount=100.0,
                     transaction_type="withdrawal", description="ATM withdrawal")
    t3 = Transaction(from_account_id=acc1.id, to_account_id=acc3.id, amount=200.0,
                     transaction_type="transfer", description="Rent payment")

    db.add_all([t1, t2, t3])
    db.commit()

    # Create sample cards
    card1 = Card(account_id=acc1.id, user_id=user1.id,
                 card_number="1111-2222-3333-4444", expiry_date="12/28",
                 cvv="123", is_active=True)
    card2 = Card(account_id=acc3.id, user_id=user2.id,
                 card_number="5555-6666-7777-8888", expiry_date="06/27",
                 cvv="456", is_active=True)

    db.add_all([card1, card2])
    db.commit()

    print("Sample data inserted successfully!")

except Exception as e:
    db.rollback()
    print(f"Error inserting sample data: {e}")

finally:
    db.close()