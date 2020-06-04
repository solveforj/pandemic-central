"""
This module reads original Census data of 2010-2018 into Pandas dataframe and
saves as new dataset with only needed data.
"""

import pandas as pd

# Load dataset into Pandas dataframe
censusData = pd.read_csv("/Users/josephgalasso/Documents/cc-est2018-alldata.csv",\
  encoding = "ISO-8859-1")

censusData = censusData[(censusData['YEAR'] == year - 2007)]

#Only keeps the needed columns
censusData = censusData.loc[:, censusData.columns.isin(['COUNTY','TOT_POP',\
 'AGEGRP','TOT_MALE', 'TOT_FEMALE','H_MALE','H_FEMALE','BA_MALE','BA_FEMALE',\
 'IA_MALE','IA_FEMALE','NA_MALE','NA_FEMALE','TOM_MALE','TOM_FEMALE'])]

# Export as new csv dataset
censusData.to_csv("raw_data/census/" + 'census-' + str(year) + \
 ".csv", sep=",", index=False)
