import happybase
import time
import yfinance as yf 
import datetime
import csv
import random
import time
import json
from passlib.context import CryptContext
import math
import sys
import struct

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_LONG = 2 ** 63 - 1

def get_password_hash(password: str) -> str:
  """
  Hash a password.
  Args:
    password: The password to hash
  Returns:
    str: The hashed password
  """
  return pwd_context.hash(password)

def number_to_java_long(number):
    java_long = struct.pack('>q', number)
    return java_long 
def java_long_to_number(java_long):
    # Unpack the Java long to a signed 64-bit integer
    number = struct.unpack('>q', java_long)[0]
    return number

def wait_for_hbase():
    while True:
        try:
            connection = happybase.Connection(host='localhost', port=9090)
            connection.close()
            break
        except:
            print("HBase is still initializing. Retrying in 5 seconds...")
            time.sleep(5)

def get_symbol_info(ticker):
    return ticker.info['currency'], ticker.info['longName'], ticker.info['website']

def get_historical_data_daily(ticker):
    symbol_historical = ticker.history(period='max', interval='1d', start='1970-01-01')
    return symbol_historical

def get_historical_data_hourly(ticker):
    current_date = datetime.datetime.now().date()
    one_year_ago = current_date - datetime.timedelta(days=365)

    symbol_historical = ticker.history(start=one_year_ago, end=current_date, interval='1h')
    return symbol_historical

def populate_table(connection, table_name, data):
    table = connection.table(table_name)
    print(f"Opened table {table_name}")
    with table.batch() as batch:
        for row, columns in data.items():
            batch.put(row, columns)

def convert_yfinance_symbol_info_to_hbase_dict(connection,symbol,currency,longName, website):
    data = dict()
    data[symbol.encode("utf-8")] = {
            b'info:name': longName.encode('utf-8'),
            b'info:currency': currency.encode('utf-8'),
            b'info:image': f'https://logo.clearbit.com/{website}'.encode('utf-8'),
    }
    table = connection.table('financial_instruments')
    table.counter_set(symbol.encode('utf-8'), b'info:popularity', 0)
    return data

def convert_yfinance_price_history_to_hbase_dict(symbol,yahoo_df):
    data = dict()
    for row in yahoo_df.iterrows():
        ticker_timestamp ,(high, low, close, volume, dividends, stock_splits, name) = row
        ticker_datetime = ticker_timestamp.to_pydatetime()
        ticker_datetime_str = ticker_datetime.strftime('%Y-%m-%d %H:%M:%S')
        ticker_datetime_ms = convert_ymd_to_milliseconds(ticker_datetime_str)
        ticker_datetime_ms = number_to_java_long(ticker_datetime_ms)
        row_key = f"{symbol}_".encode('utf-8') + ticker_datetime_ms
        data[row_key] = {
            b'series:val': str(close).encode('utf-8'),
        }
    return data

def delete_trades_from_user(connection, symbol, user):
    table = connection.table('user')
    trades = table.row(user, columns=[b'trades'])
    for date, trade in trades.items():
        trade = json.loads(trade.decode('utf-8'))
        if trade['symbol'] == symbol:
            table.delete(user, columns=[f'trades:{date}'.encode('utf-8')])

def populate_users(connection):
    data = dict()
    for row in csv.DictReader(open("datasets/users.csv")):
        username = row['username']
        data[username.encode("utf-8")] = {
            b'info:name': row['name'].encode('utf-8'),
            b'info:password': row['password'].encode('utf-8'),
            b'info:email': row['email'].encode('utf-8'),
        }
        table = connection.table('user')
        table.counter_set(username.encode('utf-8'), b'info:following', 0)
        table.counter_set(username.encode('utf-8'), b'info:followers', 0)
    populate_table(connection, 'user', data)

def populate_following(connection):
    table = connection.table('user')
    users = list(table.scan())
    data = dict()
    for user, columns in users:
        other_users = [u for u in users if u[0] != user]
        following = random.sample(other_users, random.randint(0, 100))
        following = [(followed_user.decode('utf-8'), _) for followed_user, _ in following]
        data[user] = {f'following:{followed_user}'.encode('utf-8'): b'1' for followed_user, _ in following}
        table.counter_set(user, b'info:following', len(following))
        for followed_user, _ in following:
            if followed_user not in data:
                data[followed_user] = {}
            user_following = user.decode('utf-8')
            data[followed_user][f'followers:{user_following}'.encode('utf-8')] = b'1'
            table.counter_inc(followed_user.encode('utf-8'), b'info:followers')

    populate_table(connection, 'user', data)

