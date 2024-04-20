from fastapi import APIRouter
from app.api.deps import HBase
from app.crud import financial_instruments as financial_insruments_crud
from app.models.financial_instruments import FinancialInstrument
router = APIRouter()

@router.get("/")
async def read_main(db:HBase) -> list[FinancialInstrument]:
  return financial_insruments_crud.get_symbols(db)
