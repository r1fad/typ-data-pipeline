#!/usr/bin/env python
# coding: utf-8

# Need to get forms for a particular industry/set of industries.
# In my case, I would need forms from banks and other financial service companies
import pandas as pd
import numpy as np
import re
pd.set_option("display.max_rows",500)

if __name__ == "__main__":
    df = pd.read_csv("all-companies-index.csv")
    df['company_name'] = df['company_name'].map(lambda x: re.sub(r'\W+', ' ', x))
    all_industries = df.groupby(["industry"]).count()
    all_industries = all_industries.rename(columns={"Unnamed: 0":"count"})
    all_industries.sort_values("count", ascending=False, inplace=True)
    # display(all_industries.head(10))

    required_industries = ["Security Brokers, Dealers & Flotation Companies",
                        "Finance Services", "National Commercial Banks", " State Commercial Banks"]
    required_df = df[df["industry"].isin(required_industries)]
    stats = required_df.groupby("company_name", as_index=False).count().rename(columns={"Unnamed: 0":"count"})
    # display(stats)

    all_tickers = pd.read_csv("company-tickers.csv")
    ciks = required_df["cik"].unique()
    tickers = all_tickers[all_tickers["cik"].isin(ciks)].drop_duplicates("title")
    # display(tickers)

    ticker_ciks = tickers['cik'].unique()
    missing_ciks = np.setdiff1d(ciks, ticker_ciks)
    print("Couldn't find tickers for: ")
    missing_companies = required_df[required_df["cik"].isin(missing_ciks)]["company_name"].unique()
    for company in missing_companies:
        print(company)
        
    tickers.to_csv("./industry-tickers.csv", index=False)

    # required_df = required_df.drop("Unnamed: 0", axis=1)
    required_df = required_df.drop(required_df[required_df["cik"].isin(missing_ciks)].index)
    print("Total number of companies: ", required_df["cik"].unique().size)
    print("Total number of forms: ", required_df["filing_url_html"].size)
    print("Earliest form filed", required_df["filing_date"].min())
    print("Latest form filed", required_df["filing_date"].max())
    form_stats = required_df.groupby("filing_type", as_index=False).count().rename(columns={"Unnamed: 0": "count"})
    # display(form_stats[["filing_type", "cik"]])
    required_df = required_df.sort_values("company_name")
    required_df.to_csv("./industry-index.csv", index=False)
