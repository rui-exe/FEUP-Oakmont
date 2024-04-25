from happybase import Connection
from app.models.trades import TradePublic,Position
import json
from datetime import datetime
import struct

def java_long_to_number(java_long):
    # Unpack the Java long to a signed 64-bit integer
    number = struct.unpack('>q', java_long)[0]
    return number

def get_user_trades(db:Connection, username:str)->list[TradePublic]:
    user_table = db.table("user")
    trades = []
    for key,data in user_table.row(username.encode("utf-8"),columns=[b"trades"]).items():
        time_executed = key.decode("utf-8")[len("trades:"):]
        data = json.loads(data)
        trade = {
            "type": "buy" if data["type"]=="P" else "sell",
            "symbol": data["symbol"],
            "quantity": data["quantity"],
            "price_per_item": data["price_per_item"],
            "time_offered": datetime.strptime(data["time_offered"], "%Y-%m-%d %H:%M"),
            "time_executed": datetime.strptime(time_executed, "%Y-%m-%d %H:%M") 
        }
        trades.append(trade)
    return trades

def get_user_portfolio(db:Connection, username:str)->list[Position]:
    portfolio = db.table("portfolio")
    
    positions = []
    for row_key,data in portfolio.scan(row_prefix=username.encode("utf-8")):
        print("HERE")
        row_key_str = row_key.decode("utf-8")
        symbol = row_key_str.split("_")[1]
        quantity = java_long_to_number(data[b'positions:quantity'])
        money_invested = java_long_to_number(data[b'positions:money_invested'])

        positions.append({
            "symbol":symbol,
            "quantity": quantity,
            "money_invested": money_invested
        })
    return positions