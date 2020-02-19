#!/usr/bin/env python
# coding: utf-8

# ## Creating the Master Index 
# An index is created which will be used to download the required earnigns documents and extract certain sections of text. The index will contain the following columns:
# * Central Index Key - SEC specific 
# * Company Name
# * Filing Type - 10-K and 10-Q are of interest to us
# * Filing Date
# * Filing URL of Text version
# * Filing URL of HTML version

import pandas as pd
import glob
import edgar
import os

def get_indices(since_year_arg):
  if not os.path.exists("./indices"):
    os.makedirs("./indices")
  download_directory = "./indices/"
  since_year = since_year_arg
  edgar.download_index(download_directory, since_year)

def prepend_sec_url(str):
  url_to_append = "https://www.sec.gov/Archives/"
  return url_to_append+str

if __name__ == "__main__":
  get_indices(2000)
  
  path = r'./indices'
  all_tsv_files = glob.glob(path + "/*.tsv")

  list_of_dfs = []

  # Read all index files as separate data frames and merge them into one data frame
  for filename in all_tsv_files:
      df = pd.read_csv(filename, 
                        sep="|",
                        header=None,
                        names=["cik", "company_name", "filing_type", "filing_date", "filing_url_txt", "filing_url_html"],
                        dtype=str)
      list_of_dfs.append(df)

  df = pd.concat(list_of_dfs, axis=0, ignore_index=True)

  # Convert the ```filing_date``` column to the datetime object and sort data by date and then company name
  pd.to_datetime(df["filing_date"])
  df = df.sort_values(["filing_date", "company_name"])

  # Prepend the URLs with the base SEC archive URL
  del df['filing_url_txt']
  df['filing_url_html'] = df['filing_url_html'].apply(prepend_sec_url)

  # Create 2 dataframes. One for 10-K filings and one for 10-Q filings and merge dataframes. Then write to disk
  master_index = df[(df.filing_type == "10-K") | (df.filing_type == "10-Q")]
  required = master_index.groupby('cik', as_index=False, group_keys=True).count()
  master_index = master_index[master_index["cik"].isin(required["cik"])]
  master_index.to_csv("./master-index.csv", index=False)
