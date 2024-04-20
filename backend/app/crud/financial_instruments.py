from happybase import Connection
from app.models.financial_instruments import FinancialInstrument

def get_symbols(db:Connection) -> list[FinancialInstrument]:
    table = db.table("financial_instruments")
    symbols = []
    for key, data in table.scan():
        symbol = key.decode('utf-8')
        name = data[b'info:name'].decode('utf-8')
        currency = data[b'info:currency'].decode('utf-8')
        symbols.append({"symbol":symbol,"name": name, "currency": currency})
    
    return symbols