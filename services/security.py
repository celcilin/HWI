
# services/security.py
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
import os

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-dev-only")
ALGORITHM = "HS256"

def get_password_hash(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt