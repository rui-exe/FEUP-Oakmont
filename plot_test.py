import happybase
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def retrieve_prices(table_name, symbol):
    connection = happybase.Connection(host='localhost', port=9090)
    table = connection.table(table_name)
    
    # Get the current date and the date one month ago
    end_date = datetime.now().date() + timedelta(microseconds=1)
    start_date = end_date - timedelta(days=30)

    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    end_key = f"{symbol}_{end_date_str}"

    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    start_key = f"{symbol}_{start_date_str}"

    prices = {}
    for key, data in table.scan(row_start=start_key.encode('utf-8'),row_stop=end_key.encode('utf-8')):
        # Extract the timestamp from the row key
        timestamp_str = key.decode('utf-8').split('_')[-1]
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').date()
        
        # Check if the timestamp is within the last month
        if start_date <= timestamp <= end_date:
            prices[timestamp] = float(data[b'series:val'])

    connection.close()
    return prices

def retrieve_name(table_name,symbol):
    connection = happybase.Connection(host='localhost', port=9090)
    table = connection.table(table_name)
    row = table.row(symbol.encode('utf-8'), columns=[b'info:name',b'info:currency'])
    name = row[b'info:name'].decode('utf-8')
    currency = row[b'info:currency'].decode('utf-8')
    return name,currency

def plot_prices(symbol,currency,prices):
    dates = list(prices.keys())
    values = list(prices.values())
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, marker='o', linestyle='-')
    plt.title(f"{symbol} Prices in the Last Month")
    plt.xlabel('Date')
    plt.ylabel(f"Price ({currency})")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    symbol = 'GOOGL'
    table_name = 'instrument_prices'
    prices = retrieve_prices(table_name, symbol)
    table_name = 'financial_instruments'
    name,currency = retrieve_name(table_name,symbol)
    plot_prices(name,currency,prices)

if __name__ == "__main__":
    main()
