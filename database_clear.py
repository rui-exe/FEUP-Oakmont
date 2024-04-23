import happybase

def delete_all_tables(host='localhost', port=9090):
    # Connect to HBase
    connection = happybase.Connection(host=host, port=port)

    try:
        # Get list of tables
        tables = connection.tables()

        # Iterate over tables and delete them
        for table in tables:
            connection.disable_table(table)
            connection.delete_table(table, disable=True)
            print(f"Deleted table: {table}")

    finally:
        # Close the connection
        connection.close()

if __name__ == "__main__":
    delete_all_tables()
