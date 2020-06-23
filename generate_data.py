"""
This module preprocesses Facebook Mobility data, health data, census data and
merges them with Apple and Google data.
"""

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

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'released'
__url__ = 'https://github.com/solveforj/pandemic-central'

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
    'District Of Columbia': 'DC',
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
def get_state_fips():

    # Source: US census
    # Link: www.census.gov/geographies/reference-files/2017/demo/popest/2017-fips.html
    # File:  2017 State, County, Minor Civil Division, and Incorporated Place FIPS Codes
    # Note: .xslx file header was removed and sheet was exported to csv
    fips_data = pd.read_csv("data/all-geocodes-v2017.csv",encoding = "ISO-8859-1", dtype={'State Code (FIPS)': str, 'County Code (FIPS)': str})

    # Map 040 level fips code to state name in dictionary
    state_data = fips_data[fips_data['Summary Level'] == 40]
    state_data['state_abbrev'] = state_data['Area Name (including legal/statistical area description)'].apply(lambda x : us_state_abbrev[x])
    state_map = pd.Series(state_data['State Code (FIPS)'].values,index=state_data['state_abbrev']).to_dict()
    state_map['AS'] = "60"
    state_map['GU'] = "66"
    state_map['MP'] = "69"
    state_map['PR'] = "72"
    state_map['VI'] = "78"

    # Get all county fips codes
    fips_data = fips_data[fips_data['Summary Level'] == 50]
    fips_data.insert(0, 'FIPS', fips_data['State Code (FIPS)'] + fips_data['County Code (FIPS)'])
    fips_data = fips_data[['FIPS', 'State Code (FIPS)']]

    return state_map, fips_data


def preprocess_census(year = 2018, drop_tot = True, use_reduced = False):
    # The original census file is too large for repository, but the preprocessed and reduced version may be used
    if use_reduced == True:
        data = pd.read_csv("data/census.csv")

    # Import census data file (in same directory as repository)
    # Source: US census
    # Link: www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html
    # File: Annual County Resident Population Estimates by Age, Sex, Race, and Hispanic Origin: April 1, 2010 to July 1, 2018 (CC-EST2018-ALLDATA)
    census_file = os.path.split(os.getcwd())[0] + "/cc-est2018-alldata.csv"
    census_data = pd.read_csv(census_file,  encoding = "ISO-8859-1", dtype={'STATE': str, 'COUNTY': str})
    census_data.insert(loc = 0, column = "FIPS", value = census_data["STATE"] + census_data["COUNTY"])

    # Filter data for year and minority populations
    census_data = census_data[(census_data['YEAR'] == year - 2007)]
    census_data = census_data.loc[:, census_data.columns.isin(['FIPS','TOT_POP', 'AGEGRP','TOT_MALE'\
    'TOT_FEMALE','H_MALE','H_FEMALE','BA_MALE','BA_FEMALE','IA_MALE','IA_FEMALE',\
    'NA_MALE','NA_FEMALE','TOM_MALE','TOM_FEMALE'])]

    # Add population of elderly in each county
    new_census_data = census_data[census_data['AGEGRP'] == 0].reset_index(drop=True)
    elderly_data = census_data[census_data['AGEGRP'] >= 13]
    elderly_population = elderly_data.groupby('FIPS')['TOT_POP'].sum().reset_index(drop=True)
    new_census_data['ELDERLY_POP'] = elderly_population
    new_census_data = new_census_data.drop(['AGEGRP'], axis=1)

    # Normalize data by county size
    # Source: United States Department of Agriculture
    # Link: www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/
    # File: 2010 Rural-Urban Commuting Area Codes (revised 7/3/2019)
    # Note: File was converted to csv format from xlsx without header
    county_sizes = pd.read_csv("data/ruca2010revised.csv", dtype={'State-County FIPS Code':str}, encoding="ISO-8859-1")
    county_sizes = county_sizes.rename({'State-County FIPS Code': 'FIPS', 'Land Area (square miles), 2010':'Land Area'}, axis=1)
    county_sizes['Land Area'] = county_sizes['Land Area'].apply(lambda x : float(x.replace(",", "")))
    individual_sizes = pd.DataFrame(county_sizes.groupby('FIPS')['Land Area'].apply(lambda x: x.sum()))
    individual_sizes.insert(0,'FIPS', individual_sizes.index)
    individual_sizes = individual_sizes.reset_index(drop=True)

    # Make final dataframe
    merged_df = pd.merge(left=new_census_data, right=individual_sizes, how='left', on='FIPS', copy=False)
    merged_df[merged_df.columns[1:]] = merged_df[merged_df.columns[1:]].astype(float)
    merged_df[merged_df.columns[2:-1]] = merged_df[merged_df.columns[2:-1]].div(merged_df['TOT_POP'], axis=0)
    merged_df.insert(1, "POP_DENSITY", merged_df['TOT_POP']/merged_df['Land Area'])
    if drop_tot == True:
        merged_df = merged_df.drop(['TOT_POP', 'Land Area'], axis=1)

    merged_df.to_csv("data/census.csv", index=False)

    return merged_df

def preprocess_disparities():
    # Source: Surgo Foundation
    # Link: docs.google.com/spreadsheets/d/1bPdZz1YCYai1l35XL2CWdAS0gCjpss0FMiDGWERYPmA/edit#gid=1699059654
    # Note: Original csv was modified by simplifying header titles
    disparities = pd.read_csv("data/CCVI.csv", dtype={"FIPS":str})
    disparities = disparities[disparities.columns[3:-2]].sort_values('FIPS').reset_index(drop=True)

    return disparities

def preprocess_facebook():
    # Get name of correct data file, which is in same directory as repository
    # Source: COVID-19 Mobility Data Network
    # Link: data.humdata.org/dataset/movement-range-maps
    link = "https://data.humdata.org/dataset/movement-range-maps"
    page = requests.get(link).content
    soup = BeautifulSoup(page, 'html.parser')
    data_link = soup.find_all('a', {"class": "btn btn-empty btn-empty-blue hdx-btn resource-url-analytics ga-download"}, href=True)[0]['href']
    data_link = "https://data.humdata.org" + data_link
    data_file = data_link.split("/")[-1].split(".")[0].replace("-data", "") + ".txt"
    data_path = os.path.split(os.getcwd())[0] + "/" + data_file

    # Preprocess file
    df = pd.read_csv(data_path, sep='\t', dtype={'polygon_id':str})
    df = df[df['country'] == 'USA']
    df = df[['ds', 'polygon_id', 'all_day_bing_tiles_visited_relative_change', 'all_day_ratio_single_tile_users']]
    df = df.rename({'polygon_id':'FIPS','ds':'date','all_day_bing_tiles_visited_relative_change':'fb_movement_change', 'all_day_ratio_single_tile_users':'fb_stationary'}, axis=1)
    df = df.reset_index(drop=True)

    # Compute 7 day (weekly) rolling averages for movement data
    df['fb_movement_change'] = pd.Series(df.groupby("FIPS")['fb_movement_change'].rolling(7).mean()).reset_index(drop=True)
    df['fb_stationary'] = pd.Series(df.groupby("FIPS")['fb_stationary'].rolling(7).mean()).reset_index(drop=True)

    # Move dates forward by 1 day so that movement averages represent data from past week
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].apply(pd.DateOffset(1))
    df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df = df.dropna()

    df.to_csv("data/facebook_data.csv", index=False)

    return df

