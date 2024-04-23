import requests
import yfinance as yf 
import csv

def read_symbols_from_csv(file_name,column_name):
    symbols = []
    with open(file_name, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            symbols.append(row[column_name])
    return symbols    

def getImages():
    symbols = read_symbols_from_csv('datasets/symbols.csv','Ticker')
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            logo = ticker.info['website']
            response = requests.get('https://logo.clearbit.com/' + logo)
            with open(f'images/{symbol}.png', 'wb') as file:
                file.write(response.content)
        except Exception as e:
            print(f"Error downloading image for {symbol}: {e}")
        

getImages()