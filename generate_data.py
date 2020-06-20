import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
from urllib.request import urlopen
import io
from datetime import datetime
import numpy as np
from preprocess import get_latest_file
from datetime import date


def preprocess_census(year = 2018):
    # Import census data file (in Github folder)
    censusFile = os.path.split(os.getcwd())[0] + "/cc-est2018-alldata.csv"
    censusData = pd.read_csv(censusFile,  encoding = "ISO-8859-1", dtype={'STATE': str, 'COUNTY': str})
    censusData.insert(loc = 0, column = "FIPS", value = censusData["STATE"] + censusData["COUNTY"])

    # Filter data for year and minority populations
    censusData = censusData[(censusData['YEAR'] == year - 2007)]
    censusData = censusData.loc[:, censusData.columns.isin(['FIPS','TOT_POP', 'AGEGRP','TOT_MALE'\
    'TOT_FEMALE','H_MALE','H_FEMALE','BA_MALE','BA_FEMALE','IA_MALE','IA_FEMALE',\
    'NA_MALE','NA_FEMALE','TOM_MALE','TOM_FEMALE'])]

    # Add population of elderly in each county
    newCensusData = censusData[censusData['AGEGRP'] == 0].reset_index(drop=True)
    elderlyData = censusData[censusData['AGEGRP'] >= 13]
    elderlyPopulation = elderlyData.groupby('FIPS')['TOT_POP'].sum().reset_index(drop=True)
    newCensusData['ELDERLY_POP'] = elderlyPopulation
    newCensusData = newCensusData.drop(['AGEGRP'], axis=1)

    # Normalize data by county size
    county_sizes = pd.read_csv("raw_data/census/county_size.csv", dtype={'State-County FIPS Code':str}, encoding="ISO-8859-1")
    county_sizes = county_sizes.rename({'State-County FIPS Code': 'FIPS', 'Land Area (square miles), 2010':'Land Area'}, axis=1)
    county_sizes['Land Area'] = county_sizes['Land Area'].apply(lambda x : float(x.replace(",", "")))
    individual_sizes = pd.DataFrame(county_sizes.groupby('FIPS')['Land Area'].apply(lambda x: x.sum()))
    individual_sizes.insert(0,'FIPS', individual_sizes.index)
    individual_sizes = individual_sizes.reset_index(drop=True)

    # Make final dataframe
    mergedDF = pd.merge(left=newCensusData, right=individual_sizes, how='left', on='FIPS', copy=False)
    mergedDF[mergedDF.columns[1:]] = mergedDF[mergedDF.columns[1:]].astype(float)
    mergedDF[mergedDF.columns[2:-1]] = mergedDF[mergedDF.columns[2:-1]].div(mergedDF['TOT_POP'], axis=0)
    mergedDF.insert(1, "POP_DENSITY", mergedDF['TOT_POP']/mergedDF['Land Area'])
    mergedDF = mergedDF.drop(['TOT_POP', 'Land Area'], axis=1)
    mergedDF.to_csv("raw_data/census/census-2018.csv", index=False)

def preprocess_disparities():
    disparities = pd.read_csv("raw_data/disparities/CCVI.csv", dtype={"FIPS":str})
    disparities = disparities[disparities.columns[3:-2]].sort_values('FIPS').reset_index(drop=True)
    disparities.to_csv("raw_data/disparities/disparities.csv", sep=",", index=False)

def preprocess_facebook(online=False):
    link = "https://data.humdata.org/dataset/movement-range-maps"
    page = requests.get(link).content
    soup = BeautifulSoup(page, 'html.parser')
    dataLink = soup.find_all('a', {"class": "btn btn-empty btn-empty-blue hdx-btn resource-url-analytics ga-download"}, href=True)[0]['href']
    dataLink = "https://data.humdata.org" + dataLink

    dataFile = dataLink.split("/")[-1].split(".")[0].replace("-data", "") + ".txt"
    print(dataLink)
    print(dataFile)

    if online == True:
        z = urlopen(dataLink)
        myzip = ZipFile(BytesIO(z.read()))
        print(myzip.infolist())
        df = pd.read_csv(myzip.open(dataFile), sep='\t', dtype={'polygon_id':str})
    else:
        path = os.path.split(os.getcwd())[0] + "/" + dataFile
        df = pd.read_csv(path, sep=',', dtype={'polygon_id':str})
    print(df)
    df = df[df['country'] == 'USA']
    #df.to_csv("raw_data/facebook/facebook_raw.csv", sep=',', index=False)
    #df = pd.read_csv("raw_data/facebook/facebook_raw.csv", dtype={'polygon_id':str})
    df = df[['ds', 'polygon_id', 'all_day_bing_tiles_visited_relative_change', 'all_day_ratio_single_tile_users']]
    df = df.rename({'polygon_id':'FIPS','ds':'date','all_day_bing_tiles_visited_relative_change':'fb_movement_change', 'all_day_ratio_single_tile_users':'fb_stationary'}, axis=1)
    df = df.reset_index(drop=True)

    df['fb_movement_change'] = pd.Series(df.groupby("FIPS")['fb_movement_change'].rolling(7).mean()).reset_index(drop=True)
    df['fb_stationary'] = pd.Series(df.groupby("FIPS")['fb_stationary'].rolling(7).mean()).reset_index(drop=True)

    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].apply(pd.DateOffset(1))
    df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df = df.dropna()
    df.to_csv('raw_data/facebook/facebook.csv', sep=',', index=False)

def preprocess_diabetes():
    diabetesData = pd.read_csv("/Users/josephgalasso/Documents/IHME_USA_COUNTY_DIABETES_PREVALENCE_1999_2012/IHME_Diabetes.csv")
    diabetesData = diabetesData[diabetesData['FIPS'] > 100]
    diabetesData = diabetesData.loc[:, diabetesData.columns.isin(['FIPS', 'Location', 'Prevalence, 2012, Both Sexes'])]
    diabetesData.rename(columns={'Prevalence, 2012, Both Sexes': 'Diabetes_Prevalence_Both_Sexes', }, inplace=True)
    diabetesData['FIPS'] = diabetesData['FIPS'].apply(lambda x: str(int(x)))

    diabetesData = diabetesData.reset_index(drop=True)
    return diabetesData

def preprocess_obesity():
    obesityData = pd.read_csv("/Users/josephgalasso/Documents/IHME_USA_OBESITY_PHYSICAL_ACTIVITY_2001_2011.csv",dtype={'fips': str})
    obesityData = obesityData[obesityData['Outcome'] == 'Obesity']
    obesityData = obesityData.loc[:, obesityData.columns.isin(['merged_fips', 'Sex', 'Prevalence 2011 (%)'])]

    maleObesityData = obesityData[obesityData['Sex'] == "Male"]
    maleObesityData.rename(columns={'Prevalence 2011 (%)': 'Male_Obesity_%', 'merged_fips':'fips'}, inplace=True)
    maleObesityData = maleObesityData.drop(['Sex'], axis=1).reset_index(drop=True)

    femaleObesityData = obesityData[obesityData['Sex'] == "Female"]
    femaleObesityData.rename(columns={'Prevalence 2011 (%)': 'Female_Obesity_%', 'merged_fips':'fips'}, inplace=True)
    femaleObesityData = femaleObesityData.drop(['Sex'], axis=1).reset_index(drop=True)

    mergedDF = pd.merge(left=maleObesityData, right=femaleObesityData, how='left', on='fips')
    mergedDF.rename(columns={'fips': 'FIPS', }, inplace=True)
    return mergedDF

