import glob
import sys
import time
import json
import re
import pandas as pd
from pandas.tseries.offsets import BDay
from html_to_plain_text import ConvertHTMLToPlainText
from add_labels import add_labels_to_dataset

FILE_TYPE_HTM = "htm"
CLOSE_PRICE = "4. close"
TICKER_DF = pd.read_csv("./industry-tickers.csv")
ATTEMPTS = 5

def get_ticker_symbol(cik):
  return TICKER_DF.loc[TICKER_DF['cik'] == cik]['ticker'].iloc[0]

def get_close_prices(company_prices_json, date):
  filing_date_close_price = 0
  close_price_4_weeks_after = 0

  try:
    if len(company_prices_json) < 10:
      return 0, 0
    four_weeks_after_filing_date = (pd.to_datetime(date) + BDay(20))
    running_date = pd.to_datetime(date)
    
    tries = 0
    while filing_date_close_price == 0 and tries <= ATTEMPTS:
      filing_date_prices = company_prices_json.get(running_date.strftime('%Y-%m-%d'))
      if filing_date_prices:
        filing_date_close_price = filing_date_prices[CLOSE_PRICE]
        break
      running_date = running_date + BDay(1)
      tries += 1

    running_date = four_weeks_after_filing_date

    tries = 0
    while close_price_4_weeks_after == 0 and tries <= ATTEMPTS:
      date_prices = company_prices_json.get(running_date.strftime('%Y-%m-%d'))
      if date_prices:
        close_price_4_weeks_after = date_prices[CLOSE_PRICE]
        break
      running_date = running_date + BDay(1)
      tries += 1
  
  except Exception as e:
    print(e)

  finally:  
    return filing_date_close_price, close_price_4_weeks_after

def add_data_to_csv(filename, data):
  df = pd.read_csv(filename)

  for index, row in df.iterrows():
    company_name = row["company_name"]
    company_name = "".join([c for c in company_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    ticker = get_ticker_symbol(row["cik"])

    company_name = re.sub(r'\W+', ' ', company_name)
    company_folder = company_name
    company_forms_folder = f"./forms/{company_folder}"

    company_prices_json = {}
    try:
      with open(f"./stock-price-data/{ticker}.json") as f:
        company_prices_json = json.loads(f.read())["Time Series (Daily)"]
    except Exception as e:
      print(e)

    filing_extension = row["form_url"][-3:]
    filing_type = row["filing_type"]
    filing_date = row["filing_date"]
    extracted_section = ""
    if filing_extension == FILE_TYPE_HTM:

      # getting text
      form_name = f"{company_forms_folder}/{filing_type}-{filing_date}.html"
      print(f"Extracting {company_name} {filing_date} {filing_type}")
      with open(form_name, 'r') as form_file:
          form = form_file.read()
      extracted_section = convert_html_to_plain_text.get_text_of_form(form)

      # getting stock prices
      print("  Getting stock prices")
      filing_date_close_price, close_price_4_weeks = get_close_prices(company_prices_json, filing_date)

      data.append((company_name,
                    ticker, 
                    filing_date, 
                    filing_type, 
                    filing_date_close_price,
                    close_price_4_weeks,
                    extracted_section
                  ))

if __name__ == "__main__":
  convert_html_to_plain_text = ConvertHTMLToPlainText()
  start_time = time.time()
  columns = ["company_name", 
              "ticker", 
              "filing_date", 
              "filing_type", 
              "filing_date_close_price", 
              "close_price_4_weeks", 
              "text"
            ]

  data = []
  final_filename = "./dataset-all.csv"
  filename = "./industry-index.csv"
  add_data_to_csv(filename, data)
  final_df = pd.DataFrame(data, columns=columns)
  print("Adding labels")
  add_labels_to_dataset(final_df)
  final_df.to_csv(final_filename, index=False)
  print(f"Took {time.time() - start_time} seconds to process all files")