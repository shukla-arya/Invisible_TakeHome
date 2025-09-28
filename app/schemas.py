'''
Defines the data validation and serialization for requests.
Ensures that the API only accepts and returns properly formatted data.
This structure gets fed into the models.py file.
'''

# Imports
from pydantic import BaseModel, EmailStr, field_validator # data validation Python library
from typing import Optional
from datetime import datetime

# Build classes to inherit the BaseModel
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class AccountCreate(BaseModel):
    account_type: str  # "checking" or "savings"
    initial_balance: float = 0.0

class AccountOut(BaseModel):
    id: int
    user_id: int
    account_type: str
    balance: float
    created_at: datetime

    model_config = {
        "from_attributes": True # equivalent to orm_mode, V2 update
    }

class TransactionCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    description: Optional[str] = None

class TransactionOut(BaseModel):
    id: int
    from_account_id: int | None
    to_account_id: int | None
    amount: float
    transaction_type: str
    timestamp: datetime
    description: Optional[str]

    model_config = {
        "from_attributes": True
    }

class CardCreate(BaseModel):
    account_id: int
    expiry_date: str # MM/YY format
    cvv: str # 3-4 digits

    @field_validator("expiry_date")
    def validate_expiry_date(cls, v):
        try:
            datetime.strptime(v, "%m/%y")
        except ValueError:
            raise ValueError("Expiry date must be in MM/YY format")
        return v

    @field_validator("cvv")
    def validate_cvv(cls, v):
        if not v.isdigit() or len(v) not in (3, 4):
            raise ValueError("CVV must be 3 or 4 digits")
        return v

class CardOut(BaseModel): # CVV excluded for encryption purposes
    id: int
    account_id: int
    card_number: str
    expiry_date: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }

class BalanceUpdateOut(BaseModel):
    account_id: int
    new_balance: float

    model_config = {
        "from_attributes": True
    }

class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    description: str | None = None