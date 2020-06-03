import pandas as pd
# Load census population demographics data
censusData = pd.read_csv("/Users/josephgalasso/Documents/cc-est2018-alldata.csv", dtype={'STATE': str, 'COUNTY': str})

# Filter for a particular year
year = 2018
censusData = censusData[(censusData['YEAR'] == year - 2007)]

print censusData.tail()
