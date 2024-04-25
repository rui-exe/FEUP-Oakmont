from fastapi import APIRouter, HTTPException
from app.api.deps import TradeExecutor,CurrentUser
from app.models.trades import TradeCreate, TradeType as ModelTradeType
from app.hbase_client.hbase_client_pb2 import Trade,TradeType as HBaseClientTradeType,TradeResult,TradeResultType
from typing import Any
import time

router = APIRouter()

@router.post("/")
async def execute_trade(trade: TradeCreate, trade_executor: TradeExecutor,current_user: CurrentUser) -> Any:
    trade_message = Trade(
        username=current_user.username,
        type=HBaseClientTradeType.BUY if trade.type==ModelTradeType.BUY else HBaseClientTradeType.SELL,
        symbol=trade.symbol,
        quantity=trade.quantity,
        price_per_item=int(trade.price_per_item * 100),
        time_offered=int(round(time.time() * 1000)),
        time_executed=int(round(time.time() * 1000))
    )

    if trade.type == trade.type==ModelTradeType.BUY:
        execute_trade_RPC = trade_executor.executeBuyTrade
    elif trade.type == trade.type==ModelTradeType.SELL:
        execute_trade_RPC = trade_executor.executeSellTrade
    else:
        raise HTTPException(status_code=400, detail="Invalid trade type")

    try:
        result:TradeResult = execute_trade_RPC(trade_message)
        result_type:TradeResultType = result.result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    if result_type == TradeResultType.TRADE_EXECUTED_SUCCESFULLY:
        return {"message": "Trade executed successfully"}
    elif result_type == TradeResultType.WRONG_TRADE_TYPE:
        raise HTTPException(status_code=400, detail="Wrong trade type")
    elif result_type == TradeResultType.NOT_ENOUGH:
        raise HTTPException(status_code=400, detail="Not enough")
    elif result_type == TradeResultType.UNEXPECTED_SERVER_ERROR:
        raise HTTPException(status_code=500, detail="Unexpected server error")
    else:
        raise HTTPException(status_code=500, detail="Unknown result")
