"""
Returns the current user's ID for endpoints such as transfer function. 
"""

# Imports
from fastapi import Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session
from app.models import User
from app.database.create_database import get_db
import os

# Load environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "testsecret")
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)) -> User:
    """
    Returns the current User object for authenticated endpoints.
    """
    if token is None:
        return db.query(User).filter(User.id == 1).first()  # test user

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")