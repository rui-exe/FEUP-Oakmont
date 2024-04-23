"""
  This module contains the routes for the OAuth2 token generation.
"""


from typing import Annotated

from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.crud import users as crud_users
from app.core import security
from app.core.config import settings
from app.api.deps import HBase
from app.models.tokens import Token

router = APIRouter()

"""
  Given the username and password, return a JWT token.
"""
@router.post("/token")
def login_access_token(
    db: HBase, form_data: Annotated[OAuth2PasswordRequestForm,
                                              Depends()]) -> Token:
  """
    OAuth2 compatible token login, get an access token for future requests
  """
  user = crud_users.authenticate(db=db,
                                 username=form_data.username,
                                 password=form_data.password)
  if not user:
    raise HTTPException(status_code=400,
                        detail="Incorrect username or password")

  access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
  return Token(access_token=security.create_access_token(
      user.username, expires_delta=access_token_expires))