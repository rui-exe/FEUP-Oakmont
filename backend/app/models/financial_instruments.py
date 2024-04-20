from pydantic import BaseModel

class FinancialInstrument(BaseModel):
    symbol: str
    name: str
    currency:str