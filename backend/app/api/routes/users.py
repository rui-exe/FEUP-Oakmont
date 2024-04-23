"""
  Users routes.
"""
from typing import Any
from fastapi import APIRouter, HTTPException
from app.crud import users as crud_users, posts as crud_posts, trades as crud_trades
from app.api.deps import (
    CurrentUser,
    HBase,
)
from app.models.users import (UserCreate, UserPublic)
from app.models.trades import Trade

router = APIRouter()


@router.post("/")
def create_user(*, db: HBase, user_in: UserCreate) -> UserPublic:
  """
  Create a new user.
  """
  user = crud_users.get_user_by_username(db=db,
                                         username=user_in.username)
  if user:
    raise HTTPException(
        status_code=400,
        detail="The user with this username already exists in the system",
    )
  user_create = UserCreate.model_validate(user_in)
  user = crud_users.create_user(db=db, user_create=user_create)
  return user


@router.get("/me")
def read_user_me(current_user: CurrentUser) -> UserPublic:
  """
  Get current user.
  """
  return current_user


@router.delete("/{username}")
def delete_user(db: HBase, current_user: CurrentUser,
                username: str) -> Any:
  """
  Delete the user with the provided ID.
  """
  user = crud_users.get_user_by_username(db=db, username=username)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  elif user != current_user:
    raise HTTPException(status_code=403,
                        detail="The user doesn't have enough privileges")

  crud_users.delete_user_by_username(db=db,username=username)
  return {"message": "User deleted successfully"}


@router.get("/{username}/posts")
def get_user_posts(db:HBase, username:str):
  """
  Get the posts of a user.
  """
  return crud_posts.get_user_posts(db, username)


@router.get("/{username}/trades")
def get_user_trades(db:HBase, username:str) -> list[Trade]:
  """
  Get the trades of a user.
  """
  return crud_trades.get_user_trades(db, username)


@router.get("/{username}/portfolio")
def get_user_portfolio(db:HBase, username:str):
  """
  Get the posts of a user.
  """
  return crud_trades.get_user_portfolio(db, username)