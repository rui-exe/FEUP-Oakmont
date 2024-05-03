import requests
from datetime import datetime
import happybase
import struct
import time 
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_last_price(symbol, token):
    try:
        url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={token}"
        response = requests.get(url)
        data = response.json()
        last_price = data['latestPrice']
        return last_price
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def number_to_java_long(number):
    java_long = struct.pack('>q', number)
    return java_long 

def update_instrument_price(connection, symbol, price):
    try:
        table = connection.table('instrument_prices')
        # Generate a row key using the current timestamp
        current_time_ms = int(datetime.now().timestamp() * 1000)
        row_key = f"{symbol}_".encode('utf-8') + number_to_java_long(current_time_ms)
        # Store the price in the 'series:val' column
        table.put(row_key, {b'series:val': str(price).encode('utf-8')})
        print(f"Updated price of {symbol} to {price} with row key {row_key}")
        
    except Exception as e:
        print(f"Error occurred while updating instrument price: {e}")

if __name__ == "__main__":
    symbol = "META"  # Example symbol
    # Get the API token from environment variables
    token = os.getenv('IEX_CLOUD_API_TOKEN')
    
    try:
        while True:
            connection = happybase.Connection(host='localhost', port=9090)
            print("Connected to HBase")
            # Get the latest price
            last_price = get_last_price(symbol, token)
            if last_price is not None:
                # Update the instrument price in the HBase table
                update_instrument_price(connection, symbol, last_price)
            # Wait for 1 minute before the next update
            connection.close()
            time.sleep(60)
    except KeyboardInterrupt:
        print("Exiting...")
