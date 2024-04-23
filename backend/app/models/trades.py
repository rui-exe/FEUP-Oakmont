"""
  This file contains the Pydantic models for the Trade entity.
"""
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class TradeType(str, Enum):
    P = "buy"
    S = "sell"
    
class Trade(BaseModel):
    type: TradeType
    symbol: str
    quantity: int
    price_per_item: float
    time_offered: datetime
    time_executed: datetime


class Position(BaseModel):
    symbol:str
    quantity:str
    money_invested:float