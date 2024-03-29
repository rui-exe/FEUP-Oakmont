import happybase
import time

def wait_for_hbase():
    while True:
        try:
            connection = happybase.Connection(host='localhost', port=9090)
            connection.close()
            break
        except:
            print("HBase is still initializing. Retrying in 5 seconds...")
            time.sleep(5)

def test_hbase():
    # Wait for HBase to initialize
    wait_for_hbase()
    print("HBase is ready!")
    # Connect to HBase
    connection = happybase.Connection(host='localhost', port=9090)
    print("Connected to HBase")
    # Create a table
    table_name = 'test_table'
    families = {
        'cf1': dict(max_versions=10),
        'cf2': dict(max_versions=1),
        'cf3': dict()
    }
    connection.create_table(table_name, families)
    print("Created table")
    # Open the table
    table = connection.table(table_name)
    print("Opened table")
    # Insert data
    data = {
        b'row1': {b'cf1:col1': b'value1', b'cf2:col2': b'value2'},
        b'row2': {b'cf1:col1': b'value3', b'cf2:col2': b'value4'},
        b'row3': {b'cf1:col1': b'value5', b'cf2:col2': b'value6'}
    }
    with table.batch() as batch:
        for row, columns in data.items():
            batch.put(row, columns)

    # Scan the table
    print("Scanning table...")
    for key, data in table.scan():
        print(key, data)

    # Delete the table
    #connection.delete_table(table_name, disable=True)

    # Close the connection
    connection.close()

if __name__ == "__main__":
    test_hbase()
