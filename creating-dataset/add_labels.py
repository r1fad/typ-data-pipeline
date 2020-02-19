import pandas as pd 
import numpy
import matplotlib.pyplot as plt

def add_labels_to_dataset(df):
  labels = []
  percent_change = df['close_price_4_weeks'].astype(float) / df['filing_date_close_price'].astype(float)
  labels = pd.qcut(percent_change, 3,labels=["SELL", "HOLD", "BUY"])
  df["label"] = labels

if __name__ == "__main__":
  filename = "./dataset.csv"
  df = pd.read_csv(filename)
  if 'label' in df.columns:
    df.drop("label", axis=1)
  print("Labelling data")
  add_labels_to_dataset(df)
  df.to_csv(filename, index=False)