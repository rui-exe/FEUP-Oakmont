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
    table_name = 'popularity_to_instrument'
    families = {
        'data': {}
    }
    connection.create_table(table_name, families)


    # Create the table instrument for prices
    table_name = 'instrument_prices'
    families = {
        'series': {}
    }
    connection.create_table(table_name, families)


    # Create table Item
    table_name = 'instrument'
    families = {
        'info':  {},
        'posts': {}
    }

    connection.create_table(table_name, families)

    # Create table User
    table_name = 'user'
    families = {
        'info': {},
        'posts': {},
        'following': {},
        'trades':  {},
        'portfolio': {}
    }

    connection.create_table(table_name, families)

    # Close the connection
    connection.close()

if __name__ == "__main__":
    create_tables()
