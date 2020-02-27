import pandas as pd 
from bs4 import BeautifulSoup
import urllib.request
import time
import random
import os

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
URL_TO_PREPEND = "https://www.sec.gov"

def create_index_with_cik(cik, companies):
  company_df = pd.DataFrame()
  try:
    company_df = companies.loc[companies["cik"] == cik]
    company_name = company_df.iloc[-1]["company_name"]
    company_name = "".join([c for c in company_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()

    form_urls = []
    industry = []
    r, c = company_df.shape
    
    print(f"Getting form urls for: {company_name}")
    for index, row in company_df.iterrows():
      filing_url = row["filing_url_html"]
      
      request = urllib.request.Request(filing_url,headers={"User-Agent": USER_AGENT})
      response = urllib.request.urlopen(request)
      filing_html = response.read()

      soup = BeautifulSoup(filing_html, features="html.parser")
      table = soup.find( "table", {"summary":"Document Format Files"})
      table_rows = table.findAll(lambda tag: tag.name=="tr")

      company_info = soup.find("div", {"id":"filerDiv"})
      company_sic = company_info.find("acronym", {"title": "Standard Industrial Code"})
      info = []
      for tag in company_sic.next_elements:
        if not tag.string:
          break
        info.append(tag.string.strip())
      print(company_name, info[-1])
      industry.append(info[-1])
      
      for table_row in table_rows:
        cells = table_row.findChildren('td')
        if (cells != []):
          if (cells[3].string == "10-K" or cells[3].string == "10-Q"):
            cell = cells[2]
            form_url = URL_TO_PREPEND+ cell.find("a").get("href")
            form_urls.append(form_url)
            break
      
    print("Number of forms: ",len(form_urls))
    company_df.insert(c, "form_url", form_urls)
    company_df.insert(c, "industry", industry)
    company_df.to_csv(f"./indices/{company_name}.csv", index=False)
  except Exception as e:
    print(e)
  finally:
    return company_df

if __name__ == "__main__":
  program_start_time = time.time()
  companies = pd.read_csv("../master-index.csv")
  all_ciks = companies["cik"].unique()
  # all_ciks = [73124]
  all_company_dfs = []

  if not os.path.exists("./indices"):
    os.makedirs("./indices")
  
  for cik in all_ciks:
    start_time = time.time()
    company_df = create_index_with_cik(cik, companies)
    all_company_dfs.append(company_df)
    print(f"Took {time.time() - start_time} seconds to retrieve")

  print("Merging datasets and writing to file")
  df = pd.concat(all_company_dfs, axis=0, ignore_index=True)
  df.to_csv("./all-companies-index.csv", index=False)
  print(f"Finsihed in {time.time()- program_start_time} seconds")