def preprocess_mortality():
    mortalityData = pd.read_csv("/Users/josephgalasso/Documents/IHME_Mortality.csv")
    mortalityData = mortalityData[mortalityData['FIPS'] > 100.0]
    columns = mortalityData.columns[1:]
    for i in columns:
        mortalityData[i] = mortalityData[i].apply(lambda x : float(x.split(" ")[0]))
    mortalityData = mortalityData.reset_index(drop=True)
    mortalityData['FIPS'] = mortalityData['FIPS'].apply(lambda x : str(int(x)))

    return mortalityData

def preprocess_infectious_disease_mortality():
    mortalityData = pd.read_csv("/Users/josephgalasso/Documents/IHME_Infections_Disease_Mortality.csv")
    mortalityData = mortalityData[mortalityData['FIPS'] > 100.0]
    columns = mortalityData.columns[1:]
    for i in columns:
        mortalityData[i] = mortalityData[i].apply(lambda x : float(x.split(" ")[0]))
    mortalityData = mortalityData.reset_index(drop=True)
    mortalityData['FIPS'] = mortalityData['FIPS'].apply(lambda x : str(int(x)))
    return mortalityData

def preprocess_respiratory_disease_mortality():
    mortalityData = pd.read_csv("/Users/josephgalasso/Documents/IHME_Respiratory_Disease.csv")
    mortalityData = mortalityData[mortalityData['FIPS'] > 100.0]
    columns = mortalityData.columns[1:]
    for i in columns:
        mortalityData[i] = mortalityData[i].apply(lambda x : float(x.split(" ")[0]))
    mortalityData = mortalityData.reset_index(drop=True)
    mortalityData['FIPS'] = mortalityData['FIPS'].apply(lambda x : str(int(x)))
    return mortalityData

def process_fips():
        fipsData = pd.read_csv("raw_data/health_data/all-geocodes-v2017.csv", dtype={'State Code (FIPS)': str, 'County Code (FIPS)': str}, encoding="ISO-8859-1")

        # Map 040 level fips code to state name in dictionary
        stateData = fipsData[fipsData['Summary Level'] == 40]
        stateMap = pd.Series(stateData['Area Name (including legal/statistical area description)'].values,index=stateData['State Code (FIPS)']).to_dict()

        # Get all county fips codes
        fipsData = fipsData[fipsData['Summary Level'] == 50]
        fipsData.insert(0, 'FIPS', fipsData['State Code (FIPS)'] + fipsData['County Code (FIPS)'])

        def make_identifier(a, b):
            state = stateMap[a[:2]]
            county = b.split(" ")
            county = county[0]

            return state + " " + county

        fipsData['Identifier'] = fipsData.apply(lambda row : make_identifier(row['FIPS'], row['Area Name (including legal/statistical area description)']), axis=1)
        fipsMap = pd.Series(fipsData['FIPS'].values, index=fipsData['Identifier']).to_dict()

        return fipsMap

fipsMap = process_fips()

def smoking_identifier(a, b):
    county = b.split(" ")[0]
    state = a
    id = state + " " + county
    try:
        fips = fipsMap[id]
        return fips
    except KeyError:
        fips = 'NA'
        return fips

def preprocess_smoking_prevalence():
    smokingData = pd.read_csv("/Users/josephgalasso/Documents/IHME_US_COUNTY_TOTAL_AND_DAILY_SMOKING_PREVALENCE_1996_2012/IHME_US_COUNTY_TOTAL_AND_DAILY_SMOKING_PREVALENCE_1996_2012.csv")
    smokingData = smokingData[(smokingData['sex'] == 'Both') & (smokingData['year'] == 2012) & (smokingData['county'].notnull())]

    smokingData.insert(0, "fips", smokingData.apply(lambda row : smoking_identifier(row['state'], row['county']), axis=1))

    smokingData = smokingData.reset_index(drop=True)
    #Five rows of smokingData had NA values for the FIPS.  These are manually added in
    #print smokingData[smokingData['fips'] == 'NA']
    smokingData.iat[88,10] = "02158"
    smokingData.iat[309,10] = "11001"
    smokingData.iat[1131,10] = "22059"
    smokingData.iat[1791,10] = "35013"
    smokingData.iat[2406,10] = "46102"

    smokingData = smokingData.drop(['state', 'county', 'sex', 'year', 'total_lb', 'total_ub', 'daily_mean', 'daily_lb', 'daily_ub'], axis=1)
    smokingData.rename(columns={'fips': 'FIPS', 'total_mean': 'smoking_prevalence'}, inplace=True)
    return smokingData

def export_health():
    dia = preprocess_diabetes()
    dia.to_csv("raw_data/health_data/diabetes_data.csv", index=False)
    obe = preprocess_obesity()
    obe.to_csv("raw_data/health_data/obesity_data.csv", index=False)
    mort = preprocess_mortality()
    mort.to_csv("raw_data/health_data/mort_data.csv", index=False)
    id_mortality = preprocess_infectious_disease_mortality()
    id_mortality.to_csv("raw_data/health_data/id_mortality.csv", index=False)
    rd_mortality = preprocess_respiratory_disease_mortality()
    rd_mortality.to_csv("raw_data/health_data/rd_mortality.csv", index=False)
    smoking_prev = preprocess_smoking_prevalence()
    smoking_prev.to_csv("raw_data/health_data/smoking_prev.csv", index=False)

def preprocess_full_health():
    dia = pd.read_csv("raw_data/health_data/diabetes_data.csv")
    obe = pd.read_csv("raw_data/health_data/obesity_data.csv")
    mort = pd.read_csv("raw_data/health_data/mort_data.csv")
    id_mortality = pd.read_csv("raw_data/health_data/id_mortality.csv")
    rd_mortality = pd.read_csv("raw_data/health_data/rd_mortality.csv")
    smoking_prev = pd.read_csv("raw_data/health_data/smoking_prev.csv")

    mergedDF = pd.merge(left=dia, right=obe, how='left', on='FIPS', copy=False)
    mergedDF = pd.merge(left=mergedDF, right=mort, how='left', on = 'FIPS', copy=False)
    mergedDF = pd.merge(left=mergedDF, right=id_mortality, how='left', on='FIPS', copy=False)
    mergedDF = pd.merge(left=mergedDF, right=rd_mortality, how='left', on='FIPS', copy=False)
    mergedDF = pd.merge(left=mergedDF, right=smoking_prev, how='left', on='FIPS', copy=False)

    mergedDF.to_csv("raw_data/health_data/health_data.csv", index=False)

