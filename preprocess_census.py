import pandas as pd


censusData = pd.read_csv("raw_data/cc-est2018-alldata.csv",  encoding = "ISO-8859-1")

# Filter for a particular year
year = 2018
censusData = censusData[(censusData['YEAR'] == year - 2007)]

print censusData.tail()
