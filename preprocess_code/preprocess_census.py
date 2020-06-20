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

newCensusData = newCensusData.drop(['AGEGRP'], axis=1)


county_sizes = pd.read_csv("raw_data/census/county_size.csv", dtype={'State-County FIPS Code':str}, encoding="ISO-8859-1")
county_sizes = county_sizes.rename({'State-County FIPS Code': 'FIPS', 'Land Area (square miles), 2010':'Land Area'}, axis=1)
county_sizes['Land Area'] = county_sizes['Land Area'].apply(lambda x : float(x.replace(",", "")))
individual_sizes = pd.DataFrame(county_sizes.groupby('FIPS')['Land Area'].apply(lambda x: x.sum()))
individual_sizes.insert(0,'FIPS', individual_sizes.index)
individual_sizes = individual_sizes.reset_index(drop=True)

#newCensusData = pd.read_csv('raw_data/census/census-2018.csv', sep=",", dtype={'FIPS':str})
mergedDF = pd.merge(left=newCensusData, right=individual_sizes, how='left', on='FIPS', copy=False)
mergedDF[mergedDF.columns[1:]] = mergedDF[mergedDF.columns[1:]].astype(float)
mergedDF[mergedDF.columns[2:-1]] = mergedDF[mergedDF.columns[2:-1]].div(mergedDF['TOT_POP'], axis=0)
mergedDF.insert(1, "POP_DENSITY", mergedDF['TOT_POP']/mergedDF['Land Area'])
mergedDF = mergedDF.drop(['TOT_POP', 'Land Area'], axis=1)

mergedDF.to_csv("raw_data/census/census-2018.csv", index=False)
print(mergedDF)
