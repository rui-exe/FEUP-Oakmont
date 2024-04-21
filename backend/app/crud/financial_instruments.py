from happybase import Connection
from app.models.financial_instruments import FinancialInstrument,Tick
from datetime import datetime,timedelta

def get_symbols(db:Connection) -> list[FinancialInstrument]:
    financial_instruments = db.table("financial_instruments")
    symbols = []
    for key, data in financial_instruments.scan():
        symbol = key.decode('utf-8')
        name = data[b'info:name'].decode('utf-8')
        currency = data[b'info:currency'].decode('utf-8')
        symbols.append({"symbol":symbol,"name": name, "currency": currency})
    
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