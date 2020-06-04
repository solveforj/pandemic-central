import pandas as pd

censusData = pd.read_csv("/Users/josephgalasso/Documents/cc-est2018-alldata.csv",  encoding = "ISO-8859-1", dtype={'STATE': str, 'COUNTY': str})
censusData.insert(loc = 0, column = "FIPS", value = censusData["STATE"] + censusData["COUNTY"])

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

newCensusData = newCensusData.drop(['AGEGRP'], axis=1)
print newCensusData

newCensusData.to_csv("/Users/josephgalasso/Documents/GitHub/pandemic-central/raw_data/census/census-" + str(year) + ".csv", sep=",", index=False)
