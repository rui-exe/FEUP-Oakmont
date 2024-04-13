import happybase
import time
import json

def wait_for_hbase():
    while True:
        try:
            connection = happybase.Connection(host='localhost', port=9090)
            connection.close()
            break
        except:
            print("HBase is still initializing. Retrying in 5 seconds...")
            time.sleep(5)

def populate_table(connection, table_name, data):
    table = connection.table(table_name)
    print(f"Opened table {table_name}")
    with table.batch() as batch:
        for row, columns in data.items():
            batch.put(row, columns)


def populate_tables():
    wait_for_hbase()
    print("HBase is ready!")
    # Connect to HBase
    connection = happybase.Connection(host='localhost', port=9090)
    print("Connected to HBase")

    table_name = "instrument_prices"


    data = {
        b'GOOG_2022-02-15 00:00:00': {
            b'series:val': b'130.00',
        },
        b'GOOG_2024-04-12 00:00:00': {
            b'series:val': b'160.00',
        },
        b'META_2024-04-12 00:00:00': {
            b'series:val': b'512.00',
        },
    }   
    populate_table(connection,table_name,data)


    post = {
        "author": "john_doe",
        "title": "O GOMES E O MAIOR",
        "content": "Stonks, going up",
        "created_at": "2024-04-12 00:00:00"
    }
  
    table_name = "instrument_prices"
    data = {
        b'GOOG': {
            b'info:name': b'Alphabet Inc Class C',
            b'info:currency': b'USD',
            b'info:ammount_traded': b'0',
            b'2024-04-12 00:00:00': json.dumps(post).encode('utf-8')
        }
    }
    populate_table(connection,table_name,data)
    
    table_name = "user"
    data = {
        b'john_doe':
            {
                b'info:name': b'John Doe',
                b'info:email':b'johndoe@gmail.com',
                b'info:password':b'password',
                b'info:country':b'USA',
                b'info:address':b'1234 Main St',
                b'info:balance':b'10000'
            },
        b'jane_doe':
            {
                b'info:name': b'Jane Doe',
                b'info:email':b'janedoe@gmail.com',
                b'info:password':b'password',
                b'info:country':b'USA',
                b'info:address':b'1234 Main St',
                b'info:balance':b'10000'
                },
        b'john_smith':
            {
                b'info:name': b'John Smith',
                b'info:email':b'johnsmith@gmail.com',
                b'info:password':b'password',
                b'info:country':b'USA',
                b'info:address':b'1234 Main St',
                b'info:balance':b'10000'
            }
    }

    


if __name__ == "__main__":
    populate_tables()
