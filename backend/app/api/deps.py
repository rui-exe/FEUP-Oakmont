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
import app.crud.users as crud_users
import happybase
import grpc
from app.hbase_client.hbase_client_pb2_grpc import TradeExecutorStub,InstrumentAnalyticsStub

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/oauth/token")


def get_hbase_connection() -> Generator[happybase.Connection, None, None]:
  """
    Get a HBase session
  """
  connection =  happybase.Connection(host=settings.THRIFT_HOST, port=settings.THRIFT_PORT)
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
                         settings.SECRET_KEY,
                         algorithms=[settings.JWT_ALGORITHM])
    token_data = TokenPayload(**payload)
  except (JWTError, ValidationError):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )
  user = crud_users.get_user_by_username(db=db, username=token_data.username)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_trade_executor_stub():
  with grpc.insecure_channel(f"{settings.HBASE_CLIENT_HOST}:{settings.HBASE_CLIENT_PORT}") as channel:
      yield TradeExecutorStub(channel)
    
TradeExecutor = Annotated[TradeExecutorStub, Depends(get_trade_executor_stub)]


def get_instrument_analytics_stub():
  with grpc.insecure_channel(f"{settings.HBASE_CLIENT_HOST}:{settings.HBASE_CLIENT_PORT}") as channel:
      yield InstrumentAnalyticsStub(channel)
    
InstrumentAnalytics = Annotated[InstrumentAnalyticsStub, Depends(get_instrument_analytics_stub)]