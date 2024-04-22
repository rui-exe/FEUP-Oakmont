"""
  This module contains the pydantic models for the JWT tokens.
"""

from pydantic import BaseModel


class Token(BaseModel):
  """
    The schema for the JWT token returned by the authentication endpoint.
  """
  access_token: str
  token_type: str = "bearer"


class TokenPayload(BaseModel):
  """
    The schema for the JWT token payload.
  """
  username: str | None = None