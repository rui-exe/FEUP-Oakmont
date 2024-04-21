from fastapi import APIRouter,Query,Path
from app.api.deps import HBase
from app.crud import financial_instruments as financial_instruments_crud
from app.models.financial_instruments import FinancialInstrument,Tick
from datetime import datetime,timedelta

router = APIRouter()

@router.get("/")
async def get_financial_intsruments(db:HBase) -> list[FinancialInstrument]:
  return financial_instruments_crud.get_symbols(db)

@router.get("/{symbol}")
async def get_financial_instruments_with_params(
    db: HBase,
    symbol: str = Path(..., description="Symbol of the financial instrument"),
    start_date: datetime = Query(..., description="Start date for the interval"),
    end_date: datetime = Query(..., description="End date for the interval"),
    interval: timedelta = Query(..., description="Interval for the tick data")
) -> list[Tick]:
    return financial_instruments_crud.get_instrument_prices(db, symbol, start_date, end_date, interval)