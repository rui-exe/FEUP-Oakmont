"""Global configuration settings for the application."""

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()



class Settings(BaseSettings):
  """
  Global configuration settings for the application.
  """

  HBASE_HOST: str = os.getenv("HBASE_HOST")
  HBASE_PORT: int = os.getenv("HBASE_PORT")


settings = Settings()
