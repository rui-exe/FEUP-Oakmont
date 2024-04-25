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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
  """
  Hash a password.
  Args:
    password: The password to hash
  Returns:
    str: The hashed password
  """
  return pwd_context.hash(password)

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
    symbol_historical = ticker.history(period='max', interval='1d')
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
        row_key = f"{symbol}_{ticker_datetime_str}"
        data[row_key.encode("utf-8")] = {
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

        if username not in data_users:
            data_users[username] = {}
        user_posts_json = json.dumps({"symbol": symbol, "post": post})
        data_users[username][f'posts:{date}'.encode('utf-8')] = user_posts_json.encode('utf-8')
       
        if symbol not in data_symbols:
            data_symbols[symbol] = {}
        symbol_posts_json = json.dumps({"username": username, "post": post})
        data_symbols[symbol][f'posts:{date}'.encode('utf-8')] = symbol_posts_json.encode('utf-8')

    populate_table(connection, 'user', data_users)
    populate_table(connection, 'financial_instruments', data_symbols)



def populate_financial_instruments(connection,symbols):
    for symbol in symbols:
        print(symbol)
        try:
            ticker = yf.Ticker(symbol)

            
            currency, longName, website = get_symbol_info(ticker)
            symbol_info = convert_yfinance_symbol_info_to_hbase_dict(connection, symbol,currency,longName, website)
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
        time_executed = convert_dmy_to_ymd(time_executed)
        time_offered = convert_dmy_to_ymd(time_offered)
        trade_json = json.dumps({ "type": type, "symbol": symbol, "quantity": quantity, "price_per_item": price_per_item, "time_offered": time_offered})
        if username not in data_trades:
            data_trades[username] = {}
        
        data_trades[username][f'trades:{time_executed}'.encode('utf-8')] = trade_json.encode('utf-8')
    populate_table(connection, 'user', data_trades)

def populate_portfolio(connection):
    users_table = connection.table('user').scan(columns=[b'trades'])
    users = list(users_table)
    for user, trades in users:
        user_stocks = {}
        for date, trade in trades.items():
            date = date.decode('utf-8')
            trade = json.loads(trade.decode('utf-8'))
            symbol = trade['symbol']
            quantity = float(trade['quantity'])
            type = trade['type']
            price_per_item = float(trade['price_per_item'])
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
        
        table.counter_set(row_key.encode('utf-8'), b'positions:quantity', int(quantity*100))
        table.counter_set(row_key.encode('utf-8'), b'positions:money_invested', int(money_invested*100))


def delete_old_score(connection, symbol, old_score):
    table = connection.table('popularity_to_instrument')
    try:
        table.delete(f"{sys.maxsize - old_score}_{symbol}".encode('utf-8'))
    except:
        pass

def populate_popularity_to_instrument(connection):

    users_table = connection.table('user').scan(columns=[b'trades'])
    users = list(users_table)
    reference_date = datetime.datetime.strptime("2020-01-01 00:00", '%Y-%m-%d %H:%M')
    for user, trades in users:
        for date, trade in trades.items():    
            data = dict()
            date = date.decode('utf-8').split(":")[1]
            date_time_obj = datetime.datetime.strptime(date + ':00', '%Y-%m-%d %H:%M')

            #get the trade information
            trade = json.loads(trade.decode('utf-8'))
            symbol, quantity = trade['symbol'], float(trade['quantity'])
            price = float(trade['price_per_item'])
            cost_of_trade = quantity * price / 100

            #calculate the timestamp score based on the number of years since 2020 plus the cost of the trade (/ (3600*24*365) converts to years)
            timestamp = ((date_time_obj - reference_date).total_seconds() + cost_of_trade) / (3600*24*365)
            score = int(timestamp * 10 ** int(timestamp))

            table = connection.table('financial_instruments')
            old_score = table.counter_get(symbol.encode('utf-8'), b'info:popularity')
            delete_old_score(connection, symbol, old_score)
            score += old_score      
            table.counter_set(symbol.encode('utf-8'), b'info:popularity', score)
            score = sys.maxsize - score

            row_key = f"{score}_{symbol}"
            data[row_key.encode("utf-8")] = {
                b'cf1:val': b'1',
            }
            


            populate_table(connection, 'popularity_to_instrument', data)
            
def read_symbols_from_csv(file_name,column_name):
    symbols = []
    with open(file_name, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            symbols.append(row[column_name])
    return symbols    

def convert_dmy_to_ymd(date):
    return datetime.datetime.strptime(date, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M')

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
