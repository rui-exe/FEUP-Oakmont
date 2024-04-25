from fastapi import APIRouter
from app.api.deps import HBase,CurrentUser
from app.models.financial_instruments import FinancialInstrument
from app.crud import financial_instruments as financial_instruments_crud

router = APIRouter()

@router.get("/")
async def get_financial_instruments(db:HBase) -> list[FinancialInstrument]:
  """
  Get all financial instruments
  """
  return financial_instruments_crud.get_popular_symbols(db)