def preprocess_diabetes():
    # Source: Institute for Health Metrics and Evaluation (IHME). Diagnosed and Undiagnosed Diabetes Prevalence by County in the U.S.,
    #         1999-2012. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2016.
    # Note: Total sheet from .xslx file is exported as csv
    diabetes_data = pd.read_csv("data/IHME_Diabetes.csv")

    # Preprocess file
    diabetes_data = diabetes_data[diabetes_data['FIPS'] > 100]
    diabetes_data = diabetes_data.loc[:, diabetes_data.columns.isin(['FIPS', 'Location', 'Prevalence, 2012, Both Sexes'])]
    diabetes_data.rename(columns={'Prevalence, 2012, Both Sexes': 'Diabetes_Prevalence_Both_Sexes', }, inplace=True)
    diabetes_data['FIPS'] = diabetes_data['FIPS'].apply(lambda x: str(int(x)))
    diabetes_data = diabetes_data.reset_index(drop=True)

    return diabetes_data

def preprocess_obesity():
    # Source: Institute for Health Metrics and Evaluation (IHME). United States Physical Activity and Obesity Prevalence by County 2001-2011.
    #         Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2013.
    # Link: ghdx.healthdata.org/record/ihme-data/united-states-physical-activity-and-obesity-prevalence-county-2001-2011
    obesity_data = pd.read_csv("data/IHME_USA_OBESITY_PHYSICAL_ACTIVITY_2001_2011.csv",dtype={'fips': str})

    # Preprocess data
    obesity_data = obesity_data[obesity_data['Outcome'] == 'Obesity']
    obesity_data = obesity_data.loc[:, obesity_data.columns.isin(['merged_fips', 'Sex', 'Prevalence 2011 (%)'])]
    male_obesity_data = obesity_data[obesity_data['Sex'] == "Male"]
    male_obesity_data.rename(columns={'Prevalence 2011 (%)': 'Male_Obesity_%', 'merged_fips':'fips'}, inplace=True)
    male_obesity_data = male_obesity_data.drop(['Sex'], axis=1).reset_index(drop=True)
    female_obesity_data = obesity_data[obesity_data['Sex'] == "Female"]
    female_obesity_data.rename(columns={'Prevalence 2011 (%)': 'Female_Obesity_%', 'merged_fips':'fips'}, inplace=True)
    female_obesity_data = female_obesity_data.drop(['Sex'], axis=1).reset_index(drop=True)
    merged_df = pd.merge(left=male_obesity_data, right=female_obesity_data, how='left', on='fips')
    merged_df.rename(columns={'fips': 'FIPS', }, inplace=True)
    merged_df['FIPS'] = merged_df['FIPS'].astype(str)

    return merged_df

def preprocess_mortality():
    # Source: Institute for Health Metrics and Evaluation (IHME). United States Life Expectancy and Age-specific Mortality Risk by County 1980-2014.
    #         Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2017.
    # Link: http://ghdx.healthdata.org/record/ihme-data/united-states-life-expectancy-and-age-specific-mortality-risk-county-1980-2014
    # Note: All columns for all sheets in the original .xlsx file were merged into 1 sheet by FIPS,
    #       which was exported into a csv file
    mortality_data = pd.read_csv("data/IHME_Mortality.csv")

    # Preprocess data
    mortality_data = mortality_data[mortality_data['FIPS'] > 100.0]
    columns = mortality_data.columns[1:]
    for i in columns:
        mortality_data[i] = mortality_data[i].apply(lambda x : float(x.split(" ")[0]))
    mortality_data = mortality_data.reset_index(drop=True)
    mortality_data['FIPS'] = mortality_data['FIPS'].apply(lambda x : str(int(x)))

    return mortality_data

def preprocess_infectious_disease_mortality():
    # Source: Institute for Health Metrics and Evaluation (IHME). United States Infectious Disease Mortality Rates by County 1980-2014.
    #         Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2018.
    # Link: http://ghdx.healthdata.org/record/ihme-data/united-states-infectious-disease-mortality-rates-county-1980-2014
    # Note: All columns for all sheets in the original .xlsx file were merged into 1 sheet by FIPS,
    #       which was exported into a csv file
    mortality_data = pd.read_csv("data/IHME_Infections_Disease_Mortality.csv")

    # Preprocess data
    mortality_data = mortality_data[mortality_data['FIPS'] > 100.0]
    columns = mortality_data.columns[1:]
    for i in columns:
        mortality_data[i] = mortality_data[i].apply(lambda x : float(x.split(" ")[0]))
    mortality_data = mortality_data.reset_index(drop=True)
    mortality_data['FIPS'] = mortality_data['FIPS'].apply(lambda x : str(int(x)))

    return mortality_data

def preprocess_respiratory_disease_mortality():
    # Source: Institute for Health Metrics and Evaluation (IHME). United States Chronic Respiratory Disease Mortality Rates by County 1980-2014.
    #         Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2017.
    # Link: http://ghdx.healthdata.org/record/ihme-data/united-states-chronic-respiratory-disease-mortality-rates-county-1980-2014
    # Note: All columns for all sheets in the original .xlsx file were merged into 1 sheet by FIPS,
    #       which was exported into a csv file
    mortality_data = pd.read_csv("data/IHME_Respiratory_Disease_Mortality.csv")

    # Preprocess data
    mortality_data = mortality_data[mortality_data['FIPS'] > 100.0]
    columns = mortality_data.columns[1:]
    for i in columns:
        mortality_data[i] = mortality_data[i].apply(lambda x : float(x.split(" ")[0]))
    mortality_data = mortality_data.reset_index(drop=True)
    mortality_data['FIPS'] = mortality_data['FIPS'].apply(lambda x : str(int(x)))

    return mortality_data

def preprocess_smoking_prevalence():
    # Source: Institute for Health Metrics and Evaluation (IHME). United States Smoking Prevalence by County 1996-2012.
    #         Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2014
    # Link: ghdx.healthdata.org/record/ihme-data/united-states-smoking-prevalence-county-1996-2012
    # File: IHME_US_COUNTY_TOTAL_AND_DAILY_SMOKING_PREVALENCE_1996_2012.csv
    smoking_data = pd.read_csv("data/IHME_US_COUNTY_TOTAL_AND_DAILY_SMOKING_PREVALENCE_1996_2012.csv")

    # Preprocess data
    smoking_data = smoking_data[(smoking_data['sex'] == 'Both') & (smoking_data['year'] == 2012) & (smoking_data['county'].notnull())]
    smoking_data['state'] = smoking_data['state'].apply(lambda x : us_state_abbrev[x])
    smoking_data = smoking_data.drop(['sex', 'year', 'total_lb', 'total_ub', 'daily_mean', 'daily_lb', 'daily_ub'], axis=1)
    smoking_data.rename(columns={'fips': 'FIPS', 'total_mean': 'smoking_prevalence', 'county': 'Location', 'state':'region'}, inplace=True)

    return smoking_data

