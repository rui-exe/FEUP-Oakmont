"""
  This module contains the security functions for the application.
  It includes functions to manage JWT tokens and passwords.
"""
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
  """
  Create a new access token.
  Args:
    subject: The subject of the token
    expires_delta: for how long the token will be valid
  Returns:
    str: The encoded token
  """
  expire = datetime.now(timezone.utc) + expires_delta
  to_encode = {"exp": expire, "sub": str(subject)}
  encoded_jwt = jwt.encode(to_encode,
                           settings.SECRET_KEY,
                           algorithm=settings.ALGORITHM)
  return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
  """
  Verify a password.
  Args:
    plain_password: The plain password
    hashed_password: The hashed password, as stored in the database
  Returns:
    bool: True if the password is correct, False otherwise
  """
  return pwd_context.verify(plain_password, hashed_password)



def get_password_hash(password: str) -> str:
  """
  Hash a password.
  Args:
    password: The password to hash
  Returns:
    str: The hashed password
  """
  return pwd_context.hash(password)