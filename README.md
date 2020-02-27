## A tool to create a dataset for 10K and 10Q earnings documents
This tool is used as part of my Third Year Project at the University of Manchester.
It outputs a dataset containing earnings documents from the year 2000 to 2019 of companies
specified in ```industry-index.csv``` along with their filing date, stock price on the day of filing, stock price 4 weeks after filing and label which can be either one of 'BUY', 'HOLD' or 'SELL'

## How to run the tool
There are various scripts that have to be run manually for the dataset to be created. Ideally these list of commands would be one command that takes in a set of arguments like the list of companies and date range but for now, those features are for future work.

There is a known issue in MacOS High Sierra and above which prevents the module python-edgar from running because it uses multithreading.
To get around, please set the following variable in your terminal environment before running the rest of the commands:
```
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

Install the required modules first.
```
pip3 install -r requirements.txt
```

Create the master index of companies that file with the Secuirities Exchange Commission. The URLs in this index point to filing page of a particular company, not the earnings document itself
```
python3 create-master-index.py
```

Create the index containing URLs pointing to the documents themselves and add the Industry that each company is part of
```
cd creating-dataset && python3 create-form-index.py
```

Create an index containing companies that belong to industries of your interest. This involves editing ```create-index-for-industry.py``` and adding the industries that you'd like. Make sure to use the industry names provided by the SEC.
```
python3 create-industry-index.py
```

Download the forms belonging to the industries of your interest
```
python3 download-forms.py
```

Download stock price information
```
python3 get-stock-prices.py
```

Finally, create the dataset
```
python3 create-dataset.py
```


