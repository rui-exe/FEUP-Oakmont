"""
  This module contains the CRUD operations for the User ORM.
"""
from happybase import Connection
from app.core.security import get_password_hash, verify_password
from app.models.users import User, UserCreate, UserPublic



def create_user(*, db: Connection, user_create: UserCreate) -> UserPublic:
  """
  Create a new user.
  Args:
    db: HBase session
    user_create: New user information
  Returns:
    User: The created user
  """
  
  user = User.model_validate(
      user_create,
      update={"hashed_password": get_password_hash(user_create.password)})
  
  users = db.table("user")
  users.put(user.username.encode("utf-8"),{
    user.name.encode("utf-8"),
    user.password.encode("utf-8"),
    user.email.encode("utf-8")
  })
  
  return user

def delete_user_by_username(*, db: Connection, username: str) -> None:
  """
  Deletes the user given by username.
  Args:
    db: HBase session
    username: User's username
  Returns:
    None:
  """
  users = db.table("user")
  users.delete(username.encode("utf-8"))



def get_user_by_username(*, db: Connection, username: str) -> User | None:
  """
    Get a user by username.
    Args:
      db: HBase session
      username: The username to search
    Returns:
      User | None: The user found or None
  """
  
  users = db.table("user")
  user_in_db = users.row(username.decode("utf-8"), columns=[b'info:username', b'info:name', b'info:email', b'info:password'])
  
  username = user_in_db[b'info:username']
  name = user_in_db[b'info:name']
  email = user_in_db[b'info:email']
  password = user_in_db[b'info:password']

  return User(username=username, name=name, email=email, hashed_password=password)


def authenticate(*, db: Connection, username: str,
                 password: str) -> User | None:
  """
    Given an username and a password, authenticate the user.
    Args:
      db: HBase session
      username: The username to authenticate
      password: The password to authenticate
    Returns:
      User | None: The authenticated user or None if the user
        is not found or the password is incorrect
  """
  db_user = get_user_by_username(db=db, username=username)
  if not db_user:
    return None
  if not verify_password(password, db_user.hashed_password):
    return None
  return db_user