"""Global configuration settings for the application."""

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import secrets
load_dotenv()



class Settings(BaseSettings):
  """
  Global configuration settings for the application.
  """
  SECRET_KEY: str = secrets.token_urlsafe(32)
  JWT_ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
  THRIFT_HOST: str = os.getenv("THRIFT_HOST")
  THRIFT_PORT: int = os.getenv("THRIFT_PORT")
  HBASE_CLIENT_HOST: str = os.getenv("HBASE_CLIENT_HOST")
  HBASE_CLIENT_PORT: int = os.getenv("HBASE_CLIENT_PORT")


settings = Settings()
