"""
  This file contains the Pydantic models for the User entity.
"""
from pydantic import BaseModel,Field



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
