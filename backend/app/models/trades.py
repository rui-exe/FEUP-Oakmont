"""
  This file contains the Pydantic models for the Trade entity.
"""
from pydantic import BaseModel, ValidationError, validator
from datetime import datetime
from enum import Enum

class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TradeCreate(BaseModel):
    type: TradeType
    symbol: str
    quantity: int
    price_per_item: float
    @validator('price_per_item')
    def check_decimal_places(cls, value):
        if value != round(value, 2):
            raise ValidationError("Price must have at most 2 decimal places")
        return value
    
class TradePublic(TradeCreate):
    time_offered: datetime
    time_executed: datetime


class Position(BaseModel):
    symbol:str
    quantity:str
    money_invested:float