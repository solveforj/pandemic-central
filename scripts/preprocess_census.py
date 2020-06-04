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

"""
Joseph's Version
"""
import pandas as pd

censusData = pd.read_csv("/Users/josephgalasso/Documents/cc-est2018-alldata.csv",  encoding = "ISO-8859-1", dtype={'STATE': str, 'COUNTY': str})
censusData['FIPS'] = censusData["STATE"] + censusData["COUNTY"]

year = 2018
censusData = censusData[(censusData['YEAR'] == year - 2007)]
censusData = censusData.loc[:, censusData.columns.isin(['FIPS','TOT_POP', 'AGEGRP','TOT_MALE'\
'TOT_FEMALE','H_MALE','H_FEMALE','BA_MALE','BA_FEMALE','IA_MALE','IA_FEMALE',\
'NA_MALE','NA_FEMALE','TOM_MALE','TOM_FEMALE'])]

newCensusData = pd.DataFrame()
uniqueFIPS = list(set(censusData['FIPS'].tolist()))

for fips in uniqueFIPS:
    # Filter censusData for fips
    fipsData = censusData[censusData['FIPS'] == fips]

    # Get total values (AGEGRP == 0) -> BASELINE
    newRow = fipsData[fipsData['AGEGRP'] == 0]
    # Get values for people >60 yrs old (AGEGRP >= 13)
    elderlyData = fipsData[fipsData['AGEGRP'] >= 13]

    # Get sum of TOT_POP variable
    elderlyPopulation = elderlyData['TOT_POP'].sum()
    newRow['ELDERLY_POP'] = [elderlyPopulation]

    # Add BASELINE as new row to newCensusData
    newCensusData = newCensusData.append(newRow, ignore_index = True)
    print type(newRow)
    print len(newCensusData)

print newCensusData

newCensusData.to_csv("/Users/josephgalasso/Documents/GitHub/pandemic-central/raw_data/census/census-" + str(year) + ".csv", sep=",", index=False)