def merge_health_data():

    # Get all data files
    diabetes = preprocess_diabetes()
    obesity = preprocess_obesity()
    mortality = preprocess_mortality()
    id_mortality = preprocess_infectious_disease_mortality()
    rd_mortality = preprocess_respiratory_disease_mortality()

    # Merge all data files
    merged_df = pd.merge(left=diabetes, right=obesity, how='left', on='FIPS', copy=False)
    merged_df = pd.merge(left=merged_df, right=mortality, how='left', on = 'FIPS', copy=False)
    merged_df = pd.merge(left=merged_df, right=id_mortality, how='left', on='FIPS', copy=False)
    merged_df = pd.merge(left=merged_df, right=rd_mortality, how='left', on='FIPS', copy=False)

    return merged_df


def preprocess_JHU():
    # The Johns Hopkins COVID-19 dataset does not include data for individual counties in New York City
    # This data is retrieved from the New York City Public Health Department
    # Link: www1.nyc.gov/site/doh/covid/covid-19-data.page
    # Note: Daily data is obtained from the "Get the data" links on the Daily Counts graph, which are below
    bronx = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C3%2C0%0A03%2F01%2F2020%2C1%2C1%2C0%0A03%2F02%2F2020%2C0%2C9%2C0%0A03%2F03%2F2020%2C1%2C7%2C0%0A03%2F04%2F2020%2C0%2C6%2C0%0A03%2F05%2F2020%2C0%2C2%2C0%0A03%2F06%2F2020%2C2%2C5%2C0%0A03%2F07%2F2020%2C0%2C2%2C0%0A03%2F08%2F2020%2C4%2C0%2C0%0A03%2F09%2F2020%2C4%2C11%2C0%0A03%2F10%2F2020%2C8%2C8%2C0%0A03%2F11%2F2020%2C19%2C19%2C0%0A03%2F12%2F2020%2C29%2C18%2C0%0A03%2F13%2F2020%2C80%2C33%2C0%0A03%2F14%2F2020%2C85%2C26%2C0%0A03%2F15%2F2020%2C117%2C34%2C1%0A03%2F16%2F2020%2C303%2C64%2C3%0A03%2F17%2F2020%2C343%2C66%2C1%0A03%2F18%2F2020%2C483%2C101%2C1%0A03%2F19%2F2020%2C620%2C122%2C4%0A03%2F20%2F2020%2C718%2C109%2C13%0A03%2F21%2F2020%2C483%2C151%2C13%0A03%2F22%2F2020%2C491%2C161%2C12%0A03%2F23%2F2020%2C722%2C207%2C12%0A03%2F24%2F2020%2C927%2C255%2C14%0A03%2F25%2F2020%2C1054%2C290%2C30%0A03%2F26%2F2020%2C998%2C307%2C37%0A03%2F27%2F2020%2C1089%2C306%2C34%0A03%2F28%2F2020%2C761%2C300%2C61%0A03%2F29%2F2020%2C697%2C310%2C54%0A03%2F30%2F2020%2C1309%2C320%2C74%0A03%2F31%2F2020%2C1283%2C352%2C93%0A04%2F01%2F2020%2C1235%2C337%2C90%0A04%2F02%2F2020%2C1284%2C338%2C95%0A04%2F03%2F2020%2C1445%2C357%2C114%0A04%2F04%2F2020%2C1007%2C281%2C106%0A04%2F05%2F2020%2C816%2C316%2C122%0A04%2F06%2F2020%2C1512%2C380%2C109%0A04%2F07%2F2020%2C1462%2C330%2C114%0A04%2F08%2F2020%2C1288%2C365%2C106%0A04%2F09%2F2020%2C1278%2C301%2C108%0A04%2F10%2F2020%2C1229%2C304%2C118%0A04%2F11%2F2020%2C992%2C263%2C132%0A04%2F12%2F2020%2C758%2C236%2C106%0A04%2F13%2F2020%2C693%2C279%2C118%0A04%2F14%2F2020%2C1072%2C213%2C109%0A04%2F15%2F2020%2C1063%2C221%2C92%0A04%2F16%2F2020%2C933%2C197%2C83%0A04%2F17%2F2020%2C911%2C197%2C85%0A04%2F18%2F2020%2C548%2C153%2C57%0A04%2F19%2F2020%2C528%2C148%2C73%0A04%2F20%2F2020%2C975%2C164%2C76%0A04%2F21%2F2020%2C637%2C146%2C68%0A04%2F22%2F2020%2C920%2C126%2C67%0A04%2F23%2F2020%2C732%2C129%2C57%0A04%2F24%2F2020%2C578%2C113%2C61%0A04%2F25%2F2020%2C412%2C100%2C52%0A04%2F26%2F2020%2C194%2C88%2C52%0A04%2F27%2F2020%2C544%2C112%2C53%0A04%2F28%2F2020%2C667%2C110%2C55%0A04%2F29%2F2020%2C556%2C98%2C40%0A04%2F30%2F2020%2C477%2C70%2C44%0A05%2F01%2F2020%2C441%2C91%2C45%0A05%2F02%2F2020%2C259%2C61%2C49%0A05%2F03%2F2020%2C150%2C56%2C27%0A05%2F04%2F2020%2C347%2C68%2C35%0A05%2F05%2F2020%2C294%2C84%2C25%0A05%2F06%2F2020%2C281%2C71%2C25%0A05%2F07%2F2020%2C294%2C58%2C27%0A05%2F08%2F2020%2C251%2C70%2C21%0A05%2F09%2F2020%2C177%2C46%2C21%0A05%2F10%2F2020%2C75%2C35%2C13%0A05%2F11%2F2020%2C227%2C54%2C26%0A05%2F12%2F2020%2C353%2C53%2C20%0A05%2F13%2F2020%2C455%2C51%2C15%0A05%2F14%2F2020%2C255%2C46%2C8%0A05%2F15%2F2020%2C176%2C52%2C16%0A05%2F16%2F2020%2C108%2C27%2C26%0A05%2F17%2F2020%2C56%2C26%2C19%0A05%2F18%2F2020%2C185%2C33%2C11%0A05%2F19%2F2020%2C178%2C41%2C11%0A05%2F20%2F2020%2C274%2C38%2C15%0A05%2F21%2F2020%2C189%2C33%2C12%0A05%2F22%2F2020%2C247%2C48%2C11%0A05%2F23%2F2020%2C87%2C21%2C14%0A05%2F24%2F2020%2C96%2C23%2C12%0A05%2F25%2F2020%2C95%2C31%2C6%0A05%2F26%2F2020%2C266%2C36%2C9%0A05%2F27%2F2020%2C165%2C26%2C7%0A05%2F28%2F2020%2C105%2C24%2C8%0A05%2F29%2F2020%2C141%2C44%2C5%0A05%2F30%2F2020%2C60%2C22%2C12%0A05%2F31%2F2020%2C29%2C20%2C4%0A06%2F01%2F2020%2C115%2C28%2C3%0A06%2F02%2F2020%2C62%2C24%2C6%0A06%2F03%2F2020%2C34%2C14%2C5%0A06%2F04%2F2020%2C20%2C7%2C1%0A06%2F05%2F2020%2C2%2C0%2C0"

    brooklyn = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C4%2C0%0A03%2F01%2F2020%2C0%2C0%2C0%0A03%2F02%2F2020%2C0%2C4%2C0%0A03%2F03%2F2020%2C0%2C4%2C0%0A03%2F04%2F2020%2C1%2C5%2C0%0A03%2F05%2F2020%2C3%2C5%2C0%0A03%2F06%2F2020%2C1%2C2%2C0%0A03%2F07%2F2020%2C2%2C5%2C0%0A03%2F08%2F2020%2C5%2C9%2C0%0A03%2F09%2F2020%2C16%2C14%2C0%0A03%2F10%2F2020%2C11%2C13%2C0%0A03%2F11%2F2020%2C31%2C15%2C0%0A03%2F12%2F2020%2C96%2C26%2C0%0A03%2F13%2F2020%2C166%2C36%2C0%0A03%2F14%2F2020%2C163%2C36%2C1%0A03%2F15%2F2020%2C429%2C44%2C0%0A03%2F16%2F2020%2C739%2C81%2C1%0A03%2F17%2F2020%2C786%2C99%2C4%0A03%2F18%2F2020%2C968%2C109%2C6%0A03%2F19%2F2020%2C1208%2C146%2C6%0A03%2F20%2F2020%2C1140%2C186%2C10%0A03%2F21%2F2020%2C558%2C172%2C12%0A03%2F22%2F2020%2C757%2C180%2C10%0A03%2F23%2F2020%2C909%2C267%2C27%0A03%2F24%2F2020%2C1208%2C297%2C23%0A03%2F25%2F2020%2C1230%2C371%2C36%0A03%2F26%2F2020%2C1357%2C429%2C50%0A03%2F27%2F2020%2C1406%2C394%2C73%0A03%2F28%2F2020%2C849%2C351%2C74%0A03%2F29%2F2020%2C1120%2C408%2C87%0A03%2F30%2F2020%2C1746%2C488%2C106%0A03%2F31%2F2020%2C1493%2C449%2C122%0A04%2F01%2F2020%2C1588%2C448%2C129%0A04%2F02%2F2020%2C1636%2C398%2C163%0A04%2F03%2F2020%2C1442%2C397%2C135%0A04%2F04%2F2020%2C917%2C320%2C151%0A04%2F05%2F2020%2C1149%2C365%2C161%0A04%2F06%2F2020%2C1503%2C447%2C164%0A04%2F07%2F2020%2C1415%2C454%2C178%0A04%2F08%2F2020%2C1320%2C411%2C170%0A04%2F09%2F2020%2C1360%2C391%2C185%0A04%2F10%2F2020%2C1150%2C321%2C168%0A04%2F11%2F2020%2C1122%2C281%2C153%0A04%2F12%2F2020%2C697%2C250%2C200%0A04%2F13%2F2020%2C1061%2C320%2C157%0A04%2F14%2F2020%2C1032%2C250%2C153%0A04%2F15%2F2020%2C880%2C266%2C128%0A04%2F16%2F2020%2C880%2C231%2C123%0A04%2F17%2F2020%2C957%2C239%2C116%0A04%2F18%2F2020%2C574%2C165%2C113%0A04%2F19%2F2020%2C634%2C135%2C114%0A04%2F20%2F2020%2C979%2C203%2C94%0A04%2F21%2F2020%2C898%2C160%2C91%0A04%2F22%2F2020%2C854%2C156%2C104%0A04%2F23%2F2020%2C789%2C151%2C106%0A04%2F24%2F2020%2C627%2C138%2C93%0A04%2F25%2F2020%2C404%2C103%2C74%0A04%2F26%2F2020%2C333%2C88%2C60%0A04%2F27%2F2020%2C610%2C112%2C85%0A04%2F28%2F2020%2C714%2C116%2C57%0A04%2F29%2F2020%2C682%2C119%2C71%0A04%2F30%2F2020%2C599%2C89%2C65%0A05%2F01%2F2020%2C496%2C78%2C55%0A05%2F02%2F2020%2C263%2C56%2C46%0A05%2F03%2F2020%2C247%2C60%2C46%0A05%2F04%2F2020%2C464%2C83%2C41%0A05%2F05%2F2020%2C434%2C72%2C48%0A05%2F06%2F2020%2C452%2C69%2C37%0A05%2F07%2F2020%2C400%2C77%2C45%0A05%2F08%2F2020%2C348%2C74%2C42%0A05%2F09%2F2020%2C121%2C49%2C28%0A05%2F10%2F2020%2C191%2C41%2C24%0A05%2F11%2F2020%2C409%2C71%2C32%0A05%2F12%2F2020%2C400%2C56%2C32%0A05%2F13%2F2020%2C363%2C58%2C22%0A05%2F14%2F2020%2C332%2C57%2C14%0A05%2F15%2F2020%2C260%2C56%2C26%0A05%2F16%2F2020%2C163%2C42%2C21%0A05%2F17%2F2020%2C138%2C35%2C17%0A05%2F18%2F2020%2C270%2C52%2C14%0A05%2F19%2F2020%2C331%2C63%2C14%0A05%2F20%2F2020%2C308%2C49%2C19%0A05%2F21%2F2020%2C335%2C59%2C12%0A05%2F22%2F2020%2C364%2C58%2C13%0A05%2F23%2F2020%2C161%2C33%2C19%0A05%2F24%2F2020%2C176%2C34%2C12%0A05%2F25%2F2020%2C166%2C31%2C13%0A05%2F26%2F2020%2C332%2C33%2C10%0A05%2F27%2F2020%2C251%2C50%2C9%0A05%2F28%2F2020%2C221%2C42%2C14%0A05%2F29%2F2020%2C148%2C27%2C16%0A05%2F30%2F2020%2C94%2C28%2C11%0A05%2F31%2F2020%2C64%2C21%2C10%0A06%2F01%2F2020%2C150%2C30%2C7%0A06%2F02%2F2020%2C103%2C23%2C4%0A06%2F03%2F2020%2C59%2C24%2C4%0A06%2F04%2F2020%2C39%2C2%2C1%0A06%2F05%2F2020%2C5%2C0%2C0"

    manhattan = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C1%2C2%2C0%0A03%2F01%2F2020%2C0%2C0%2C0%0A03%2F02%2F2020%2C0%2C4%2C0%0A03%2F03%2F2020%2C0%2C2%2C0%0A03%2F04%2F2020%2C2%2C5%2C0%0A03%2F05%2F2020%2C0%2C6%2C0%0A03%2F06%2F2020%2C3%2C3%2C0%0A03%2F07%2F2020%2C1%2C4%2C0%0A03%2F08%2F2020%2C6%2C1%2C0%0A03%2F09%2F2020%2C25%2C12%2C0%0A03%2F10%2F2020%2C24%2C12%2C0%0A03%2F11%2F2020%2C61%2C21%2C0%0A03%2F12%2F2020%2C137%2C11%2C0%0A03%2F13%2F2020%2C182%2C27%2C0%0A03%2F14%2F2020%2C179%2C28%2C0%0A03%2F15%2F2020%2C209%2C32%2C2%0A03%2F16%2F2020%2C458%2C38%2C1%0A03%2F17%2F2020%2C566%2C57%2C0%0A03%2F18%2F2020%2C540%2C77%2C4%0A03%2F19%2F2020%2C553%2C90%2C4%0A03%2F20%2F2020%2C656%2C110%2C11%0A03%2F21%2F2020%2C401%2C112%2C5%0A03%2F22%2F2020%2C321%2C127%2C8%0A03%2F23%2F2020%2C536%2C171%2C7%0A03%2F24%2F2020%2C624%2C187%2C17%0A03%2F25%2F2020%2C594%2C180%2C20%0A03%2F26%2F2020%2C627%2C211%2C33%0A03%2F27%2F2020%2C657%2C202%2C41%0A03%2F28%2F2020%2C383%2C199%2C28%0A03%2F29%2F2020%2C405%2C159%2C35%0A03%2F30%2F2020%2C825%2C263%2C35%0A03%2F31%2F2020%2C637%2C219%2C43%0A04%2F01%2F2020%2C590%2C170%2C60%0A04%2F02%2F2020%2C656%2C225%2C63%0A04%2F03%2F2020%2C686%2C257%2C52%0A04%2F04%2F2020%2C390%2C198%2C63%0A04%2F05%2F2020%2C358%2C184%2C86%0A04%2F06%2F2020%2C719%2C259%2C69%0A04%2F07%2F2020%2C607%2C196%2C90%0A04%2F08%2F2020%2C558%2C176%2C65%0A04%2F09%2F2020%2C565%2C197%2C64%0A04%2F10%2F2020%2C502%2C192%2C68%0A04%2F11%2F2020%2C314%2C130%2C59%0A04%2F12%2F2020%2C253%2C142%2C63%0A04%2F13%2F2020%2C394%2C187%2C72%0A04%2F14%2F2020%2C444%2C159%2C59%0A04%2F15%2F2020%2C436%2C145%2C55%0A04%2F16%2F2020%2C361%2C109%2C58%0A04%2F17%2F2020%2C333%2C124%2C42%0A04%2F18%2F2020%2C187%2C86%2C56%0A04%2F19%2F2020%2C179%2C84%2C48%0A04%2F20%2F2020%2C378%2C92%2C50%0A04%2F21%2F2020%2C374%2C98%2C47%0A04%2F22%2F2020%2C387%2C106%2C38%0A04%2F23%2F2020%2C401%2C69%2C47%0A04%2F24%2F2020%2C414%2C92%2C50%0A04%2F25%2F2020%2C149%2C52%2C42%0A04%2F26%2F2020%2C98%2C52%2C33%0A04%2F27%2F2020%2C302%2C72%2C29%0A04%2F28%2F2020%2C322%2C71%2C36%0A04%2F29%2F2020%2C285%2C51%2C33%0A04%2F30%2F2020%2C218%2C40%2C33%0A05%2F01%2F2020%2C244%2C48%2C24%0A05%2F02%2F2020%2C139%2C28%2C23%0A05%2F03%2F2020%2C104%2C41%2C35%0A05%2F04%2F2020%2C214%2C47%2C18%0A05%2F05%2F2020%2C242%2C33%2C18%0A05%2F06%2F2020%2C166%2C33%2C17%0A05%2F07%2F2020%2C119%2C30%2C21%0A05%2F08%2F2020%2C101%2C38%2C14%0A05%2F09%2F2020%2C75%2C23%2C17%0A05%2F10%2F2020%2C95%2C21%2C19%0A05%2F11%2F2020%2C190%2C35%2C13%0A05%2F12%2F2020%2C164%2C31%2C14%0A05%2F13%2F2020%2C155%2C39%2C8%0A05%2F14%2F2020%2C151%2C29%2C16%0A05%2F15%2F2020%2C136%2C36%2C12%0A05%2F16%2F2020%2C58%2C15%2C9%0A05%2F17%2F2020%2C50%2C18%2C10%0A05%2F18%2F2020%2C132%2C27%2C10%0A05%2F19%2F2020%2C167%2C36%2C10%0A05%2F20%2F2020%2C164%2C21%2C12%0A05%2F21%2F2020%2C146%2C24%2C5%0A05%2F22%2F2020%2C155%2C35%2C5%0A05%2F23%2F2020%2C46%2C19%2C7%0A05%2F24%2F2020%2C70%2C21%2C6%0A05%2F25%2F2020%2C71%2C24%2C11%0A05%2F26%2F2020%2C126%2C24%2C6%0A05%2F27%2F2020%2C106%2C26%2C8%0A05%2F28%2F2020%2C93%2C27%2C3%0A05%2F29%2F2020%2C67%2C30%2C5%0A05%2F30%2F2020%2C36%2C11%2C9%0A05%2F31%2F2020%2C24%2C13%2C5%0A06%2F01%2F2020%2C65%2C19%2C2%0A06%2F02%2F2020%2C46%2C19%2C5%0A06%2F03%2F2020%2C44%2C19%2C2%0A06%2F04%2F2020%2C13%2C3%2C1%0A06%2F05%2F2020%2C3%2C0%2C0"

    queens = 'data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C2%2C0%0A03%2F01%2F2020%2C0%2C2%2C0%0A03%2F02%2F2020%2C0%2C5%2C0%0A03%2F03%2F2020%2C1%2C5%2C0%0A03%2F04%2F2020%2C2%2C3%2C0%0A03%2F05%2F2020%2C0%2C5%2C0%0A03%2F06%2F2020%2C1%2C7%2C0%0A03%2F07%2F2020%2C3%2C3%2C0%0A03%2F08%2F2020%2C5%2C5%2C0%0A03%2F09%2F2020%2C10%2C8%2C0%0A03%2F10%2F2020%2C24%2C23%2C0%0A03%2F11%2F2020%2C40%2C29%2C1%0A03%2F12%2F2020%2C79%2C28%2C0%0A03%2F13%2F2020%2C165%2C48%2C0%0A03%2F14%2F2020%2C194%2C57%2C1%0A03%2F15%2F2020%2C230%2C64%2C1%0A03%2F16%2F2020%2C530%2C105%2C4%0A03%2F17%2F2020%2C650%2C108%2C3%0A03%2F18%2F2020%2C830%2C152%2C9%0A03%2F19%2F2020%2C1065%2C160%2C6%0A03%2F20%2F2020%2C1184%2C224%2C9%0A03%2F21%2F2020%2C945%2C223%2C13%0A03%2F22%2F2020%2C695%2C223%2C14%0A03%2F23%2F2020%2C1190%2C336%2C28%0A03%2F24%2F2020%2C1390%2C356%2C34%0A03%2F25%2F2020%2C1569%2C401%2C30%0A03%2F26%2F2020%2C1640%2C425%2C56%0A03%2F27%2F2020%2C1571%2C413%2C56%0A03%2F28%2F2020%2C1200%2C440%2C89%0A03%2F29%2F2020%2C1075%2C450%2C92%0A03%2F30%2F2020%2C1836%2C540%2C94%0A03%2F31%2F2020%2C1791%2C553%2C93%0A04%2F01%2F2020%2C1763%2C514%2C136%0A04%2F02%2F2020%2C1807%2C557%2C133%0A04%2F03%2F2020%2C1749%2C514%2C154%0A04%2F04%2F2020%2C1196%2C462%2C149%0A04%2F05%2F2020%2C1131%2C385%2C176%0A04%2F06%2F2020%2C1907%2C524%2C198%0A04%2F07%2F2020%2C1938%2C515%2C180%0A04%2F08%2F2020%2C1839%2C509%2C172%0A04%2F09%2F2020%2C1543%2C449%2C154%0A04%2F10%2F2020%2C1317%2C441%2C144%0A04%2F11%2F2020%2C970%2C351%2C153%0A04%2F12%2F2020%2C911%2C303%2C160%0A04%2F13%2F2020%2C968%2C351%2C177%0A04%2F14%2F2020%2C1290%2C379%2C160%0A04%2F15%2F2020%2C1171%2C304%2C139%0A04%2F16%2F2020%2C1137%2C281%2C120%0A04%2F17%2F2020%2C1097%2C285%2C109%0A04%2F18%2F2020%2C701%2C209%2C114%0A04%2F19%2F2020%2C869%2C184%2C119%0A04%2F20%2F2020%2C1219%2C219%2C113%0A04%2F21%2F2020%2C930%2C208%2C87%0A04%2F22%2F2020%2C1109%2C176%2C74%0A04%2F23%2F2020%2C789%2C151%2C86%0A04%2F24%2F2020%2C774%2C161%2C81%0A04%2F25%2F2020%2C540%2C115%2C62%0A04%2F26%2F2020%2C334%2C122%2C78%0A04%2F27%2F2020%2C719%2C119%2C80%0A04%2F28%2F2020%2C890%2C119%2C61%0A04%2F29%2F2020%2C692%2C116%2C72%0A04%2F30%2F2020%2C591%2C112%2C55%0A05%2F01%2F2020%2C620%2C105%2C70%0A05%2F02%2F2020%2C334%2C88%2C55%0A05%2F03%2F2020%2C247%2C76%2C44%0A05%2F04%2F2020%2C433%2C78%2C48%0A05%2F05%2F2020%2C460%2C60%2C39%0A05%2F06%2F2020%2C445%2C65%2C52%0A05%2F07%2F2020%2C356%2C62%2C34%0A05%2F08%2F2020%2C341%2C51%2C40%0A05%2F09%2F2020%2C255%2C39%2C30%0A05%2F10%2F2020%2C85%2C39%2C27%0A05%2F11%2F2020%2C378%2C72%2C23%0A05%2F12%2F2020%2C314%2C50%2C15%0A05%2F13%2F2020%2C304%2C47%2C22%0A05%2F14%2F2020%2C331%2C62%2C20%0A05%2F15%2F2020%2C265%2C65%2C25%0A05%2F16%2F2020%2C135%2C59%2C17%0A05%2F17%2F2020%2C106%2C36%2C24%0A05%2F18%2F2020%2C274%2C49%2C14%0A05%2F19%2F2020%2C288%2C50%2C11%0A05%2F20%2F2020%2C238%2C40%2C21%0A05%2F21%2F2020%2C304%2C38%2C8%0A05%2F22%2F2020%2C224%2C51%2C25%0A05%2F23%2F2020%2C129%2C42%2C12%0A05%2F24%2F2020%2C118%2C27%2C10%0A05%2F25%2F2020%2C106%2C45%2C9%0A05%2F26%2F2020%2C260%2C43%2C7%0A05%2F27%2F2020%2C161%2C53%2C15%0A05%2F28%2F2020%2C160%2C31%2C7%0A05%2F29%2F2020%2C193%2C43%2C14%0A05%2F30%2F2020%2C92%2C25%2C16%0A05%2F31%2F2020%2C60%2C31%2C11%0A06%2F01%2F2020%2C121%2C34%2C10%0A06%2F02%2F2020%2C90%2C34%2C9%0A06%2F03%2F2020%2C58%2C17%2C2%0A06%2F04%2F2020%2C28%2C1%2C1%0A06%2F05%2F2020%2C7%2C0%2C0'

    staten_island = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C0%2C0%0A03%2F01%2F2020%2C0%2C1%2C0%0A03%2F02%2F2020%2C0%2C0%2C0%0A03%2F03%2F2020%2C0%2C1%2C0%0A03%2F04%2F2020%2C0%2C2%2C0%0A03%2F05%2F2020%2C0%2C1%2C0%0A03%2F06%2F2020%2C1%2C2%2C0%0A03%2F07%2F2020%2C1%2C0%2C0%0A03%2F08%2F2020%2C1%2C0%2C0%0A03%2F09%2F2020%2C3%2C3%2C0%0A03%2F10%2F2020%2C2%2C5%2C0%0A03%2F11%2F2020%2C3%2C3%2C0%0A03%2F12%2F2020%2C13%2C5%2C0%0A03%2F13%2F2020%2C26%2C3%2C0%0A03%2F14%2F2020%2C22%2C8%2C0%0A03%2F15%2F2020%2C46%2C16%2C1%0A03%2F16%2F2020%2C91%2C17%2C0%0A03%2F17%2F2020%2C108%2C21%2C0%0A03%2F18%2F2020%2C150%2C23%2C0%0A03%2F19%2F2020%2C258%2C31%2C4%0A03%2F20%2F2020%2C309%2C30%2C3%0A03%2F21%2F2020%2C248%2C34%2C1%0A03%2F22%2F2020%2C316%2C32%2C6%0A03%2F23%2F2020%2C208%2C46%2C8%0A03%2F24%2F2020%2C349%2C48%2C6%0A03%2F25%2F2020%2C394%2C49%2C4%0A03%2F26%2F2020%2C403%2C47%2C10%0A03%2F27%2F2020%2C372%2C57%2C7%0A03%2F28%2F2020%2C266%2C53%2C13%0A03%2F29%2F2020%2C230%2C57%2C17%0A03%2F30%2F2020%2C397%2C68%2C10%0A03%2F31%2F2020%2C233%2C69%2C21%0A04%2F01%2F2020%2C263%2C72%2C16%0A04%2F02%2F2020%2C370%2C79%2C30%0A04%2F03%2F2020%2C343%2C63%2C29%0A04%2F04%2F2020%2C346%2C51%2C20%0A04%2F05%2F2020%2C323%2C65%2C22%0A04%2F06%2F2020%2C730%2C81%2C24%0A04%2F07%2F2020%2C629%2C70%2C28%0A04%2F08%2F2020%2C558%2C56%2C34%0A04%2F09%2F2020%2C297%2C57%2C25%0A04%2F10%2F2020%2C300%2C52%2C19%0A04%2F11%2F2020%2C311%2C48%2C27%0A04%2F12%2F2020%2C252%2C44%2C26%0A04%2F13%2F2020%2C185%2C56%2C25%0A04%2F14%2F2020%2C289%2C52%2C23%0A04%2F15%2F2020%2C317%2C34%2C24%0A04%2F16%2F2020%2C209%2C38%2C14%0A04%2F17%2F2020%2C281%2C38%2C15%0A04%2F18%2F2020%2C153%2C25%2C19%0A04%2F19%2F2020%2C134%2C30%2C19%0A04%2F20%2F2020%2C224%2C28%2C16%0A04%2F21%2F2020%2C216%2C27%2C11%0A04%2F22%2F2020%2C173%2C20%2C14%0A04%2F23%2F2020%2C128%2C19%2C13%0A04%2F24%2F2020%2C143%2C34%2C13%0A04%2F25%2F2020%2C88%2C26%2C9%0A04%2F26%2F2020%2C46%2C23%2C7%0A04%2F27%2F2020%2C107%2C20%2C9%0A04%2F28%2F2020%2C129%2C19%2C8%0A04%2F29%2F2020%2C124%2C19%2C14%0A04%2F30%2F2020%2C130%2C18%2C11%0A05%2F01%2F2020%2C77%2C12%2C8%0A05%2F02%2F2020%2C60%2C18%2C12%0A05%2F03%2F2020%2C35%2C14%2C15%0A05%2F04%2F2020%2C90%2C14%2C8%0A05%2F05%2F2020%2C78%2C11%2C12%0A05%2F06%2F2020%2C59%2C6%2C7%0A05%2F07%2F2020%2C60%2C8%2C3%0A05%2F08%2F2020%2C42%2C9%2C5%0A05%2F09%2F2020%2C32%2C6%2C3%0A05%2F10%2F2020%2C13%2C5%2C8%0A05%2F11%2F2020%2C27%2C3%2C3%0A05%2F12%2F2020%2C53%2C8%2C6%0A05%2F13%2F2020%2C48%2C9%2C6%0A05%2F14%2F2020%2C41%2C12%2C5%0A05%2F15%2F2020%2C33%2C7%2C6%0A05%2F16%2F2020%2C25%2C8%2C2%0A05%2F17%2F2020%2C10%2C4%2C2%0A05%2F18%2F2020%2C38%2C2%2C2%0A05%2F19%2F2020%2C42%2C8%2C5%0A05%2F20%2F2020%2C56%2C6%2C7%0A05%2F21%2F2020%2C66%2C10%2C3%0A05%2F22%2F2020%2C28%2C6%2C5%0A05%2F23%2F2020%2C35%2C5%2C2%0A05%2F24%2F2020%2C14%2C4%2C5%0A05%2F25%2F2020%2C15%2C5%2C3%0A05%2F26%2F2020%2C50%2C3%2C1%0A05%2F27%2F2020%2C43%2C4%2C1%0A05%2F28%2F2020%2C23%2C7%2C1%0A05%2F29%2F2020%2C20%2C7%2C2%0A05%2F30%2F2020%2C13%2C3%2C0%0A05%2F31%2F2020%2C10%2C3%2C2%0A06%2F01%2F2020%2C32%2C1%2C2%0A06%2F02%2F2020%2C28%2C4%2C1%0A06%2F03%2F2020%2C12%2C2%2C2%0A06%2F04%2F2020%2C2%2C0%2C0%0A06%2F05%2F2020%2C0%2C0%2C0"

    nyFIPS = {"bronx" : "36005", "brooklyn": "36047", "manhattan":"36061", "queens":"36081", "staten_island":"36085"}

    def read_NYC_county(county_link, fips):
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

    # Get daily case data from New York City counties
    bronx = read_NYC_county(bronx, "bronx")
    brooklyn = read_NYC_county(brooklyn, "brooklyn")
    manhattan = read_NYC_county(manhattan, "manhattan")
    queens = read_NYC_county(queens, "queens")
    staten_island = read_NYC_county(staten_island, "staten_island")

    # Get all other data from Johns Hopkins
    jhu_data = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv", dtype={"FIPS": str})
    jhu_data = jhu_data[jhu_data['FIPS'].notnull()]
    jhu_data['FIPS'] = jhu_data['FIPS'].apply(lambda x : process_FIPS(x))
    jhu_data = jhu_data.drop(["Admin2","Province_State","Country_Region","Lat","Long_","Combined_Key","UID","iso2","iso3","code3"], axis=1)
    jhu_data = jhu_data.melt(id_vars=['FIPS'], var_name = 'date', value_name = 'confirmed_cases')

    # Merge Johns Hopkins Data with NYC data
    ny_fips_list = ["36005","36047","36061", "36081", "36085"]
    full_data = pd.concat([jhu_data[~jhu_data['FIPS'].isin(ny_fips_list)], bronx, brooklyn,manhattan,queens,staten_island]).sort_values(['FIPS','date']).reset_index(drop=True)

    # Compute 7-day (weekly) rolling average of cases for each county
    full_data['confirmed_cases'] = pd.Series(full_data.groupby("FIPS")['confirmed_cases'].rolling(7).mean()).reset_index(drop=True)
    full_data = full_data[full_data['confirmed_cases'].notnull()]

    # Move dates forward by 1 day so that movement averages represent data from past week
    full_data['date'] = pd.to_datetime(full_data['date'])
    full_data['date'] = full_data['date'].apply(pd.DateOffset(1))

    # Normalize confirmed cases for population and export to csv
    census_data = preprocess_census(drop_tot = False)[['TOT_POP', 'FIPS']]

    merged_df = pd.merge(left=census_data, right=full_data, how='left', on='FIPS', copy=False)
    merged_df['confirmed_cases'] = (merged_df['confirmed_cases']/merged_df['TOT_POP'] * 100000).round()
    merged_df = merged_df.drop('TOT_POP', axis=1)
    startdate = datetime.strptime('2020-2-15', '%Y-%m-%d')
    merged_df = merged_df[merged_df['date'] >= startdate]

    merged_df.to_csv('data/jhu_data.csv', sep=",", index=False)

    return merged_df