def preprocess_JHU():
    bronx = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C3%2C0%0A03%2F01%2F2020%2C1%2C1%2C0%0A03%2F02%2F2020%2C0%2C9%2C0%0A03%2F03%2F2020%2C1%2C7%2C0%0A03%2F04%2F2020%2C0%2C6%2C0%0A03%2F05%2F2020%2C0%2C2%2C0%0A03%2F06%2F2020%2C2%2C5%2C0%0A03%2F07%2F2020%2C0%2C2%2C0%0A03%2F08%2F2020%2C4%2C0%2C0%0A03%2F09%2F2020%2C4%2C11%2C0%0A03%2F10%2F2020%2C8%2C8%2C0%0A03%2F11%2F2020%2C19%2C19%2C0%0A03%2F12%2F2020%2C29%2C18%2C0%0A03%2F13%2F2020%2C80%2C33%2C0%0A03%2F14%2F2020%2C85%2C26%2C0%0A03%2F15%2F2020%2C117%2C34%2C1%0A03%2F16%2F2020%2C303%2C64%2C3%0A03%2F17%2F2020%2C343%2C66%2C1%0A03%2F18%2F2020%2C483%2C101%2C1%0A03%2F19%2F2020%2C620%2C122%2C4%0A03%2F20%2F2020%2C718%2C109%2C13%0A03%2F21%2F2020%2C483%2C151%2C13%0A03%2F22%2F2020%2C491%2C161%2C12%0A03%2F23%2F2020%2C722%2C207%2C12%0A03%2F24%2F2020%2C927%2C255%2C14%0A03%2F25%2F2020%2C1054%2C290%2C30%0A03%2F26%2F2020%2C998%2C307%2C37%0A03%2F27%2F2020%2C1089%2C306%2C34%0A03%2F28%2F2020%2C761%2C300%2C61%0A03%2F29%2F2020%2C697%2C310%2C54%0A03%2F30%2F2020%2C1309%2C320%2C74%0A03%2F31%2F2020%2C1283%2C352%2C93%0A04%2F01%2F2020%2C1235%2C337%2C90%0A04%2F02%2F2020%2C1284%2C338%2C95%0A04%2F03%2F2020%2C1445%2C357%2C114%0A04%2F04%2F2020%2C1007%2C281%2C106%0A04%2F05%2F2020%2C816%2C316%2C122%0A04%2F06%2F2020%2C1512%2C380%2C109%0A04%2F07%2F2020%2C1462%2C330%2C114%0A04%2F08%2F2020%2C1288%2C365%2C106%0A04%2F09%2F2020%2C1278%2C301%2C108%0A04%2F10%2F2020%2C1229%2C304%2C118%0A04%2F11%2F2020%2C992%2C263%2C132%0A04%2F12%2F2020%2C758%2C236%2C106%0A04%2F13%2F2020%2C693%2C279%2C118%0A04%2F14%2F2020%2C1072%2C213%2C109%0A04%2F15%2F2020%2C1063%2C221%2C92%0A04%2F16%2F2020%2C933%2C197%2C83%0A04%2F17%2F2020%2C911%2C197%2C85%0A04%2F18%2F2020%2C548%2C153%2C57%0A04%2F19%2F2020%2C528%2C148%2C73%0A04%2F20%2F2020%2C975%2C164%2C76%0A04%2F21%2F2020%2C637%2C146%2C68%0A04%2F22%2F2020%2C920%2C126%2C67%0A04%2F23%2F2020%2C732%2C129%2C57%0A04%2F24%2F2020%2C578%2C113%2C61%0A04%2F25%2F2020%2C412%2C100%2C52%0A04%2F26%2F2020%2C194%2C88%2C52%0A04%2F27%2F2020%2C544%2C112%2C53%0A04%2F28%2F2020%2C667%2C110%2C55%0A04%2F29%2F2020%2C556%2C98%2C40%0A04%2F30%2F2020%2C477%2C70%2C44%0A05%2F01%2F2020%2C441%2C91%2C45%0A05%2F02%2F2020%2C259%2C61%2C49%0A05%2F03%2F2020%2C150%2C56%2C27%0A05%2F04%2F2020%2C347%2C68%2C35%0A05%2F05%2F2020%2C294%2C84%2C25%0A05%2F06%2F2020%2C281%2C71%2C25%0A05%2F07%2F2020%2C294%2C58%2C27%0A05%2F08%2F2020%2C251%2C70%2C21%0A05%2F09%2F2020%2C177%2C46%2C21%0A05%2F10%2F2020%2C75%2C35%2C13%0A05%2F11%2F2020%2C227%2C54%2C26%0A05%2F12%2F2020%2C353%2C53%2C20%0A05%2F13%2F2020%2C455%2C51%2C15%0A05%2F14%2F2020%2C255%2C46%2C8%0A05%2F15%2F2020%2C176%2C52%2C16%0A05%2F16%2F2020%2C108%2C27%2C26%0A05%2F17%2F2020%2C56%2C26%2C19%0A05%2F18%2F2020%2C185%2C33%2C11%0A05%2F19%2F2020%2C178%2C41%2C11%0A05%2F20%2F2020%2C274%2C38%2C15%0A05%2F21%2F2020%2C189%2C33%2C12%0A05%2F22%2F2020%2C247%2C48%2C11%0A05%2F23%2F2020%2C87%2C21%2C14%0A05%2F24%2F2020%2C96%2C23%2C12%0A05%2F25%2F2020%2C95%2C31%2C6%0A05%2F26%2F2020%2C266%2C36%2C9%0A05%2F27%2F2020%2C165%2C26%2C7%0A05%2F28%2F2020%2C105%2C24%2C8%0A05%2F29%2F2020%2C141%2C44%2C5%0A05%2F30%2F2020%2C60%2C22%2C12%0A05%2F31%2F2020%2C29%2C20%2C4%0A06%2F01%2F2020%2C115%2C28%2C3%0A06%2F02%2F2020%2C62%2C24%2C6%0A06%2F03%2F2020%2C34%2C14%2C5%0A06%2F04%2F2020%2C20%2C7%2C1%0A06%2F05%2F2020%2C2%2C0%2C0"

    brooklyn = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C4%2C0%0A03%2F01%2F2020%2C0%2C0%2C0%0A03%2F02%2F2020%2C0%2C4%2C0%0A03%2F03%2F2020%2C0%2C4%2C0%0A03%2F04%2F2020%2C1%2C5%2C0%0A03%2F05%2F2020%2C3%2C5%2C0%0A03%2F06%2F2020%2C1%2C2%2C0%0A03%2F07%2F2020%2C2%2C5%2C0%0A03%2F08%2F2020%2C5%2C9%2C0%0A03%2F09%2F2020%2C16%2C14%2C0%0A03%2F10%2F2020%2C11%2C13%2C0%0A03%2F11%2F2020%2C31%2C15%2C0%0A03%2F12%2F2020%2C96%2C26%2C0%0A03%2F13%2F2020%2C166%2C36%2C0%0A03%2F14%2F2020%2C163%2C36%2C1%0A03%2F15%2F2020%2C429%2C44%2C0%0A03%2F16%2F2020%2C739%2C81%2C1%0A03%2F17%2F2020%2C786%2C99%2C4%0A03%2F18%2F2020%2C968%2C109%2C6%0A03%2F19%2F2020%2C1208%2C146%2C6%0A03%2F20%2F2020%2C1140%2C186%2C10%0A03%2F21%2F2020%2C558%2C172%2C12%0A03%2F22%2F2020%2C757%2C180%2C10%0A03%2F23%2F2020%2C909%2C267%2C27%0A03%2F24%2F2020%2C1208%2C297%2C23%0A03%2F25%2F2020%2C1230%2C371%2C36%0A03%2F26%2F2020%2C1357%2C429%2C50%0A03%2F27%2F2020%2C1406%2C394%2C73%0A03%2F28%2F2020%2C849%2C351%2C74%0A03%2F29%2F2020%2C1120%2C408%2C87%0A03%2F30%2F2020%2C1746%2C488%2C106%0A03%2F31%2F2020%2C1493%2C449%2C122%0A04%2F01%2F2020%2C1588%2C448%2C129%0A04%2F02%2F2020%2C1636%2C398%2C163%0A04%2F03%2F2020%2C1442%2C397%2C135%0A04%2F04%2F2020%2C917%2C320%2C151%0A04%2F05%2F2020%2C1149%2C365%2C161%0A04%2F06%2F2020%2C1503%2C447%2C164%0A04%2F07%2F2020%2C1415%2C454%2C178%0A04%2F08%2F2020%2C1320%2C411%2C170%0A04%2F09%2F2020%2C1360%2C391%2C185%0A04%2F10%2F2020%2C1150%2C321%2C168%0A04%2F11%2F2020%2C1122%2C281%2C153%0A04%2F12%2F2020%2C697%2C250%2C200%0A04%2F13%2F2020%2C1061%2C320%2C157%0A04%2F14%2F2020%2C1032%2C250%2C153%0A04%2F15%2F2020%2C880%2C266%2C128%0A04%2F16%2F2020%2C880%2C231%2C123%0A04%2F17%2F2020%2C957%2C239%2C116%0A04%2F18%2F2020%2C574%2C165%2C113%0A04%2F19%2F2020%2C634%2C135%2C114%0A04%2F20%2F2020%2C979%2C203%2C94%0A04%2F21%2F2020%2C898%2C160%2C91%0A04%2F22%2F2020%2C854%2C156%2C104%0A04%2F23%2F2020%2C789%2C151%2C106%0A04%2F24%2F2020%2C627%2C138%2C93%0A04%2F25%2F2020%2C404%2C103%2C74%0A04%2F26%2F2020%2C333%2C88%2C60%0A04%2F27%2F2020%2C610%2C112%2C85%0A04%2F28%2F2020%2C714%2C116%2C57%0A04%2F29%2F2020%2C682%2C119%2C71%0A04%2F30%2F2020%2C599%2C89%2C65%0A05%2F01%2F2020%2C496%2C78%2C55%0A05%2F02%2F2020%2C263%2C56%2C46%0A05%2F03%2F2020%2C247%2C60%2C46%0A05%2F04%2F2020%2C464%2C83%2C41%0A05%2F05%2F2020%2C434%2C72%2C48%0A05%2F06%2F2020%2C452%2C69%2C37%0A05%2F07%2F2020%2C400%2C77%2C45%0A05%2F08%2F2020%2C348%2C74%2C42%0A05%2F09%2F2020%2C121%2C49%2C28%0A05%2F10%2F2020%2C191%2C41%2C24%0A05%2F11%2F2020%2C409%2C71%2C32%0A05%2F12%2F2020%2C400%2C56%2C32%0A05%2F13%2F2020%2C363%2C58%2C22%0A05%2F14%2F2020%2C332%2C57%2C14%0A05%2F15%2F2020%2C260%2C56%2C26%0A05%2F16%2F2020%2C163%2C42%2C21%0A05%2F17%2F2020%2C138%2C35%2C17%0A05%2F18%2F2020%2C270%2C52%2C14%0A05%2F19%2F2020%2C331%2C63%2C14%0A05%2F20%2F2020%2C308%2C49%2C19%0A05%2F21%2F2020%2C335%2C59%2C12%0A05%2F22%2F2020%2C364%2C58%2C13%0A05%2F23%2F2020%2C161%2C33%2C19%0A05%2F24%2F2020%2C176%2C34%2C12%0A05%2F25%2F2020%2C166%2C31%2C13%0A05%2F26%2F2020%2C332%2C33%2C10%0A05%2F27%2F2020%2C251%2C50%2C9%0A05%2F28%2F2020%2C221%2C42%2C14%0A05%2F29%2F2020%2C148%2C27%2C16%0A05%2F30%2F2020%2C94%2C28%2C11%0A05%2F31%2F2020%2C64%2C21%2C10%0A06%2F01%2F2020%2C150%2C30%2C7%0A06%2F02%2F2020%2C103%2C23%2C4%0A06%2F03%2F2020%2C59%2C24%2C4%0A06%2F04%2F2020%2C39%2C2%2C1%0A06%2F05%2F2020%2C5%2C0%2C0"

    manhattan = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C1%2C2%2C0%0A03%2F01%2F2020%2C0%2C0%2C0%0A03%2F02%2F2020%2C0%2C4%2C0%0A03%2F03%2F2020%2C0%2C2%2C0%0A03%2F04%2F2020%2C2%2C5%2C0%0A03%2F05%2F2020%2C0%2C6%2C0%0A03%2F06%2F2020%2C3%2C3%2C0%0A03%2F07%2F2020%2C1%2C4%2C0%0A03%2F08%2F2020%2C6%2C1%2C0%0A03%2F09%2F2020%2C25%2C12%2C0%0A03%2F10%2F2020%2C24%2C12%2C0%0A03%2F11%2F2020%2C61%2C21%2C0%0A03%2F12%2F2020%2C137%2C11%2C0%0A03%2F13%2F2020%2C182%2C27%2C0%0A03%2F14%2F2020%2C179%2C28%2C0%0A03%2F15%2F2020%2C209%2C32%2C2%0A03%2F16%2F2020%2C458%2C38%2C1%0A03%2F17%2F2020%2C566%2C57%2C0%0A03%2F18%2F2020%2C540%2C77%2C4%0A03%2F19%2F2020%2C553%2C90%2C4%0A03%2F20%2F2020%2C656%2C110%2C11%0A03%2F21%2F2020%2C401%2C112%2C5%0A03%2F22%2F2020%2C321%2C127%2C8%0A03%2F23%2F2020%2C536%2C171%2C7%0A03%2F24%2F2020%2C624%2C187%2C17%0A03%2F25%2F2020%2C594%2C180%2C20%0A03%2F26%2F2020%2C627%2C211%2C33%0A03%2F27%2F2020%2C657%2C202%2C41%0A03%2F28%2F2020%2C383%2C199%2C28%0A03%2F29%2F2020%2C405%2C159%2C35%0A03%2F30%2F2020%2C825%2C263%2C35%0A03%2F31%2F2020%2C637%2C219%2C43%0A04%2F01%2F2020%2C590%2C170%2C60%0A04%2F02%2F2020%2C656%2C225%2C63%0A04%2F03%2F2020%2C686%2C257%2C52%0A04%2F04%2F2020%2C390%2C198%2C63%0A04%2F05%2F2020%2C358%2C184%2C86%0A04%2F06%2F2020%2C719%2C259%2C69%0A04%2F07%2F2020%2C607%2C196%2C90%0A04%2F08%2F2020%2C558%2C176%2C65%0A04%2F09%2F2020%2C565%2C197%2C64%0A04%2F10%2F2020%2C502%2C192%2C68%0A04%2F11%2F2020%2C314%2C130%2C59%0A04%2F12%2F2020%2C253%2C142%2C63%0A04%2F13%2F2020%2C394%2C187%2C72%0A04%2F14%2F2020%2C444%2C159%2C59%0A04%2F15%2F2020%2C436%2C145%2C55%0A04%2F16%2F2020%2C361%2C109%2C58%0A04%2F17%2F2020%2C333%2C124%2C42%0A04%2F18%2F2020%2C187%2C86%2C56%0A04%2F19%2F2020%2C179%2C84%2C48%0A04%2F20%2F2020%2C378%2C92%2C50%0A04%2F21%2F2020%2C374%2C98%2C47%0A04%2F22%2F2020%2C387%2C106%2C38%0A04%2F23%2F2020%2C401%2C69%2C47%0A04%2F24%2F2020%2C414%2C92%2C50%0A04%2F25%2F2020%2C149%2C52%2C42%0A04%2F26%2F2020%2C98%2C52%2C33%0A04%2F27%2F2020%2C302%2C72%2C29%0A04%2F28%2F2020%2C322%2C71%2C36%0A04%2F29%2F2020%2C285%2C51%2C33%0A04%2F30%2F2020%2C218%2C40%2C33%0A05%2F01%2F2020%2C244%2C48%2C24%0A05%2F02%2F2020%2C139%2C28%2C23%0A05%2F03%2F2020%2C104%2C41%2C35%0A05%2F04%2F2020%2C214%2C47%2C18%0A05%2F05%2F2020%2C242%2C33%2C18%0A05%2F06%2F2020%2C166%2C33%2C17%0A05%2F07%2F2020%2C119%2C30%2C21%0A05%2F08%2F2020%2C101%2C38%2C14%0A05%2F09%2F2020%2C75%2C23%2C17%0A05%2F10%2F2020%2C95%2C21%2C19%0A05%2F11%2F2020%2C190%2C35%2C13%0A05%2F12%2F2020%2C164%2C31%2C14%0A05%2F13%2F2020%2C155%2C39%2C8%0A05%2F14%2F2020%2C151%2C29%2C16%0A05%2F15%2F2020%2C136%2C36%2C12%0A05%2F16%2F2020%2C58%2C15%2C9%0A05%2F17%2F2020%2C50%2C18%2C10%0A05%2F18%2F2020%2C132%2C27%2C10%0A05%2F19%2F2020%2C167%2C36%2C10%0A05%2F20%2F2020%2C164%2C21%2C12%0A05%2F21%2F2020%2C146%2C24%2C5%0A05%2F22%2F2020%2C155%2C35%2C5%0A05%2F23%2F2020%2C46%2C19%2C7%0A05%2F24%2F2020%2C70%2C21%2C6%0A05%2F25%2F2020%2C71%2C24%2C11%0A05%2F26%2F2020%2C126%2C24%2C6%0A05%2F27%2F2020%2C106%2C26%2C8%0A05%2F28%2F2020%2C93%2C27%2C3%0A05%2F29%2F2020%2C67%2C30%2C5%0A05%2F30%2F2020%2C36%2C11%2C9%0A05%2F31%2F2020%2C24%2C13%2C5%0A06%2F01%2F2020%2C65%2C19%2C2%0A06%2F02%2F2020%2C46%2C19%2C5%0A06%2F03%2F2020%2C44%2C19%2C2%0A06%2F04%2F2020%2C13%2C3%2C1%0A06%2F05%2F2020%2C3%2C0%2C0"

    queens = 'data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C2%2C0%0A03%2F01%2F2020%2C0%2C2%2C0%0A03%2F02%2F2020%2C0%2C5%2C0%0A03%2F03%2F2020%2C1%2C5%2C0%0A03%2F04%2F2020%2C2%2C3%2C0%0A03%2F05%2F2020%2C0%2C5%2C0%0A03%2F06%2F2020%2C1%2C7%2C0%0A03%2F07%2F2020%2C3%2C3%2C0%0A03%2F08%2F2020%2C5%2C5%2C0%0A03%2F09%2F2020%2C10%2C8%2C0%0A03%2F10%2F2020%2C24%2C23%2C0%0A03%2F11%2F2020%2C40%2C29%2C1%0A03%2F12%2F2020%2C79%2C28%2C0%0A03%2F13%2F2020%2C165%2C48%2C0%0A03%2F14%2F2020%2C194%2C57%2C1%0A03%2F15%2F2020%2C230%2C64%2C1%0A03%2F16%2F2020%2C530%2C105%2C4%0A03%2F17%2F2020%2C650%2C108%2C3%0A03%2F18%2F2020%2C830%2C152%2C9%0A03%2F19%2F2020%2C1065%2C160%2C6%0A03%2F20%2F2020%2C1184%2C224%2C9%0A03%2F21%2F2020%2C945%2C223%2C13%0A03%2F22%2F2020%2C695%2C223%2C14%0A03%2F23%2F2020%2C1190%2C336%2C28%0A03%2F24%2F2020%2C1390%2C356%2C34%0A03%2F25%2F2020%2C1569%2C401%2C30%0A03%2F26%2F2020%2C1640%2C425%2C56%0A03%2F27%2F2020%2C1571%2C413%2C56%0A03%2F28%2F2020%2C1200%2C440%2C89%0A03%2F29%2F2020%2C1075%2C450%2C92%0A03%2F30%2F2020%2C1836%2C540%2C94%0A03%2F31%2F2020%2C1791%2C553%2C93%0A04%2F01%2F2020%2C1763%2C514%2C136%0A04%2F02%2F2020%2C1807%2C557%2C133%0A04%2F03%2F2020%2C1749%2C514%2C154%0A04%2F04%2F2020%2C1196%2C462%2C149%0A04%2F05%2F2020%2C1131%2C385%2C176%0A04%2F06%2F2020%2C1907%2C524%2C198%0A04%2F07%2F2020%2C1938%2C515%2C180%0A04%2F08%2F2020%2C1839%2C509%2C172%0A04%2F09%2F2020%2C1543%2C449%2C154%0A04%2F10%2F2020%2C1317%2C441%2C144%0A04%2F11%2F2020%2C970%2C351%2C153%0A04%2F12%2F2020%2C911%2C303%2C160%0A04%2F13%2F2020%2C968%2C351%2C177%0A04%2F14%2F2020%2C1290%2C379%2C160%0A04%2F15%2F2020%2C1171%2C304%2C139%0A04%2F16%2F2020%2C1137%2C281%2C120%0A04%2F17%2F2020%2C1097%2C285%2C109%0A04%2F18%2F2020%2C701%2C209%2C114%0A04%2F19%2F2020%2C869%2C184%2C119%0A04%2F20%2F2020%2C1219%2C219%2C113%0A04%2F21%2F2020%2C930%2C208%2C87%0A04%2F22%2F2020%2C1109%2C176%2C74%0A04%2F23%2F2020%2C789%2C151%2C86%0A04%2F24%2F2020%2C774%2C161%2C81%0A04%2F25%2F2020%2C540%2C115%2C62%0A04%2F26%2F2020%2C334%2C122%2C78%0A04%2F27%2F2020%2C719%2C119%2C80%0A04%2F28%2F2020%2C890%2C119%2C61%0A04%2F29%2F2020%2C692%2C116%2C72%0A04%2F30%2F2020%2C591%2C112%2C55%0A05%2F01%2F2020%2C620%2C105%2C70%0A05%2F02%2F2020%2C334%2C88%2C55%0A05%2F03%2F2020%2C247%2C76%2C44%0A05%2F04%2F2020%2C433%2C78%2C48%0A05%2F05%2F2020%2C460%2C60%2C39%0A05%2F06%2F2020%2C445%2C65%2C52%0A05%2F07%2F2020%2C356%2C62%2C34%0A05%2F08%2F2020%2C341%2C51%2C40%0A05%2F09%2F2020%2C255%2C39%2C30%0A05%2F10%2F2020%2C85%2C39%2C27%0A05%2F11%2F2020%2C378%2C72%2C23%0A05%2F12%2F2020%2C314%2C50%2C15%0A05%2F13%2F2020%2C304%2C47%2C22%0A05%2F14%2F2020%2C331%2C62%2C20%0A05%2F15%2F2020%2C265%2C65%2C25%0A05%2F16%2F2020%2C135%2C59%2C17%0A05%2F17%2F2020%2C106%2C36%2C24%0A05%2F18%2F2020%2C274%2C49%2C14%0A05%2F19%2F2020%2C288%2C50%2C11%0A05%2F20%2F2020%2C238%2C40%2C21%0A05%2F21%2F2020%2C304%2C38%2C8%0A05%2F22%2F2020%2C224%2C51%2C25%0A05%2F23%2F2020%2C129%2C42%2C12%0A05%2F24%2F2020%2C118%2C27%2C10%0A05%2F25%2F2020%2C106%2C45%2C9%0A05%2F26%2F2020%2C260%2C43%2C7%0A05%2F27%2F2020%2C161%2C53%2C15%0A05%2F28%2F2020%2C160%2C31%2C7%0A05%2F29%2F2020%2C193%2C43%2C14%0A05%2F30%2F2020%2C92%2C25%2C16%0A05%2F31%2F2020%2C60%2C31%2C11%0A06%2F01%2F2020%2C121%2C34%2C10%0A06%2F02%2F2020%2C90%2C34%2C9%0A06%2F03%2F2020%2C58%2C17%2C2%0A06%2F04%2F2020%2C28%2C1%2C1%0A06%2F05%2F2020%2C7%2C0%2C0'

    staten_island = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C0%2C0%0A03%2F01%2F2020%2C0%2C1%2C0%0A03%2F02%2F2020%2C0%2C0%2C0%0A03%2F03%2F2020%2C0%2C1%2C0%0A03%2F04%2F2020%2C0%2C2%2C0%0A03%2F05%2F2020%2C0%2C1%2C0%0A03%2F06%2F2020%2C1%2C2%2C0%0A03%2F07%2F2020%2C1%2C0%2C0%0A03%2F08%2F2020%2C1%2C0%2C0%0A03%2F09%2F2020%2C3%2C3%2C0%0A03%2F10%2F2020%2C2%2C5%2C0%0A03%2F11%2F2020%2C3%2C3%2C0%0A03%2F12%2F2020%2C13%2C5%2C0%0A03%2F13%2F2020%2C26%2C3%2C0%0A03%2F14%2F2020%2C22%2C8%2C0%0A03%2F15%2F2020%2C46%2C16%2C1%0A03%2F16%2F2020%2C91%2C17%2C0%0A03%2F17%2F2020%2C108%2C21%2C0%0A03%2F18%2F2020%2C150%2C23%2C0%0A03%2F19%2F2020%2C258%2C31%2C4%0A03%2F20%2F2020%2C309%2C30%2C3%0A03%2F21%2F2020%2C248%2C34%2C1%0A03%2F22%2F2020%2C316%2C32%2C6%0A03%2F23%2F2020%2C208%2C46%2C8%0A03%2F24%2F2020%2C349%2C48%2C6%0A03%2F25%2F2020%2C394%2C49%2C4%0A03%2F26%2F2020%2C403%2C47%2C10%0A03%2F27%2F2020%2C372%2C57%2C7%0A03%2F28%2F2020%2C266%2C53%2C13%0A03%2F29%2F2020%2C230%2C57%2C17%0A03%2F30%2F2020%2C397%2C68%2C10%0A03%2F31%2F2020%2C233%2C69%2C21%0A04%2F01%2F2020%2C263%2C72%2C16%0A04%2F02%2F2020%2C370%2C79%2C30%0A04%2F03%2F2020%2C343%2C63%2C29%0A04%2F04%2F2020%2C346%2C51%2C20%0A04%2F05%2F2020%2C323%2C65%2C22%0A04%2F06%2F2020%2C730%2C81%2C24%0A04%2F07%2F2020%2C629%2C70%2C28%0A04%2F08%2F2020%2C558%2C56%2C34%0A04%2F09%2F2020%2C297%2C57%2C25%0A04%2F10%2F2020%2C300%2C52%2C19%0A04%2F11%2F2020%2C311%2C48%2C27%0A04%2F12%2F2020%2C252%2C44%2C26%0A04%2F13%2F2020%2C185%2C56%2C25%0A04%2F14%2F2020%2C289%2C52%2C23%0A04%2F15%2F2020%2C317%2C34%2C24%0A04%2F16%2F2020%2C209%2C38%2C14%0A04%2F17%2F2020%2C281%2C38%2C15%0A04%2F18%2F2020%2C153%2C25%2C19%0A04%2F19%2F2020%2C134%2C30%2C19%0A04%2F20%2F2020%2C224%2C28%2C16%0A04%2F21%2F2020%2C216%2C27%2C11%0A04%2F22%2F2020%2C173%2C20%2C14%0A04%2F23%2F2020%2C128%2C19%2C13%0A04%2F24%2F2020%2C143%2C34%2C13%0A04%2F25%2F2020%2C88%2C26%2C9%0A04%2F26%2F2020%2C46%2C23%2C7%0A04%2F27%2F2020%2C107%2C20%2C9%0A04%2F28%2F2020%2C129%2C19%2C8%0A04%2F29%2F2020%2C124%2C19%2C14%0A04%2F30%2F2020%2C130%2C18%2C11%0A05%2F01%2F2020%2C77%2C12%2C8%0A05%2F02%2F2020%2C60%2C18%2C12%0A05%2F03%2F2020%2C35%2C14%2C15%0A05%2F04%2F2020%2C90%2C14%2C8%0A05%2F05%2F2020%2C78%2C11%2C12%0A05%2F06%2F2020%2C59%2C6%2C7%0A05%2F07%2F2020%2C60%2C8%2C3%0A05%2F08%2F2020%2C42%2C9%2C5%0A05%2F09%2F2020%2C32%2C6%2C3%0A05%2F10%2F2020%2C13%2C5%2C8%0A05%2F11%2F2020%2C27%2C3%2C3%0A05%2F12%2F2020%2C53%2C8%2C6%0A05%2F13%2F2020%2C48%2C9%2C6%0A05%2F14%2F2020%2C41%2C12%2C5%0A05%2F15%2F2020%2C33%2C7%2C6%0A05%2F16%2F2020%2C25%2C8%2C2%0A05%2F17%2F2020%2C10%2C4%2C2%0A05%2F18%2F2020%2C38%2C2%2C2%0A05%2F19%2F2020%2C42%2C8%2C5%0A05%2F20%2F2020%2C56%2C6%2C7%0A05%2F21%2F2020%2C66%2C10%2C3%0A05%2F22%2F2020%2C28%2C6%2C5%0A05%2F23%2F2020%2C35%2C5%2C2%0A05%2F24%2F2020%2C14%2C4%2C5%0A05%2F25%2F2020%2C15%2C5%2C3%0A05%2F26%2F2020%2C50%2C3%2C1%0A05%2F27%2F2020%2C43%2C4%2C1%0A05%2F28%2F2020%2C23%2C7%2C1%0A05%2F29%2F2020%2C20%2C7%2C2%0A05%2F30%2F2020%2C13%2C3%2C0%0A05%2F31%2F2020%2C10%2C3%2C2%0A06%2F01%2F2020%2C32%2C1%2C2%0A06%2F02%2F2020%2C28%2C4%2C1%0A06%2F03%2F2020%2C12%2C2%2C2%0A06%2F04%2F2020%2C2%2C0%2C0%0A06%2F05%2F2020%2C0%2C0%2C0"

    nyFIPS = {"bronx" : "36005", "brooklyn": "36047", "manhattan":"36061", "queens":"36081", "staten_island":"36085"}

    def readNYCounty(county_link, fips):
        with urlopen(county_link) as response:
            data = response.read().decode("utf8")
            df = pd.read_csv(io.StringIO(data))
            df.insert(0,"FIPS", [nyFIPS[fips]]*len(df))
            df = df.drop(['Hospitalizations','Deaths'], axis=1)
            df = df.rename({'DATE_OF_INTEREST':'date', 'Cases':'confirmed_cases'}, axis=1)
            return df

    def process_FIPS(fips):
        num = fips[0:-2]
        missing_zeroes = 5 - len(num)
        missing_zeroes = "0" * missing_zeroes
        return missing_zeroes + num

    jhu_data = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv", dtype={"FIPS": str})
    jhu_data = jhu_data[jhu_data['FIPS'].notnull()]
    jhu_data['FIPS'] = jhu_data['FIPS'].apply(lambda x : process_FIPS(x))
    jhu_data = jhu_data.drop(["Admin2","Province_State","Country_Region","Lat","Long_","Combined_Key","UID","iso2","iso3","code3"], axis=1)
    jhu_data = jhu_data.melt(id_vars=['FIPS'], var_name = 'date', value_name = 'confirmed_cases')

    bronx = readNYCounty(bronx, "bronx")
    brooklyn = readNYCounty(brooklyn, "brooklyn")
    manhattan = readNYCounty(manhattan, "manhattan")
    queens = readNYCounty(queens, "queens")
    staten_island = readNYCounty(staten_island, "staten_island")
    print(jhu_data[jhu_data['FIPS'] == '36061'])
    print(manhattan)

    nyFIPSList = ["36005","36047","36061", "36081", "36085"]
    full_data = pd.concat([jhu_data[~jhu_data['FIPS'].isin(nyFIPSList)], bronx, brooklyn,manhattan,queens,staten_island]).sort_values(['FIPS','date']).reset_index(drop=True)
    full_data['confirmed_cases'] = pd.Series(full_data.groupby("FIPS")['confirmed_cases'].rolling(7).mean()).reset_index(drop=True)
    full_data = full_data[full_data['confirmed_cases'].notnull()]
    full_data['date'] = pd.to_datetime(full_data['date'])
    full_data['date'] = full_data['date'].apply(pd.DateOffset(1))

    # Normalize confirmed cases for population and export to csv
    censusFile = os.path.split(os.getcwd())[0] + "/cc-est2018-alldata.csv"
    censusData = pd.read_csv(censusFile,  encoding = "ISO-8859-1", dtype={'STATE': str, 'COUNTY': str})
    censusData.insert(loc = 0, column = "FIPS", value = censusData["STATE"] + censusData["COUNTY"])

    year = 2018
    ageGroup = 0
    censusData = censusData[(censusData['YEAR'] == year - 2007) & (censusData['AGEGRP'] == ageGroup)]
    censusData = censusData.loc[:, censusData.columns.isin(['FIPS','TOT_POP'])]
    censusData['TOT_POP'] = censusData['TOT_POP'].astype(float)

    mergedDF = pd.merge(left=censusData, right=full_data, how='left', on='FIPS', copy=False)
    mergedDF['confirmed_cases'] = (mergedDF['confirmed_cases']/mergedDF['TOT_POP'] * 100000).round()
    mergedDF = mergedDF.drop('TOT_POP', axis=1)
    startdate = datetime.strptime('2020-2-15', '%Y-%m-%d')
    mergedDF = mergedDF[mergedDF['date'] >= startdate]

    mergedDF.to_csv('raw_data/jhu/jhu_data.csv', sep=",", index=False)

