import pandas as pd

def census(year):
    censusData = pd.read_csv("cc-est2018-alldata.csv",  encoding = "ISO-8859-1")
    censusData = censusData[(censusData['YEAR'] == year - 2007)]
    censusData.to_csv("census-" + year + ".csv", sep=",", index=False)
    