def preprocess_Rt():

    state_map, fips_data = get_state_fips()

    # Rt calculations from rt.live
    rt_data = pd.read_csv("https://d14wlfuexuxgcm.cloudfront.net/covid/rt.csv", usecols=['date', 'region', 'mean'])
    rt_data['state'] = rt_data['region'].apply(lambda x : state_map[x])

    date_list = rt_data['date'].unique()
    fips_list = fips_data['FIPS'].unique()

    df = pd.DataFrame()
    df['FIPS'] = fips_list
    df['date'] = [date_list]*len(fips_list)
    df = df.explode('date').reset_index(drop=True)
    df['state'] = df['FIPS'].apply(lambda x : x[0:2])

    # Rt calculations from covid19-projections.com
    projections = pd.read_csv("https://raw.githubusercontent.com/youyanggu/covid19_projections/master/projections/combined/latest_us.csv", usecols=['date', 'region', 'r_values_mean'])
    projections['datetime'] = projections['date'].apply(lambda x: pd.datetime.strptime(x, '%Y-%m-%d'))
    projections = projections[(projections['region'].notnull()) & (projections['datetime'] < pd.to_datetime('today'))]
    projections.insert(0, "state", projections['region'].apply(lambda x : state_map[x]))
    projections = projections.drop(['datetime', 'region'], axis=1).reset_index(drop=True)

    # Merge Rt values from both sources together
    merged_df = pd.merge(left=df, right=rt_data, how='left', on=['state', 'date'], copy=False)
    merged_df = merged_df[merged_df['region'].notnull()]
    merged_df = merged_df.rename({'mean':'rt_mean_MIT'},axis=1)
    merged_df = pd.merge(left=merged_df, right=projections, on=['state', 'date'], copy=False)

    merged_df.to_csv("data/rt_data.csv", index=False, sep=',')

    return merged_df

