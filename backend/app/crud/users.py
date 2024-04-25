"""
  This module contains the CRUD operations for the User ORM.
"""
from happybase import Connection
from app.core.security import get_password_hash, verify_password
from app.models.users import User, UserCreate, UserPublic
from fastapi import HTTPException



def create_user(*, db: Connection, user_create: UserCreate) -> UserPublic:
  """
  Create a new user.
  Args:
    db: HBase session
    user_create: New user information
  Returns:
    User: The created user
  """

  hashed_password = get_password_hash(user_create.password)
  user = User(username=user_create.username, name=user_create.name, email=user_create.email, hashed_password=hashed_password)
  user = User.model_validate(user)
  users = db.table("user")

  users.put(user.username.encode("utf-8"),{
    b"info:name":user.name.encode("utf-8"),
    b"info:password":user.hashed_password.encode("utf-8"),
    b"info:email":user.email.encode("utf-8")
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
  user_in_db = users.row(username.encode("utf-8"), columns=[b'info'])
  if not user_in_db:
      return None
    
  user_data = {
    "username":username,
    "name": user_in_db[b"info:name"].decode("utf-8"),
    "email": user_in_db[b"info:email"].decode("utf-8"),
    "hashed_password": user_in_db[b"info:password"].decode("utf-8")
  }
  
  if b"info:following" in user_in_db:
    user_data["nr_following"] = users.counter_get(username.encode("utf-8"),b"info:following")
  if b"info:followers" in user_in_db:
    user_data["nr_followers"] = users.counter_get(username.encode("utf-8"),b"info:followers")


  return User(**user_data)


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
  db_user:User = get_user_by_username(db=db, username=username)
  if not db_user:
    return None
  if not verify_password(password, db_user.hashed_password):
    return None
  return db_user

def get_user_followers(*, db: Connection, username: str) -> list[str]:
    """
    Get the followers of a user.
    
    Args:
        db (Connection): The database connection.
        username (str): Username of the user to get the followers.
    
    Returns:
        List[str]: A list of usernames representing the followers of the specified user.
    """
    try:
        table = db.table('user')  # Assuming 'user' is the name of the table

        # iterate all the columns of the followers column family of the user
        followers_column_family = 'followers'
        followers_data = table.row(username.encode('utf-8'), columns=[f'{followers_column_family}'.encode('utf-8')])
        print(followers_data)
        followers = [follower.decode('utf-8').replace(followers_column_family+':', '') for follower, _ in followers_data.items()]
        return followers
    except Exception as e:
        # Handle exceptions, e.g., table not found, connection error, etc.
        # You may want to log the exception or handle it differently based on your application's requirements.
        print(f"Error occurred while retrieving followers for user {username}: {e}")
        return []

def get_user_following(*, db: Connection, username: str) -> list[str]:
    """
    Get the users that the user is following.
    
    Args:
        db (Connection): The database connection.
        username (str): Username of the user to get the following.
    
    Returns:
        List[str]: A list of usernames representing the users that the specified user is following.
    """
    try:
        table = db.table('user')  # Assuming 'user' is the name of the table

        # iterate all the columns of the following column family of the user
        following_column_family = 'following'
        following_data = table.row(username.encode('utf-8'), columns=[f'{following_column_family}'.encode('utf-8')])
        print(following_data)
        print(following_data)
        following_users = [following.decode('utf-8').replace(following_column_family+':', '') for following, _ in following_data.items()]
        return following_users
    except Exception as e:
        # Handle exceptions, e.g., table not found, connection error, etc.
        # You may want to log the exception or handle it differently based on your application's requirements.
        print(f"Error occurred while retrieving following users for user {username}: {e}")
        return []



def follow_user(*, db: Connection, follower: str, followee: str) -> bool:
    """
    Follow a user.
    
    Args:
        db (Connection): The database connection.
        follower (str): Username of the follower.
        followee (str): Username of the user to follow.
    
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    if follower == followee:
        print("User cannot follow themselves")
        raise HTTPException(status_code=400, detail="User cannot follow themselves")
    # check if the follower is already following the followee
    following_users = get_user_following(db=db, username=follower)
    if followee in following_users:
        print(f"User {follower} is already following {followee}")
        raise HTTPException(status_code=400, detail="User is already following the specified user")
    try:
        table = db.table('user')  # Assuming 'user' is the name of the table

        # Add the follower to the followee's followers list
        follower_key = f'followers:{follower}'.encode('utf-8')
        table.put(followee.encode('utf-8'), {follower_key: b'1'})

        # Increment the followee's follower count
        followers_count_key = f'info:followers'.encode('utf-8')
        table.counter_inc(followee.encode('utf-8'), followers_count_key, 1)

        # Increment the follower's following count
        following_count_key = f'info:following'.encode('utf-8')
        table.counter_inc(follower.encode('utf-8'), following_count_key, 1)

        # Add the followee to the follower's following list (optional)
        following_key = f'following:{followee}'.encode('utf-8')
        table.put(follower.encode('utf-8'), {following_key: b'1'})

        return True
    except Exception as e:
        # Handle exceptions, e.g., table not found, connection error, etc.
        # You may want to log the exception or handle it differently based on your application's requirements.
        print(f"Error occurred while following user {followee}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while following the user")

def unfollow_user(*, db: Connection, follower: str, followee: str) -> bool:
    """
    Unfollow a user.
    
    Args:
        db (Connection): The database connection.
        follower (str): Username of the follower.
        followee (str): Username of the user to unfollow.
    
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    if follower == followee:
        print("User cannot unfollow themselves")
        raise HTTPException(status_code=400, detail="User cannot unfollow themselves")
    # check if the follower is following the followee
    following_users = get_user_following(db=db, username=follower)
    if followee not in following_users:
        print(f"User {follower} is not following {followee}")
        raise HTTPException(status_code=400, detail="User is not following the specified user")
    try:
        table = db.table('user')  # Assuming 'user' is the name of the table

        # Remove the follower from the followee's followers list
        follower_key = f'followers:{follower}'.encode('utf-8')
        table.delete(followee.encode('utf-8'), columns=[follower_key])

        # Decrement the followee's follower count
        followers_count_key = f'info:followers'.encode('utf-8')
        table.counter_dec(followee.encode('utf-8'), followers_count_key, 1)

        # Decrement the follower's following count
        following_count_key = f'info:following'.encode('utf-8')
        table.counter_dec(follower.encode('utf-8'), following_count_key, 1)

        # Remove the followee from the follower's following list (optional)
        following_key = f'following:{followee}'.encode('utf-8')
        table.delete(follower.encode('utf-8'), columns=[following_key])

        return True
    except Exception as e:
        # Handle exceptions, e.g., table not found, connection error, etc.
        # You may want to log the exception or handle it differently based on your application's requirements.
        print(f"Error occurred while unfollowing user {followee}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while unfollowing the user")

