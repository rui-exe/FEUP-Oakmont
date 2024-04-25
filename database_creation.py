import happybase
import time

def wait_for_hbase():
    while True:
        try:
            connection = happybase.Connection(host='localhost', port=9090)
            connection.close()
            break
        except happybase.HbaseException as e:
            print("HBase is still initializing. Retrying in 5 seconds... Error: ", e)
            time.sleep(5)

def create_tables():
    # Wait for HBase to initialize
    wait_for_hbase()
    print("HBase is ready!")
    # Connect to HBase
    connection = happybase.Connection(host='localhost', port=9090)
    print("Connected to HBase")
    
    # Create a table used for conversion from financial instrument popularity to instrument
    popularity_to_instrument_table_name = 'popularity_to_instrument'
    if popularity_to_instrument_table_name.encode() not in connection.tables():
        families = {'cf1': {}}
        connection.create_table(popularity_to_instrument_table_name, families)
        print(f"Table '{popularity_to_instrument_table_name}' created.")

    # Create the table instrument for prices
    instrument_prices_table_name = 'instrument_prices'
    if instrument_prices_table_name.encode() not in connection.tables():
        families = {'series': {}}
        connection.create_table(instrument_prices_table_name, families)
        print(f"Table '{instrument_prices_table_name}' created.")

    # Create table Item
    financial_instruments_table_name = 'financial_instruments'
    if financial_instruments_table_name.encode() not in connection.tables():
        families = {'info': {}, 'posts': {}}
        connection.create_table(financial_instruments_table_name, families)
        print(f"Table '{financial_instruments_table_name}' created.")

    # Create table User
    user_table_name = 'user'
    if user_table_name.encode() not in connection.tables():
        families = {'info': {}, 'posts': {}, 'following': {}, 'followers': {},'trades': {}}
        connection.create_table(user_table_name, families)
        print(f"Table '{user_table_name}' created.")

    # Create table Portfolio
    portfolio_table_name = 'portfolio'
    if portfolio_table_name.encode() not in connection.tables():
        families = {'positions': {}}
        connection.create_table(portfolio_table_name, families)
        print(f"Table '{portfolio_table_name}' created.")

    # Close the connection
    connection.close()

if __name__ == "__main__":
    create_tables()
