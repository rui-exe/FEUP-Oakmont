from pydantic import BaseModel
from datetime import datetime

class FinancialInstrument(BaseModel):
    symbol: str
    name: str
    currency:str

class Tick(BaseModel):
    timestamp: datetime
    value: float 