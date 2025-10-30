"""
Quick diagnostic script to confirm the SQLite database setup for the Banking API.
Checks the database connection, table creation from models, and row counts for each table.
"""

# Imports
import os
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from app.database import engine, SessionLocal
from app import models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_database():
    print("\nVerifying SQLite database setup.\n")

    # Ensure the database URL is set
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not found in environment variables.")
        return

    print(f"DATABASE_URL loaded: {db_url}")

    try:
        # Ensure tables are created
        models.Base.metadata.create_all(bind=engine)
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if not tables:
            print("No tables found in the database.")
            return

        print(f"Tables detected: {tables}\n")

        # Create session
        session = SessionLocal()

        # Display row counts
        for table_name in tables:
            count = session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"Table '{table_name}' → {count} rows")

        session.close()
        print("\nDatabase verification complete.")

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    verify_database()