def preprocess_Rt():
    us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands':'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }

    fipsData = pd.read_csv("raw_data/health_data/all-geocodes-v2017.csv",encoding = "ISO-8859-1", dtype={'State Code (FIPS)': str, 'County Code (FIPS)': str})

    # Map 040 level fips code to state name in dictionary
    stateData = fipsData[fipsData['Summary Level'] == 40]
    stateData['state_abbrev'] = stateData['Area Name (including legal/statistical area description)'].apply(lambda x : us_state_abbrev[x])
    stateMap = pd.Series(stateData['State Code (FIPS)'].values,index=stateData['state_abbrev']).to_dict()
    stateMap['AS'] = "60"
    stateMap['GU'] = "66"
    stateMap['MP'] = "69"
    stateMap['PR'] = "72"
    stateMap['VI'] = "78"

    # Get all county fips codes
    fipsData = fipsData[fipsData['Summary Level'] == 50]
    fipsData.insert(0, 'FIPS', fipsData['State Code (FIPS)'] + fipsData['County Code (FIPS)'])
    fipsData = fipsData[['FIPS', 'State Code (FIPS)']]

    rt_data = pd.read_csv("raw_data/rt_data/rt.csv", usecols=['date', 'region', 'mean'])
    rt_data['state'] = rt_data['region'].apply(lambda x : stateMap[x])

    date_list = rt_data['date'].unique()
    fips_list = fipsData['FIPS'].unique()

    df = pd.DataFrame()
    df['FIPS'] = fips_list
    df['date'] = [date_list]*len(fips_list)
    df = df.explode('date').reset_index(drop=True)
    df['state'] = df['FIPS'].apply(lambda x : x[0:2])

    # MIT Model
    projections = pd.read_csv("https://raw.githubusercontent.com/youyanggu/covid19_projections/master/projections/combined/latest_us.csv", usecols=['date', 'region', 'r_values_mean'])
    projections['datetime'] = projections['date'].apply(lambda x: pd.datetime.strptime(x, '%Y-%m-%d'))
    projections = projections[(projections['region'].notnull()) & (projections['datetime'] < pd.to_datetime('today'))]
    projections.insert(0, "state", projections['region'].apply(lambda x : stateMap[x]))
    projections = projections.drop(['datetime', 'region'], axis=1).reset_index(drop=True)


    merged_df = pd.merge(left=df, right=rt_data, how='left', on=['state', 'date'], copy=False)
    merged_df = merged_df[merged_df['region'].notnull()]
    merged_df = merged_df.rename({'mean':'rt_mean_MIT'},axis=1)

    new_merged_df = pd.merge(left=merged_df, right=projections, on=['state', 'date'], copy=False)

    new_merged_df.to_csv("raw_data/rt_data/rt_data.csv", index=False, sep=',')

