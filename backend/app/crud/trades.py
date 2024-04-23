from happybase import Connection
from app.models.trades import Trade,Position
import json
from datetime import datetime
def get_user_trades(db:Connection, username:str)->list[Trade]:
    user_table = db.table("user")
    trades = []
    for key,data in user_table.row(username.encode("utf-8"),columns=[b"trades"]).items():
        time_executed = key.decode("utf-8")[len("trades:"):]
        data = json.loads(data)
        trade = {
            "type": data["type"],
            "symbol": data["symbol"],
            "quantity": data["quantity"],
            "price_per_item": data["price_per_item"],
            "time_offered": datetime.strptime(data["time_offered"], "%Y-%m-%d %H:%M"),
            "time_executed": datetime.strptime(time_executed, "%Y-%m-%d %H:%M") 
        }
        trades.append(trade)
    print(trades)
    return trades
def get_user_portfolio(db:Connection, username:str)->list[Position]:
    pass