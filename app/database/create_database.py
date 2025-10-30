'''
This code sets up the engine, session, and base for the models.
Configures the database connection using the URL from the .env.
'''

# Imports
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Set up the database connection
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite://app/database/bank.db")

# Creats an SQLite session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()