def populate_posts(connection):
    #get posts from the datasets/stock_tweets.csv Tweet column 
    users = list(connection.table('user').scan())
    data_users = dict()
    data_symbols = dict()
    for row in csv.DictReader(open("datasets/stock_tweets.csv")):
        username = random.choice(users)[0].decode('utf-8')
        post = row['Tweet']
        symbol = row['Stock Name']
        date = row['Date'].split("+")[0]
        date = MAX_LONG - convert_ymd_to_milliseconds(date)
        date = number_to_java_long(date)

        if username not in data_users:
            data_users[username] = {}
        user_posts_json = json.dumps({"symbol": symbol, "post": post})
        data_users[username][b'posts:' + date] = user_posts_json.encode('utf-8')
       
        if symbol not in data_symbols:
            data_symbols[symbol] = {}
        symbol_posts_json = json.dumps({"username": username, "post": post})
        data_symbols[symbol][b'posts:' + date] = symbol_posts_json.encode('utf-8')

    populate_table(connection, 'user', data_users)
    populate_table(connection, 'financial_instruments', data_symbols)



def populate_financial_instruments(connection,symbols):
    for symbol in symbols:
        print(symbol)
        try:
            ticker = yf.Ticker(symbol)

            
            currency, longName, website = get_symbol_info(ticker)
            symbol_info = convert_yfinance_symbol_info_to_hbase_dict(connection, symbol,currency,longName, website)
            table = connection.table('financial_instruments')
            table.counter_set(symbol.encode('utf-8'), b'info:popularity', MAX_LONG)
            populate_table(connection, 'financial_instruments', symbol_info)

            symbol_historical = get_historical_data_daily(ticker)
            symbol_historical_dict = convert_yfinance_price_history_to_hbase_dict(symbol,symbol_historical)
            populate_table(connection, 'instrument_prices', symbol_historical_dict)

            symbol_historical = get_historical_data_hourly(ticker)
            symbol_historical_dict = convert_yfinance_price_history_to_hbase_dict(symbol,symbol_historical)
            populate_table(connection, 'instrument_prices', symbol_historical_dict)
        except Exception as e:
            print(e)

def populate_trades(connection):
    users = list(connection.table('user').scan())
    symbols = set([key[0].decode('utf-8') for key in connection.table('financial_instruments').scan(columns=[])])
    data_trades = dict()
    for row in csv.DictReader(open("datasets/trades.csv")):
        username = random.choice(users)[0].decode('utf-8')
        symbol = row['Ticker']
        if (symbol not in symbols):
            continue
        type = row['Transaction Type'].split(" ")[0]
        if type == "P":
            type = "S"
        else:
            type = "P"
        quantity = int(row['Quantity'])
        if quantity < 0:
            quantity = -quantity
        price_per_item = row['Price']
        time_offered = row['Trade Date']
        time_offered = time_offered + " " + str(random.randint(0,23)) + ":" + str(random.randint(0,59))
        time_executed = row['Filing Date']
        time_executed = MAX_LONG - convert_dmy_to_milliseconds(time_executed)
        time_executed = number_to_java_long(time_executed)
        time_offered = convert_dmy_to_milliseconds(time_offered)
        time_offered = number_to_java_long(time_offered)
        trade_json = json.dumps({ "type": type, "symbol": symbol, "quantity": int(float(quantity)), "price_per_item": int(float(price_per_item)* 100), "time_offered": str(time_offered)})
        if username not in data_trades:
            data_trades[username] = {}
        
        data_trades[username][b'trades:' + time_executed] = trade_json.encode('utf-8')
    populate_table(connection, 'user', data_trades)

def populate_portfolio(connection):
    users_table = connection.table('user').scan(columns=[b'trades'])
    users = list(users_table)
    for user, trades in users:
        user_stocks = {}
        for _, trade in trades.items():
            trade = json.loads(trade.decode('utf-8'))
            symbol = trade['symbol']
            quantity = int(trade['quantity'])
            type = trade['type']
            price_per_item = int(float(trade['price_per_item']))
            if symbol not in user_stocks:
                user_stocks[symbol] = tuple([0,0])
            if type == "P":
                user_stocks[symbol] = tuple([user_stocks[symbol][0] + quantity, user_stocks[symbol][1] + quantity*price_per_item])
            else:
                user_stocks[symbol] = tuple([user_stocks[symbol][0] - quantity, user_stocks[symbol][1] - quantity*price_per_item])
        
        for symbol, (quantity, money_invested) in list(user_stocks.items()):
            if quantity < 0 or money_invested < 0:
                delete_trades_from_user(connection, symbol, user)
                del user_stocks[symbol]

        table = connection.table('portfolio')
        
        username = user.decode('utf-8')
        row_key = f'{username}_{symbol}'
        
        table.counter_set(row_key.encode('utf-8'), b'positions:quantity', quantity)
        table.counter_set(row_key.encode('utf-8'), b'positions:money_invested', money_invested)


