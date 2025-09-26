'''
Defines the data validation and serialization for requests.
Ensures that the API only accepts and returns properly formatted data.
This structure gets fed into the models.py file.
'''

# Imports
from pydantic import BaseModel, EmailStr # data validation Python library

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
