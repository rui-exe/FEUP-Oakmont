"""
  This file contains the Pydantic models for the User entity.
"""
from pydantic import BaseModel, validator, Field
from fastapi import HTTPException



class UserBase(BaseModel):
  """
  The basic information of a user.
  """
  username: str
  name: str
  email: str

class UserPublic(UserBase):
  """
  The public information of a user.
  """
  nr_following: int = Field(default=0)
  nr_followers: int = Field(default=0)
  balance:float = Field(default=0)
  @validator('balance')
  def check_decimal_places(cls, value):
      if value != round(value, 2):
          raise HTTPException(status_code=500, detail="Amount must have at most 2 decimal places")
      return value

class UserCreate(UserBase):
  """
  The information needed to create a new user.
  """
  password: str


class User(UserPublic):
  """
    The database model for the User entity.
  """
  hashed_password: str


class BalanceIncrease(BaseModel):
  amount: float
  @validator('amount')
  def check_decimal_places(cls, value):
      if value != round(value, 2):
          raise HTTPException(status_code=422, detail="Balance increase must have at most 2 decimal places")
      return value