def preprocess_testing():

    us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands':'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }

    fipsData = pd.read_csv("raw_data/health_data/all-geocodes-v2017.csv",encoding = "ISO-8859-1", dtype={'State Code (FIPS)': str, 'County Code (FIPS)': str})

    # Map 040 level fips code to state name in dictionary
    stateData = fipsData[fipsData['Summary Level'] == 40]
    stateData['state_abbrev'] = stateData['Area Name (including legal/statistical area description)'].apply(lambda x : us_state_abbrev[x])
    stateMap = pd.Series(stateData['State Code (FIPS)'].values,index=stateData['state_abbrev']).to_dict()
    stateMap['AS'] = "60"
    stateMap['GU'] = "66"
    stateMap['MP'] = "69"
    stateMap['PR'] = "72"
    stateMap['VI'] = "78"


    testing = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv", usecols = ['date', 'state', 'totalTestResultsIncrease', 'positiveIncrease'], dtype = {'date':str})
    testing['state'] = testing['state'].apply(lambda x : stateMap[x])
    testing['date'] = pd.to_datetime(testing['date'])
    testing = testing.sort_values(['state','date']).reset_index(drop=True)

    print(testing.head(20))
    # ==============================================================================
    # The two lines below each perform a rolling average of a column of the DataFrame
    testing['positiveIncrease'] = pd.Series(testing.groupby("state")['positiveIncrease'].rolling(7).mean()).reset_index(drop=True)
    testing['totalTestResultsIncrease'] = pd.Series(testing.groupby("state")['totalTestResultsIncrease'].rolling(7).mean()).reset_index(drop=True)

    print(testing.head(20))
    # Rolling average applies to the previous week for the day of interest, thus, dates need to be incremented up by 1, which is done below
    testing['date'] = testing['date'].apply(pd.DateOffset(1))
    # ==============================================================================

    testing['date'] = testing['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    statePopulations = pd.read_csv("raw_data/testing_data/nst-est2019-alldata.csv", usecols = ['SUMLEV', 'STATE', 'POPESTIMATE2019'], dtype={'STATE':str, 'POPESTIMATE2019':float})
    statePopulations = statePopulations[statePopulations['SUMLEV'] == 40].drop(['SUMLEV'], axis=1).rename({'STATE':'state', 'POPESTIMATE2019': 'population'}, axis=1).reset_index(drop=True)

    testing_pop = pd.merge(left=testing, right=statePopulations, how='left', on='state', copy=False)
    testing_pop['positiveIncrease'] = (testing_pop['positiveIncrease']/testing_pop['population']) * 100000
    testing_pop['totalTestResultsIncrease'] = (testing_pop['totalTestResultsIncrease']/testing_pop['population']) * 100000
    testing_pop = testing_pop.dropna().drop('population', axis=1)


    fips_DF = pd.read_csv("raw_data/rt_data/rt_data.csv", dtype={'FIPS':str,'state':str}, usecols=['FIPS','date','state'])

    merged_DF = pd.merge(left=fips_DF, right=testing_pop, how='left', on=['state', 'date'], copy=False)

    merged_DF.to_csv("raw_data/testing_data/testing_data.csv", sep=',', index=False)

def merge_data():

    # Update necessary data
    print("Updating Rt data")
    preprocess_Rt()

    print("Updating JHU data")
    preprocess_JHU()

    print("Updating Facebook Data")
    preprocess_facebook(online=False)

    print("Updating Testing Data")
    preprocess_testing()


    MOBILITY_PATH = get_latest_file('7-days-mobility')
    TIME = date.today().isoformat()
    PATH = 'processed_data/merged/'

    dst = PATH + TIME + '.csv'

    testing_data = pd.read_csv("raw_data/testing_data/testing_data.csv", dtype={'FIPS':int}, usecols=['FIPS', 'date','positiveIncrease', 'totalTestResultsIncrease'])
    rt_data = pd.read_csv("raw_data/rt_data/rt_data.csv", dtype={'FIPS':int}, usecols=['FIPS', 'date','r_values_mean', 'rt_mean_MIT'])
    jhu_data = pd.read_csv("raw_data/jhu/jhu_data.csv", dtype={'FIPS':int})
    health_data = pd.read_csv("raw_data/health_data/health_data.csv", dtype={'FIPS':int})
    disparities_data = pd.read_csv("raw_data/disparities/disparities.csv", dtype={'FIPS':int})
    census_data = pd.read_csv("raw_data/census/census-2018.csv", dtype={'FIPS':int})
    mobility_data = pd.read_csv(MOBILITY_PATH, dtype={'fips':int}, usecols=['fips', 'date', 'google_mobility_7d','apple_mobility_7d'])
    facebook_data = pd.read_csv("raw_data/facebook/facebook.csv", dtype={'FIPS':int})

    merged_DF = pd.merge(left=rt_data, right=testing_data, how='left', on=['FIPS', 'date'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=jhu_data, how='left', on=['FIPS', 'date'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=mobility_data, how='left', left_on=['FIPS', 'date'], right_on=['fips', 'date'], copy=False)
    merged_DF = merged_DF.drop(['fips'], 1)
    merged_DF = pd.merge(left=merged_DF, right=facebook_data, how='left', left_on=['FIPS', 'date'], right_on=['FIPS', 'date'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=health_data, how='left', on=['FIPS'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=disparities_data, how='left', on=['FIPS'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=census_data, how='left', on=['FIPS'], copy=False).sort_values(['FIPS', 'date'])

    if os.path.exists(dst):
        os.remove(dst)

    merged_DF.to_csv(dst, sep=',', index=False)

merge_data()
