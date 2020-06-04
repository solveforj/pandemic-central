import pandas as pd

censusData = pd.read_csv("/Users/josephgalasso/Documents/cc-est2018-alldata.csv",  encoding = "ISO-8859-1")
censusData = censusData[(censusData['YEAR'] == year - 2007)]
censusData = censusData.loc[:, censusData.columns.isin(['COUNTY','TOT_POP', 'AGEGRP','TOT_MALE'\
'TOT_FEMALE','H_MALE','H_FEMALE','BA_MALE','BA_FEMALE','IA_MALE','IA_FEMALE',\
'NA_MALE','NA_FEMALE','TOM_MALE','TOM_FEMALE'])]
censusData.to_csv("/Users/josephgalasso/Documents/GitHub/pandemic-central/raw_data/census/census-" + str(year) + ".csv", sep=",", index=False)
