import os
import re
import time
import glob
import random
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
FILE_TYPE_HTM = "htm"

def get_random_wait_time():
  return random.uniform(0.5, 1.6)

def get_htm(url):
  url = url.replace("ix?doc=/", "")
  request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
  response = urllib.request.urlopen(request)
  form_response = response.read()
  return form_response

def download_forms(index_file):
  df = pd.read_csv(index_file)

  for index, row in df.iterrows():
    company_name = row["company_name"]
    company_name = "".join([c for c in company_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    company_name = re.sub(r'\W+', ' ', company_name)

    if not os.path.exists(f"./forms/{company_name}"):
      os.makedirs(f"./forms/{company_name}")

    form_url = row["form_url"]
    form = row["filing_type"]
    date = row["filing_date"]
    file_extension = form_url[-3:]
    if file_extension == FILE_TYPE_HTM:
      filename = f"./forms/{company_name}/{form}-{date}.html"
      if os.path.exists(filename):
        continue
      print(f"Downloading {company_name} {form} filed on {date}")
      form_html = get_htm(form_url)
      writer = open(filename, "wb")
      try:
        writer.write(form_html)
      except Exception as e:
        print("An error occured", e)
      finally:
        writer.close()

if __name__ == "__main__":
  start_time = time.time()
  if not os.path.exists("./forms"):
    os.makedirs("./forms")
  industry_index = "./industry-index.csv"
  # all_csv_files = ["../bank-indices/895421_index.csv"]
  download_forms(industry_index)
  print(f"Took {time.time() - start_time} seconds to download all files")