def delete_old_score(connection, symbol, old_score):
    table = connection.table('popularity_to_instrument')
    table.delete(f"{old_score}_{symbol}".encode('utf-8'))



def populate_popularity_to_instrument(connection):
    #populate with INT_MAX popularity in every symbol
    table = connection.table('financial_instruments')
    symbols = set([key[0].decode('utf-8') for key in table.scan(columns=[])])
    for symbol in symbols:
        table.counter_set(symbol.encode('utf-8'), b'info:popularity', MAX_LONG)

    users_table = connection.table('user').scan(columns=[b'trades'])
    users = list(users_table)
    reference_date = datetime.datetime.strptime("2020-01-01 00:00", '%Y-%m-%d %H:%M')
    for user, trades in users:
        for date, trade in trades.items():    
            data = dict()
            time_executed_reverse_ms = java_long_to_number(date[len("trades:"):])
            time_executed_ms = MAX_LONG-time_executed_reverse_ms
            date_time_obj = datetime.datetime.fromtimestamp(int(time_executed_ms/1000))

            #get the trade information
            trade = json.loads(trade.decode('utf-8'))
            symbol, quantity = trade['symbol'], int(trade['quantity'])
            price = int(float(trade['price_per_item']))
            cost_of_trade = quantity * price / 100

            # double the score every 30 days and one for each order of maginute of cost_of_trade increase the order of magnitude of the score
            timestamp = ((date_time_obj - reference_date).total_seconds()) / (3600*24*30)
            score = int((cost_of_trade * 2 ** timestamp) / 1000000000)
            """
            timestamp = ((date_time_obj - reference_date).total_seconds()) / (3600*24*12)
            score = int(((cost_of_trade ** 0.5 * timestamp ** 20) ** 0.5) / 1000000000000)
            """
            table = connection.table('financial_instruments')
            new_reverse_score = table.counter_inc(symbol.encode('utf-8'), b'info:popularity', -score)
            
            old_reverse_score = new_reverse_score + score
            delete_old_score(connection, symbol, old_reverse_score)
            #get the symbol information
            symbol_info = table.row(symbol.encode('utf-8'))
            
            row_key = f"{new_reverse_score}_{symbol}"
            data[row_key.encode("utf-8")] = {
                b'info:name': symbol_info[b'info:name'],
                b'info:currency': symbol_info[b'info:currency'],
                b'info:image': symbol_info[b'info:image'],
            }
            
            populate_table(connection, 'popularity_to_instrument', data)
            
def read_symbols_from_csv(file_name,column_name):
    symbols = []
    with open(file_name, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            symbols.append(row[column_name])
    return symbols    

def convert_dmy_to_milliseconds(date):
    return int(datetime.datetime.strptime(date, '%d/%m/%Y %H:%M').timestamp() * 1000)

def convert_ymd_to_milliseconds(date):
    return int(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

def populate_tables():
    wait_for_hbase()
    print("HBase is ready!")
    # Connect to HBase
    connection = happybase.Connection(host='localhost', port=9090)
    print("Connected to HBase")
    
    
    #symbols = ['^GSPC', 'AAPL', 'GOOGL', 'MSFT', 'GME', 'NVDA' , 'KO', 'EDR', 'EDP.LS','FCP.LS']
    #symbols = read_symbols_from_csv("datasets/symbols.csv","Ticker")
    
    #shuffle to avoid hotspots
    #random.shuffle(symbols)

    #get unique Stock Name from the datasets/stock_tweets.csv
    symbols = read_symbols_from_csv("datasets/stock_tweets.csv","Stock Name")
    symbols = list(set(symbols))
    
    
    populate_financial_instruments(connection,symbols)
    populate_users(connection)
    populate_following(connection)
    populate_posts(connection)
    populate_trades(connection)
    populate_portfolio(connection)
    populate_popularity_to_instrument(connection)




if __name__ == "__main__":
    populate_tables()
