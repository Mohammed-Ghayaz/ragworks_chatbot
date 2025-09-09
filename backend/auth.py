from json import load
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

class UserRegistration(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_encryption = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret_hash_key = os.getenv("SECRET_HASH_KEY")
ACCESS_TOKEN_EXPIRY = 30


def verify_password(password: str, hashed_password: str):
    return pwd_encryption.verify(password, hashed_password)

def hash_password(password: str):
    return pwd_encryption.hash(password)

def create_access_token(data: dict, expiry_delta: timedelta | None = None):
    to_encode = data.copy()

    if expiry_delta:
        expiry = datetime.utcnow() + expiry_delta
    else:
        expiry = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expiry})
    
    return jwt.encode(to_encode, secret_hash_key, algorithm="HS256")


