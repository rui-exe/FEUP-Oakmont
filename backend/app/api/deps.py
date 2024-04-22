"""
  Dependencies for FastAPI endpoints
"""

from collections.abc import Generator
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from app.core.config import settings
from app.models.users import User
from app.models.tokens import TokenPayload
import happybase
import app.crud.users as crud_users

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/oauth/token")


def get_hbase_connection() -> Generator[happybase.Connection, None, None]:
  """
    Get a HBase session
  """
  connection =  happybase.Connection(host=settings.HBASE_HOST, port=settings.HBASE_PORT)
  yield connection
  connection.close()

HBase = Annotated[happybase.Connection, Depends(get_hbase_connection)]
OAuth2Token = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(db: HBase, token: OAuth2Token) -> User:
  """
  Get the current user from the JWT token
  """
  try:
    payload = jwt.decode(token,
                         settings.PUBLIC_KEY,
                         algorithms=[settings.JWT_ALGORITHM])
    token_data = TokenPayload(**payload)
  except (JWTError, ValidationError):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )
  user = crud_users.get_user_by_username(token_data.username)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user


CurrentUser = Annotated[User, Depends(get_current_user)]