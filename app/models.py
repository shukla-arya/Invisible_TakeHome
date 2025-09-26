'''
Generates SQLAlchemy models for a banking service including Users, Accounts, Transactions, Cards.
Includes foreign keys, timestamps, and basic constraints.
Maps to tables in SQLite.
'''

# Imports
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Define the entities and attributes
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    accounts = relationship("Account", back_populates="owner")
    cards = relationship("Card", back_populates="owner")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_type = Column(String, nullable=False)  # e.g., "checking", "savings"
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    cards = relationship("Card", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # e.g., "deposit", "withdrawal", "transfer"
    timestamp = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=True)

    account = relationship("Account", back_populates="transactions")

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_number = Column(String, unique=True, nullable=False)
    expiry_date = Column(String, nullable=False)  # format: MM/YY
    cvv = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="cards")
    owner = relationship("User", back_populates="cards")
