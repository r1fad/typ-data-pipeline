from urllib import request
import json
import pandas as pd
import time
import os
import config

API_KEY = config.ALPHAVANTAGE_API_KEY
API_BASE_URL = "https://www.alphavantage.co/query"

OUTPUT_SIZE_FULL = "full"
OUTPUT_SIZE_COMPACT = "compact"
TIME_SERIES_DAILY = "TIME_SERIES_DAILY"

DATATYPE_JSON = "json"
DATATYPE_CSV = "csv"

def construct_url(ticker, output_size=OUTPUT_SIZE_COMPACT):
  function = f"function={TIME_SERIES_DAILY}"
  symbol = f"symbol={ticker}"
  apikey = f"apikey={API_KEY}"
  outputsize = f"outputsize={output_size}"
  query_url = f"{API_BASE_URL}?{function}&{symbol}&{outputsize}&{apikey}"
  return query_url

def get_time_series_daily(ticker):
  filename = f'./stock-price-data/{ticker}.json'
  if os.path.exists(filename):
    return False

  url = construct_url(ticker, OUTPUT_SIZE_FULL)
  content = request.urlopen(url).read()
  data = json.loads(content)
  with open(filename, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
  return True

if __name__ == "__main__":
  ticker_df = pd.read_csv("./industry-tickers.csv")
  tickers = ticker_df["ticker"]
  if not os.path.exists("./stock-price-data"):
    os.makedirs("./stock-price-data")
  count = 0
  for ticker in tickers:
    if count % 5 == 0 and count != 0:
      print("5 requests made, waiting 60 seconds...")
      time.sleep(60)
    print(f"Getting historical data for {ticker}")
    request_made = get_time_series_daily(ticker)
    if request_made:
      count += 1