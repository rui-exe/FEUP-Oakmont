import happybase

def scan_all_tables(host='localhost', port=9090):
    connection = happybase.Connection(host=host, port=port)
    try:
        # List all tables
        tables = connection.tables()
        
        for table_name in tables:
            print(f"Scanning table: {table_name}")
            table = connection.table(table_name)
            # Scan table and print row data
            for key, data in table.scan():
                print(f"Row key: {key}, Data: {data}")
    finally:
        connection.close()

if __name__ == "__main__":
    scan_all_tables()