def preprocess_testing():

    state_map, fips_data = get_state_fips()

    # State testing data obtained from the COVID Tracking Project (www.covidtracking.com)
    testing = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv", usecols = ['date', 'state', 'totalTestResultsIncrease', 'positiveIncrease'], dtype = {'date':str})
    testing['state'] = testing['state'].apply(lambda x : state_map[x])
    testing['date'] = pd.to_datetime(testing['date'])
    testing = testing.sort_values(['state','date']).reset_index(drop=True)

    # Compute 7 day (weekly) rolling averages for state testing data
    testing['positiveIncrease'] = pd.Series(testing.groupby("state")['positiveIncrease'].rolling(7).mean()).reset_index(drop=True)
    testing['totalTestResultsIncrease'] = pd.Series(testing.groupby("state")['totalTestResultsIncrease'].rolling(7).mean()).reset_index(drop=True)

    # Move dates forward by 1 day so that movement averages represent data from past week
    testing['date'] = testing['date'].apply(pd.DateOffset(1))
    testing['date'] = testing['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    # Source: US Census
    # Link: www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/
    # File: nst-est2019-alldata.csv
    state_populations = pd.read_csv("data/nst-est2019-alldata.csv", usecols = ['SUMLEV', 'STATE', 'POPESTIMATE2019'], dtype={'STATE':str, 'POPESTIMATE2019':float})

    # Process state population data
    state_populations = state_populations[state_populations['SUMLEV'] == 40].drop(['SUMLEV'], axis=1).rename({'STATE':'state', 'POPESTIMATE2019': 'population'}, axis=1).reset_index(drop=True)

    # Merge state population and state testing data
    testing_pop = pd.merge(left=testing, right=state_populations, how='left', on='state', copy=False)
    testing_pop['positiveIncrease'] = (testing_pop['positiveIncrease']/testing_pop['population']) * 100000
    testing_pop['totalTestResultsIncrease'] = (testing_pop['totalTestResultsIncrease']/testing_pop['population']) * 100000
    testing_pop = testing_pop.dropna().drop('population', axis=1)

    # Get dataframe of all dates mapped to all FIPS from the Rt data
    fips_df = pd.read_csv("data/rt_data.csv", dtype={'FIPS':str,'state':str}, usecols=['FIPS','date','state'])

    merged_df = pd.merge(left=fips_df, right=testing_pop, how='left', on=['state', 'date'], copy=False)
    merged_df = merged_df.drop(['state'], axis=1)

    merged_df.to_csv("data/testing_data.csv", sep=',', index=False)

    return merged_df

def merge_data(save_files = False, mode = "training"):

    census = preprocess_census(use_reduced=True)

    disparities = preprocess_disparities()
    health = merge_health_data()
    smoking = preprocess_smoking_prevalence()

    print("Updating Facebook Data - This will take a while")
    mobility = preprocess_facebook()

    print("Updating JHU Data - This will take a while")
    cases = preprocess_JHU()

    print("Updating Rt Data - This will take a while")
    rt = preprocess_Rt()

    print("Updating Testing Data - This will take a while")
    testing = preprocess_testing()

    print("Processing and exporting data")
    census['FIPS'] = census['FIPS'].astype(int)
    disparities['FIPS'] = disparities['FIPS'].astype(int)
    health['FIPS'] = health['FIPS'].astype(int)
    mobility['FIPS'] = mobility['FIPS'].astype(int)
    mobility['date'] = mobility['date'].astype(str)
    cases['FIPS'] = cases['FIPS'].astype(int)
    cases['date'] = cases['date'].astype(str)
    rt['FIPS'] = rt['FIPS'].astype(int)
    rt['date'] = rt['date'].astype(str)
    testing['FIPS'] = testing['FIPS'].astype(int)
    testing['date'] = testing['date'].astype(str)

    merged_DF = pd.merge(left=rt, right=testing, how='left', on=['FIPS', 'date'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=cases, how='left', on=['FIPS', 'date'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=mobility, how='left', on=['FIPS', 'date'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=health, how='left', on=['FIPS'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=disparities, how='left', on=['FIPS'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right = smoking, how='left', on=['region', 'Location'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=census, how='left', on=['FIPS'], copy=False).sort_values(['FIPS', 'date']).reset_index(drop=True)

    locations = merged_DF['Location']
    merged_DF = merged_DF.drop('Location', axis=1)
    merged_DF.insert(0, 'Location', locations)

    columns = merged_DF.columns.tolist()
    columns.remove('fb_stationary')
    columns.remove('fb_movement_change')

    cleaned_DF = merged_DF.dropna(subset=columns)
    unused_DF = merged_DF[~merged_DF.index.isin(cleaned_DF.index)]
    training_mobility = cleaned_DF.dropna()
    maxes = training_mobility.groupby('FIPS')['date'].transform(max)
    latest_mobility = training_mobility.loc[training_mobility['date'] == maxes]
    no_mobility = cleaned_DF[~cleaned_DF.index.isin(training_mobility.index)]
    no_mobility = no_mobility.drop(['fb_stationary', 'fb_movement_change'], axis=1)
    maxes = no_mobility.groupby('FIPS')['date'].transform(max)
    latest_no_mobility = no_mobility.loc[no_mobility['date'] == maxes]
    training_no_mobility = cleaned_DF.drop(['fb_stationary', 'fb_movement_change'], axis=1)

    if save_files == True:
        unused_DF.to_csv(os.path.split(os.getcwd())[0] + "/unused_data.csv", index=False)
        training_mobility.to_csv(os.path.split(os.getcwd())[0] + "/training_mobility.csv", index=False)
        latest_mobility.to_csv(os.path.split(os.getcwd())[0] + "/latest_mobility.csv", index=False)
        latest_no_mobility.to_csv(os.path.split(os.getcwd())[0] + "/latest_no_mobility.csv", index=False)
        training_no_mobility.to_csv(os.path.split(os.getcwd())[0] + "/training_no_mobility.csv", index=False)

    if mode == "training":
        return training_mobility, training_no_mobility
    if mode == "predictions":
        return latest_mobility, latest_no_mobility

if __name__ == '__main__':
    merge_data(save_files=True)
