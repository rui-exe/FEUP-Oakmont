from happybase import Connection
from app.models.trades import TradePublic,Position
import json
from datetime import datetime
import struct

LONG_MAX = 2**63 - 1 

def java_long_to_number(java_long):
    # Unpack the Java long to a signed 64-bit integer
    number = struct.unpack('>q', java_long)[0]
    return number

def get_user_trades(db:Connection, username:str)->list[TradePublic]:
    user_table = db.table("user")
    trades = []
    for key,data in user_table.row(username.encode("utf-8"),columns=[b"trades"]).items():
        data = json.loads(data)
        time_executed_reverse_ms = java_long_to_number(key[len("trades:"):])
        time_executed_ms = LONG_MAX-time_executed_reverse_ms

        print(data)
        trade = {
            "type": "buy" if data["type"]=="P" else "sell",
            "symbol": data["symbol"],
            "quantity": data["quantity"],
            "price_per_item": data["price_per_item"]/100,
            "time_executed": datetime.fromtimestamp(int(time_executed_ms/1000))
        }
        trades.append(trade)
    return trades

def get_user_portfolio(db:Connection, username:str)->list[Position]:
    portfolio = db.table("portfolio")
    
    positions = []
    for row_key,data in portfolio.scan(row_prefix=username.encode("utf-8")):
        row_key_str = row_key.decode("utf-8")
        symbol = row_key_str.split("_")[1]
        quantity = java_long_to_number(data[b'positions:quantity'])
        money_invested = java_long_to_number(data[b'positions:money_invested'])

        positions.append({
            "symbol":symbol,
            "quantity": quantity,
            "money_invested": money_invested/100
        })
    return positions