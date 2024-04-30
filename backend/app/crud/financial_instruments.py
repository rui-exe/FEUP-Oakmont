from happybase import Connection
from app.models.financial_instruments import FinancialInstrument,Tick
from datetime import datetime,timedelta
from fastapi import HTTPException

def get_symbols(db:Connection) -> list[FinancialInstrument]:
    financial_instruments = db.table("financial_instruments")
    symbols = []
    for key, data in financial_instruments.scan():
        symbol = key.decode('utf-8')
        name = data[b'info:name'].decode('utf-8')
        currency = data[b'info:currency'].decode('utf-8')
        image = data[b'info:image'].decode('utf-8')
        symbols.append({"symbol":symbol,"name": name, "currency": currency, "image": image})
    
    return symbols


def get_instrument_prices(db:Connection, symbol:str, start_date:datetime, end_date:datetime, interval:timedelta)->list[Tick]:
    instrument_prices = db.table("instrument_prices")
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    row_start = f"{symbol}_{start_date_str}"
    end_date = end_date + timedelta(microseconds=1)
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    row_stop = f"{symbol}_{end_date_str}"
    
    ticks = []
    for row_key,data in instrument_prices.scan(row_start = row_start.encode("utf-8"), row_stop = row_stop.encode("utf-8")):
        row_key_str = row_key.decode("utf-8")
        timestamp_str = row_key_str.split("_")[1]
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        ticks.append({
            "timestamp":timestamp,
            "value": data[b'series:val'].decode('utf-8')
        })
    return ticks

def get_popular_symbols(db:Connection) -> list[FinancialInstrument]:
    popular_symbols = db.table("popularity_to_instrument")
    symbols = []
    #get the top 10 and the infor from the popularity table
    for key, data in popular_symbols.scan(limit=10):
        symbol = key.decode('utf-8').split("_")[1]
        name = data[b'info:name'].decode('utf-8')
        currency = data[b'info:currency'].decode('utf-8')
        image = data[b'info:image'].decode('utf-8')
        symbols.append({"symbol":symbol,"name": name, "currency": currency, "image": image})
            
    return symbols

def get_symbol_info(db:Connection, symbol:str) -> FinancialInstrument:
    financial_instruments = db.table("financial_instruments")
    data = financial_instruments.row(symbol.encode("utf-8"))
    if not data:
        raise HTTPException(status_code=404, detail="Symbol not found")
    name = data[b'info:name'].decode('utf-8')
    currency = data[b'info:currency'].decode('utf-8')
    image = data[b'info:image'].decode('utf-8')
    return FinancialInstrument(symbol=symbol,name=name,currency=currency,image=image)

def get_most_recent_price(db:Connection, symbol:str) -> Tick:
    instrument_prices = db.table("instrument_prices")
    row_key_prefix = f"{symbol}_".encode("utf-8")
    
    data = list(instrument_prices.scan(row_prefix=row_key_prefix, limit=1, reverse=True))
    if not data:
        raise HTTPException(status_code=404, detail="Symbol not found")
    timestamp_str = data[0][0].decode("utf-8").split("_")[1]
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    return Tick(timestamp=timestamp, value=float(data[0][1][b"series:val"].decode("utf-8")))  