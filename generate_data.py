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
from preprocess import get_latest_file, get_facebook_data
from datetime import date

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__version__ = '1.0.2'
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


def preprocess_census(year = 2018, drop_tot = False, use_reduced = False):
    # This is static data, so the normal output of this function is stored and used to save time
    if use_reduced == True:
        data = pd.read_csv("data/census.csv", dtype={'FIPS': str})
        return data

    # Import census data file (in same directory as repository)
    # Source: US census
    # Link: www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html
    # File: Annual County Resident Population Estimates by Age, Sex, Race, and Hispanic Origin: April 1, 2010 to July 1, 2018 (CC-EST2018-ALLDATA)
    #census_file = os.path.split(os.getcwd())[0] + "/cc-est2018-alldata.csv"
    census_file = "data/cc-est2018-alldata.csv.gz"
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

    # Preprocess file
    data_path = get_latest_file('facebook')
    df = pd.read_csv(data_path, dtype={'polygon_id':str})
    df = df[['ds', 'polygon_id', 'all_day_bing_tiles_visited_relative_change', 'all_day_ratio_single_tile_users']]
    df = df.rename({'polygon_id':'FIPS','ds':'date','all_day_bing_tiles_visited_relative_change':'fb_movement_change', 'all_day_ratio_single_tile_users':'fb_stationary'}, axis=1)
    df = df.reset_index(drop=True)

    # Compute 7 day (weekly) rolling averages for movement data
    df['fb_movement_change'] = pd.Series(df.groupby("FIPS")['fb_movement_change'].rolling(14).mean()).reset_index(drop=True)
    df['fb_stationary'] = pd.Series(df.groupby("FIPS")['fb_stationary'].rolling(14).mean()).reset_index(drop=True)

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
    bronx = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C3%2C0%0A03%2F01%2F2020%2C1%2C1%2C0%0A03%2F02%2F2020%2C0%2C9%2C0%0A03%2F03%2F2020%2C1%2C7%2C0%0A03%2F04%2F2020%2C0%2C6%2C0%0A03%2F05%2F2020%2C0%2C2%2C0%0A03%2F06%2F2020%2C2%2C5%2C0%0A03%2F07%2F2020%2C0%2C2%2C0%0A03%2F08%2F2020%2C4%2C2%2C0%0A03%2F09%2F2020%2C4%2C11%2C0%0A03%2F10%2F2020%2C8%2C8%2C0%0A03%2F11%2F2020%2C19%2C20%2C0%0A03%2F12%2F2020%2C29%2C16%2C0%0A03%2F13%2F2020%2C79%2C34%2C0%0A03%2F14%2F2020%2C86%2C26%2C0%0A03%2F15%2F2020%2C118%2C34%2C1%0A03%2F16%2F2020%2C303%2C65%2C3%0A03%2F17%2F2020%2C343%2C65%2C1%0A03%2F18%2F2020%2C482%2C100%2C1%0A03%2F19%2F2020%2C620%2C123%2C4%0A03%2F20%2F2020%2C719%2C112%2C13%0A03%2F21%2F2020%2C484%2C152%2C12%0A03%2F22%2F2020%2C491%2C163%2C12%0A03%2F23%2F2020%2C726%2C207%2C12%0A03%2F24%2F2020%2C926%2C254%2C14%0A03%2F25%2F2020%2C1054%2C289%2C31%0A03%2F26%2F2020%2C999%2C305%2C37%0A03%2F27%2F2020%2C1086%2C305%2C35%0A03%2F28%2F2020%2C763%2C303%2C62%0A03%2F29%2F2020%2C700%2C311%2C55%0A03%2F30%2F2020%2C1310%2C322%2C76%0A03%2F31%2F2020%2C1285%2C358%2C97%0A04%2F01%2F2020%2C1236%2C341%2C94%0A04%2F02%2F2020%2C1285%2C339%2C96%0A04%2F03%2F2020%2C1445%2C353%2C116%0A04%2F04%2F2020%2C1007%2C284%2C106%0A04%2F05%2F2020%2C818%2C318%2C124%0A04%2F06%2F2020%2C1512%2C383%2C111%0A04%2F07%2F2020%2C1466%2C333%2C114%0A04%2F08%2F2020%2C1297%2C370%2C114%0A04%2F09%2F2020%2C1280%2C302%2C109%0A04%2F10%2F2020%2C1232%2C304%2C119%0A04%2F11%2F2020%2C994%2C267%2C133%0A04%2F12%2F2020%2C759%2C237%2C110%0A04%2F13%2F2020%2C693%2C277%2C123%0A04%2F14%2F2020%2C1074%2C216%2C111%0A04%2F15%2F2020%2C1061%2C220%2C93%0A04%2F16%2F2020%2C932%2C199%2C85%0A04%2F17%2F2020%2C910%2C194%2C88%0A04%2F18%2F2020%2C548%2C156%2C61%0A04%2F19%2F2020%2C530%2C150%2C78%0A04%2F20%2F2020%2C975%2C164%2C78%0A04%2F21%2F2020%2C637%2C149%2C69%0A04%2F22%2F2020%2C921%2C130%2C66%0A04%2F23%2F2020%2C732%2C130%2C59%0A04%2F24%2F2020%2C579%2C115%2C62%0A04%2F25%2F2020%2C411%2C102%2C56%0A04%2F26%2F2020%2C195%2C87%2C54%0A04%2F27%2F2020%2C545%2C114%2C54%0A04%2F28%2F2020%2C668%2C109%2C56%0A04%2F29%2F2020%2C556%2C97%2C40%0A04%2F30%2F2020%2C478%2C70%2C45%0A05%2F01%2F2020%2C441%2C92%2C45%0A05%2F02%2F2020%2C259%2C63%2C49%0A05%2F03%2F2020%2C150%2C57%2C27%0A05%2F04%2F2020%2C347%2C68%2C35%0A05%2F05%2F2020%2C294%2C85%2C27%0A05%2F06%2F2020%2C281%2C71%2C28%0A05%2F07%2F2020%2C295%2C59%2C28%0A05%2F08%2F2020%2C253%2C71%2C22%0A05%2F09%2F2020%2C177%2C47%2C21%0A05%2F10%2F2020%2C75%2C36%2C13%0A05%2F11%2F2020%2C227%2C53%2C28%0A05%2F12%2F2020%2C354%2C52%2C20%0A05%2F13%2F2020%2C454%2C49%2C16%0A05%2F14%2F2020%2C255%2C47%2C9%0A05%2F15%2F2020%2C177%2C54%2C16%0A05%2F16%2F2020%2C110%2C30%2C26%0A05%2F17%2F2020%2C56%2C25%2C19%0A05%2F18%2F2020%2C186%2C35%2C10%0A05%2F19%2F2020%2C177%2C42%2C11%0A05%2F20%2F2020%2C275%2C40%2C15%0A05%2F21%2F2020%2C192%2C32%2C12%0A05%2F22%2F2020%2C259%2C42%2C12%0A05%2F23%2F2020%2C87%2C25%2C17%0A05%2F24%2F2020%2C96%2C26%2C13%0A05%2F25%2F2020%2C97%2C31%2C8%0A05%2F26%2F2020%2C270%2C41%2C10%0A05%2F27%2F2020%2C173%2C24%2C9%0A05%2F28%2F2020%2C111%2C23%2C12%0A05%2F29%2F2020%2C158%2C43%2C7%0A05%2F30%2F2020%2C75%2C26%2C12%0A05%2F31%2F2020%2C30%2C18%2C6%0A06%2F01%2F2020%2C151%2C26%2C3%0A06%2F02%2F2020%2C110%2C26%2C7%0A06%2F03%2F2020%2C100%2C19%2C10%0A06%2F04%2F2020%2C113%2C26%2C3%0A06%2F05%2F2020%2C102%2C16%2C7%0A06%2F06%2F2020%2C51%2C19%2C12%0A06%2F07%2F2020%2C42%2C18%2C7%0A06%2F08%2F2020%2C97%2C16%2C10%0A06%2F09%2F2020%2C79%2C16%2C6%0A06%2F10%2F2020%2C74%2C16%2C8%0A06%2F11%2F2020%2C60%2C12%2C5%0A06%2F12%2F2020%2C76%2C12%2C5%0A06%2F13%2F2020%2C44%2C7%2C4%0A06%2F14%2F2020%2C27%2C13%2C8%0A06%2F15%2F2020%2C68%2C13%2C5%0A06%2F16%2F2020%2C73%2C11%2C4%0A06%2F17%2F2020%2C68%2C13%2C2%0A06%2F18%2F2020%2C59%2C6%2C1%0A06%2F19%2F2020%2C77%2C9%2C3%0A06%2F20%2F2020%2C52%2C5%2C5%0A06%2F21%2F2020%2C25%2C7%2C5%0A06%2F22%2F2020%2C83%2C8%2C2%0A06%2F23%2F2020%2C44%2C13%2C8%0A06%2F24%2F2020%2C63%2C6%2C2%0A06%2F25%2F2020%2C41%2C13%2C3%0A06%2F26%2F2020%2C28%2C10%2C4%0A06%2F27%2F2020%2C12%2C4%2C0%0A06%2F28%2F2020%2C11%2C0%2C1%0A06%2F29%2F2020%2C1%2C0%2C0"

    brooklyn = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C4%2C0%0A03%2F01%2F2020%2C0%2C0%2C0%0A03%2F02%2F2020%2C0%2C4%2C0%0A03%2F03%2F2020%2C0%2C5%2C0%0A03%2F04%2F2020%2C1%2C5%2C0%0A03%2F05%2F2020%2C3%2C5%2C0%0A03%2F06%2F2020%2C1%2C3%2C0%0A03%2F07%2F2020%2C2%2C6%2C0%0A03%2F08%2F2020%2C5%2C9%2C0%0A03%2F09%2F2020%2C16%2C15%2C0%0A03%2F10%2F2020%2C11%2C13%2C0%0A03%2F11%2F2020%2C31%2C15%2C0%0A03%2F12%2F2020%2C96%2C30%2C0%0A03%2F13%2F2020%2C166%2C39%2C0%0A03%2F14%2F2020%2C164%2C38%2C1%0A03%2F15%2F2020%2C430%2C43%2C0%0A03%2F16%2F2020%2C740%2C87%2C1%0A03%2F17%2F2020%2C786%2C99%2C4%0A03%2F18%2F2020%2C970%2C114%2C6%0A03%2F19%2F2020%2C1208%2C150%2C6%0A03%2F20%2F2020%2C1140%2C187%2C11%0A03%2F21%2F2020%2C557%2C172%2C12%0A03%2F22%2F2020%2C756%2C182%2C10%0A03%2F23%2F2020%2C912%2C278%2C27%0A03%2F24%2F2020%2C1213%2C301%2C23%0A03%2F25%2F2020%2C1235%2C375%2C36%0A03%2F26%2F2020%2C1365%2C453%2C50%0A03%2F27%2F2020%2C1417%2C407%2C75%0A03%2F28%2F2020%2C856%2C367%2C78%0A03%2F29%2F2020%2C1136%2C422%2C90%0A03%2F30%2F2020%2C1754%2C507%2C106%0A03%2F31%2F2020%2C1507%2C477%2C126%0A04%2F01%2F2020%2C1597%2C468%2C135%0A04%2F02%2F2020%2C1640%2C405%2C168%0A04%2F03%2F2020%2C1445%2C405%2C140%0A04%2F04%2F2020%2C917%2C342%2C162%0A04%2F05%2F2020%2C1150%2C373%2C167%0A04%2F06%2F2020%2C1501%2C467%2C168%0A04%2F07%2F2020%2C1418%2C482%2C179%0A04%2F08%2F2020%2C1322%2C423%2C172%0A04%2F09%2F2020%2C1369%2C413%2C189%0A04%2F10%2F2020%2C1155%2C339%2C177%0A04%2F11%2F2020%2C1127%2C301%2C158%0A04%2F12%2F2020%2C700%2C261%2C200%0A04%2F13%2F2020%2C1063%2C341%2C158%0A04%2F14%2F2020%2C1036%2C275%2C153%0A04%2F15%2F2020%2C884%2C282%2C131%0A04%2F16%2F2020%2C884%2C247%2C126%0A04%2F17%2F2020%2C958%2C260%2C117%0A04%2F18%2F2020%2C574%2C176%2C117%0A04%2F19%2F2020%2C635%2C140%2C117%0A04%2F20%2F2020%2C981%2C213%2C95%0A04%2F21%2F2020%2C899%2C174%2C91%0A04%2F22%2F2020%2C854%2C161%2C108%0A04%2F23%2F2020%2C790%2C160%2C106%0A04%2F24%2F2020%2C628%2C142%2C93%0A04%2F25%2F2020%2C404%2C105%2C76%0A04%2F26%2F2020%2C332%2C88%2C61%0A04%2F27%2F2020%2C610%2C117%2C89%0A04%2F28%2F2020%2C715%2C124%2C57%0A04%2F29%2F2020%2C682%2C120%2C72%0A04%2F30%2F2020%2C599%2C98%2C66%0A05%2F01%2F2020%2C496%2C88%2C55%0A05%2F02%2F2020%2C264%2C63%2C46%0A05%2F03%2F2020%2C248%2C61%2C46%0A05%2F04%2F2020%2C463%2C90%2C42%0A05%2F05%2F2020%2C434%2C77%2C49%0A05%2F06%2F2020%2C451%2C77%2C38%0A05%2F07%2F2020%2C401%2C87%2C45%0A05%2F08%2F2020%2C349%2C79%2C43%0A05%2F09%2F2020%2C121%2C57%2C28%0A05%2F10%2F2020%2C191%2C43%2C26%0A05%2F11%2F2020%2C409%2C78%2C32%0A05%2F12%2F2020%2C400%2C57%2C33%0A05%2F13%2F2020%2C364%2C68%2C22%0A05%2F14%2F2020%2C332%2C61%2C14%0A05%2F15%2F2020%2C260%2C60%2C26%0A05%2F16%2F2020%2C164%2C48%2C24%0A05%2F17%2F2020%2C138%2C37%2C19%0A05%2F18%2F2020%2C270%2C59%2C15%0A05%2F19%2F2020%2C331%2C65%2C16%0A05%2F20%2F2020%2C326%2C50%2C21%0A05%2F21%2F2020%2C346%2C66%2C15%0A05%2F22%2F2020%2C387%2C61%2C14%0A05%2F23%2F2020%2C163%2C34%2C20%0A05%2F24%2F2020%2C181%2C35%2C12%0A05%2F25%2F2020%2C174%2C33%2C14%0A05%2F26%2F2020%2C339%2C34%2C11%0A05%2F27%2F2020%2C261%2C53%2C11%0A05%2F28%2F2020%2C227%2C48%2C13%0A05%2F29%2F2020%2C177%2C31%2C16%0A05%2F30%2F2020%2C110%2C29%2C11%0A05%2F31%2F2020%2C81%2C26%2C11%0A06%2F01%2F2020%2C253%2C37%2C10%0A06%2F02%2F2020%2C200%2C31%2C6%0A06%2F03%2F2020%2C144%2C39%2C13%0A06%2F04%2F2020%2C144%2C31%2C10%0A06%2F05%2F2020%2C133%2C20%2C6%0A06%2F06%2F2020%2C59%2C12%2C10%0A06%2F07%2F2020%2C53%2C15%2C5%0A06%2F08%2F2020%2C113%2C20%2C13%0A06%2F09%2F2020%2C131%2C18%2C7%0A06%2F10%2F2020%2C99%2C9%2C11%0A06%2F11%2F2020%2C107%2C13%2C5%0A06%2F12%2F2020%2C122%2C20%2C6%0A06%2F13%2F2020%2C52%2C9%2C4%0A06%2F14%2F2020%2C54%2C11%2C6%0A06%2F15%2F2020%2C112%2C21%2C4%0A06%2F16%2F2020%2C134%2C15%2C6%0A06%2F17%2F2020%2C107%2C10%2C7%0A06%2F18%2F2020%2C110%2C12%2C4%0A06%2F19%2F2020%2C87%2C22%2C3%0A06%2F20%2F2020%2C43%2C10%2C4%0A06%2F21%2F2020%2C53%2C12%2C6%0A06%2F22%2F2020%2C103%2C12%2C7%0A06%2F23%2F2020%2C65%2C12%2C8%0A06%2F24%2F2020%2C73%2C11%2C10%0A06%2F25%2F2020%2C54%2C6%2C4%0A06%2F26%2F2020%2C46%2C11%2C2%0A06%2F27%2F2020%2C33%2C12%2C2%0A06%2F28%2F2020%2C11%2C0%2C1%0A06%2F29%2F2020%2C2%2C0%2C0"

    manhattan = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C1%2C2%2C0%0A03%2F01%2F2020%2C0%2C0%2C0%0A03%2F02%2F2020%2C0%2C4%2C0%0A03%2F03%2F2020%2C0%2C2%2C0%0A03%2F04%2F2020%2C2%2C6%2C0%0A03%2F05%2F2020%2C0%2C6%2C0%0A03%2F06%2F2020%2C3%2C3%2C0%0A03%2F07%2F2020%2C1%2C4%2C0%0A03%2F08%2F2020%2C6%2C1%2C0%0A03%2F09%2F2020%2C25%2C12%2C0%0A03%2F10%2F2020%2C24%2C13%2C0%0A03%2F11%2F2020%2C61%2C22%2C0%0A03%2F12%2F2020%2C137%2C13%2C0%0A03%2F13%2F2020%2C182%2C31%2C0%0A03%2F14%2F2020%2C177%2C29%2C0%0A03%2F15%2F2020%2C209%2C31%2C2%0A03%2F16%2F2020%2C457%2C41%2C0%0A03%2F17%2F2020%2C566%2C61%2C0%0A03%2F18%2F2020%2C541%2C82%2C4%0A03%2F19%2F2020%2C554%2C96%2C4%0A03%2F20%2F2020%2C657%2C111%2C11%0A03%2F21%2F2020%2C402%2C116%2C5%0A03%2F22%2F2020%2C322%2C126%2C8%0A03%2F23%2F2020%2C534%2C174%2C7%0A03%2F24%2F2020%2C626%2C188%2C17%0A03%2F25%2F2020%2C594%2C185%2C20%0A03%2F26%2F2020%2C628%2C216%2C33%0A03%2F27%2F2020%2C661%2C202%2C42%0A03%2F28%2F2020%2C387%2C204%2C28%0A03%2F29%2F2020%2C408%2C160%2C35%0A03%2F30%2F2020%2C823%2C265%2C35%0A03%2F31%2F2020%2C640%2C223%2C43%0A04%2F01%2F2020%2C589%2C173%2C60%0A04%2F02%2F2020%2C655%2C229%2C62%0A04%2F03%2F2020%2C686%2C258%2C52%0A04%2F04%2F2020%2C390%2C196%2C66%0A04%2F05%2F2020%2C358%2C183%2C86%0A04%2F06%2F2020%2C719%2C262%2C70%0A04%2F07%2F2020%2C605%2C194%2C91%0A04%2F08%2F2020%2C556%2C179%2C66%0A04%2F09%2F2020%2C567%2C202%2C65%0A04%2F10%2F2020%2C504%2C196%2C68%0A04%2F11%2F2020%2C314%2C130%2C59%0A04%2F12%2F2020%2C254%2C143%2C63%0A04%2F13%2F2020%2C394%2C187%2C73%0A04%2F14%2F2020%2C443%2C162%2C59%0A04%2F15%2F2020%2C434%2C145%2C55%0A04%2F16%2F2020%2C360%2C110%2C57%0A04%2F17%2F2020%2C333%2C125%2C42%0A04%2F18%2F2020%2C188%2C89%2C57%0A04%2F19%2F2020%2C178%2C84%2C50%0A04%2F20%2F2020%2C384%2C95%2C50%0A04%2F21%2F2020%2C375%2C100%2C47%0A04%2F22%2F2020%2C388%2C111%2C38%0A04%2F23%2F2020%2C402%2C71%2C48%0A04%2F24%2F2020%2C413%2C94%2C49%0A04%2F25%2F2020%2C149%2C51%2C43%0A04%2F26%2F2020%2C98%2C51%2C34%0A04%2F27%2F2020%2C304%2C72%2C29%0A04%2F28%2F2020%2C324%2C72%2C35%0A04%2F29%2F2020%2C286%2C53%2C33%0A04%2F30%2F2020%2C218%2C43%2C34%0A05%2F01%2F2020%2C245%2C49%2C25%0A05%2F02%2F2020%2C141%2C29%2C23%0A05%2F03%2F2020%2C103%2C43%2C35%0A05%2F04%2F2020%2C215%2C55%2C19%0A05%2F05%2F2020%2C243%2C42%2C18%0A05%2F06%2F2020%2C166%2C37%2C17%0A05%2F07%2F2020%2C118%2C34%2C23%0A05%2F08%2F2020%2C100%2C41%2C13%0A05%2F09%2F2020%2C74%2C29%2C15%0A05%2F10%2F2020%2C94%2C29%2C21%0A05%2F11%2F2020%2C192%2C40%2C14%0A05%2F12%2F2020%2C163%2C30%2C14%0A05%2F13%2F2020%2C155%2C42%2C8%0A05%2F14%2F2020%2C149%2C32%2C17%0A05%2F15%2F2020%2C137%2C43%2C11%0A05%2F16%2F2020%2C56%2C18%2C10%0A05%2F17%2F2020%2C50%2C19%2C11%0A05%2F18%2F2020%2C133%2C31%2C10%0A05%2F19%2F2020%2C168%2C39%2C10%0A05%2F20%2F2020%2C165%2C25%2C12%0A05%2F21%2F2020%2C146%2C26%2C6%0A05%2F22%2F2020%2C156%2C35%2C5%0A05%2F23%2F2020%2C47%2C21%2C7%0A05%2F24%2F2020%2C70%2C28%2C6%0A05%2F25%2F2020%2C71%2C26%2C12%0A05%2F26%2F2020%2C127%2C27%2C6%0A05%2F27%2F2020%2C111%2C28%2C9%0A05%2F28%2F2020%2C96%2C29%2C3%0A05%2F29%2F2020%2C79%2C30%2C5%0A05%2F30%2F2020%2C39%2C12%2C12%0A05%2F31%2F2020%2C24%2C14%2C5%0A06%2F01%2F2020%2C82%2C23%2C3%0A06%2F02%2F2020%2C72%2C25%2C9%0A06%2F03%2F2020%2C78%2C25%2C7%0A06%2F04%2F2020%2C89%2C15%2C7%0A06%2F05%2F2020%2C61%2C10%2C7%0A06%2F06%2F2020%2C31%2C8%2C2%0A06%2F07%2F2020%2C23%2C6%2C1%0A06%2F08%2F2020%2C73%2C7%2C2%0A06%2F09%2F2020%2C68%2C7%2C8%0A06%2F10%2F2020%2C68%2C8%2C2%0A06%2F11%2F2020%2C61%2C4%2C2%0A06%2F12%2F2020%2C63%2C7%2C3%0A06%2F13%2F2020%2C24%2C3%2C2%0A06%2F14%2F2020%2C29%2C4%2C2%0A06%2F15%2F2020%2C61%2C5%2C3%0A06%2F16%2F2020%2C68%2C5%2C3%0A06%2F17%2F2020%2C68%2C5%2C3%0A06%2F18%2F2020%2C57%2C5%2C4%0A06%2F19%2F2020%2C56%2C5%2C4%0A06%2F20%2F2020%2C43%2C5%2C2%0A06%2F21%2F2020%2C24%2C3%2C4%0A06%2F22%2F2020%2C59%2C5%2C5%0A06%2F23%2F2020%2C55%2C2%2C5%0A06%2F24%2F2020%2C52%2C4%2C3%0A06%2F25%2F2020%2C30%2C4%2C3%0A06%2F26%2F2020%2C25%2C2%2C3%0A06%2F27%2F2020%2C7%2C2%2C1%0A06%2F28%2F2020%2C7%2C0%2C0%0A06%2F29%2F2020%2C0%2C0%2C0"

    queens = 'data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C2%2C0%0A03%2F01%2F2020%2C0%2C2%2C0%0A03%2F02%2F2020%2C0%2C5%2C0%0A03%2F03%2F2020%2C1%2C5%2C0%0A03%2F04%2F2020%2C2%2C3%2C0%0A03%2F05%2F2020%2C0%2C6%2C0%0A03%2F06%2F2020%2C1%2C5%2C0%0A03%2F07%2F2020%2C3%2C3%2C0%0A03%2F08%2F2020%2C5%2C5%2C0%0A03%2F09%2F2020%2C10%2C8%2C0%0A03%2F10%2F2020%2C24%2C23%2C0%0A03%2F11%2F2020%2C40%2C30%2C1%0A03%2F12%2F2020%2C80%2C28%2C0%0A03%2F13%2F2020%2C166%2C49%2C0%0A03%2F14%2F2020%2C194%2C58%2C1%0A03%2F15%2F2020%2C230%2C65%2C1%0A03%2F16%2F2020%2C530%2C106%2C4%0A03%2F17%2F2020%2C650%2C111%2C3%0A03%2F18%2F2020%2C832%2C152%2C10%0A03%2F19%2F2020%2C1065%2C160%2C6%0A03%2F20%2F2020%2C1184%2C223%2C9%0A03%2F21%2F2020%2C946%2C224%2C14%0A03%2F22%2F2020%2C695%2C223%2C14%0A03%2F23%2F2020%2C1189%2C333%2C28%0A03%2F24%2F2020%2C1390%2C362%2C35%0A03%2F25%2F2020%2C1573%2C399%2C32%0A03%2F26%2F2020%2C1642%2C426%2C60%0A03%2F27%2F2020%2C1575%2C412%2C58%0A03%2F28%2F2020%2C1202%2C434%2C92%0A03%2F29%2F2020%2C1075%2C453%2C94%0A03%2F30%2F2020%2C1841%2C549%2C99%0A03%2F31%2F2020%2C1791%2C553%2C96%0A04%2F01%2F2020%2C1767%2C526%2C142%0A04%2F02%2F2020%2C1814%2C562%2C140%0A04%2F03%2F2020%2C1754%2C518%2C159%0A04%2F04%2F2020%2C1200%2C468%2C156%0A04%2F05%2F2020%2C1136%2C388%2C182%0A04%2F06%2F2020%2C1913%2C529%2C201%0A04%2F07%2F2020%2C1943%2C522%2C185%0A04%2F08%2F2020%2C1846%2C509%2C183%0A04%2F09%2F2020%2C1557%2C455%2C173%0A04%2F10%2F2020%2C1325%2C444%2C156%0A04%2F11%2F2020%2C981%2C352%2C164%0A04%2F12%2F2020%2C920%2C309%2C174%0A04%2F13%2F2020%2C974%2C350%2C192%0A04%2F14%2F2020%2C1300%2C382%2C163%0A04%2F15%2F2020%2C1177%2C301%2C152%0A04%2F16%2F2020%2C1139%2C287%2C131%0A04%2F17%2F2020%2C1097%2C284%2C122%0A04%2F18%2F2020%2C704%2C212%2C136%0A04%2F19%2F2020%2C867%2C187%2C136%0A04%2F20%2F2020%2C1219%2C221%2C126%0A04%2F21%2F2020%2C933%2C210%2C103%0A04%2F22%2F2020%2C1109%2C177%2C86%0A04%2F23%2F2020%2C787%2C152%2C106%0A04%2F24%2F2020%2C774%2C165%2C97%0A04%2F25%2F2020%2C540%2C117%2C80%0A04%2F26%2F2020%2C332%2C126%2C90%0A04%2F27%2F2020%2C721%2C122%2C91%0A04%2F28%2F2020%2C893%2C119%2C72%0A04%2F29%2F2020%2C692%2C118%2C81%0A04%2F30%2F2020%2C592%2C112%2C66%0A05%2F01%2F2020%2C620%2C108%2C76%0A05%2F02%2F2020%2C333%2C88%2C61%0A05%2F03%2F2020%2C248%2C79%2C56%0A05%2F04%2F2020%2C432%2C82%2C55%0A05%2F05%2F2020%2C462%2C66%2C45%0A05%2F06%2F2020%2C443%2C66%2C58%0A05%2F07%2F2020%2C356%2C65%2C41%0A05%2F08%2F2020%2C343%2C53%2C48%0A05%2F09%2F2020%2C256%2C42%2C33%0A05%2F10%2F2020%2C85%2C38%2C35%0A05%2F11%2F2020%2C376%2C71%2C27%0A05%2F12%2F2020%2C314%2C53%2C18%0A05%2F13%2F2020%2C304%2C51%2C30%0A05%2F14%2F2020%2C333%2C63%2C23%0A05%2F15%2F2020%2C265%2C64%2C27%0A05%2F16%2F2020%2C135%2C60%2C21%0A05%2F17%2F2020%2C107%2C37%2C26%0A05%2F18%2F2020%2C273%2C49%2C20%0A05%2F19%2F2020%2C288%2C49%2C12%0A05%2F20%2F2020%2C247%2C45%2C26%0A05%2F21%2F2020%2C307%2C38%2C9%0A05%2F22%2F2020%2C227%2C51%2C28%0A05%2F23%2F2020%2C130%2C44%2C14%0A05%2F24%2F2020%2C118%2C28%2C13%0A05%2F25%2F2020%2C106%2C46%2C12%0A05%2F26%2F2020%2C261%2C45%2C9%0A05%2F27%2F2020%2C164%2C53%2C18%0A05%2F28%2F2020%2C174%2C33%2C9%0A05%2F29%2F2020%2C209%2C46%2C14%0A05%2F30%2F2020%2C107%2C24%2C17%0A05%2F31%2F2020%2C69%2C31%2C15%0A06%2F01%2F2020%2C139%2C35%2C15%0A06%2F02%2F2020%2C160%2C37%2C15%0A06%2F03%2F2020%2C147%2C26%2C9%0A06%2F04%2F2020%2C137%2C15%2C11%0A06%2F05%2F2020%2C104%2C17%2C5%0A06%2F06%2F2020%2C98%2C9%2C11%0A06%2F07%2F2020%2C74%2C6%2C10%0A06%2F08%2F2020%2C143%2C15%2C14%0A06%2F09%2F2020%2C127%2C8%2C9%0A06%2F10%2F2020%2C111%2C11%2C8%0A06%2F11%2F2020%2C110%2C9%2C7%0A06%2F12%2F2020%2C126%2C11%2C9%0A06%2F13%2F2020%2C73%2C7%2C1%0A06%2F14%2F2020%2C68%2C13%2C6%0A06%2F15%2F2020%2C118%2C11%2C6%0A06%2F16%2F2020%2C120%2C16%2C7%0A06%2F17%2F2020%2C89%2C13%2C8%0A06%2F18%2F2020%2C116%2C14%2C6%0A06%2F19%2F2020%2C117%2C3%2C5%0A06%2F20%2F2020%2C57%2C5%2C5%0A06%2F21%2F2020%2C55%2C7%2C11%0A06%2F22%2F2020%2C113%2C8%2C8%0A06%2F23%2F2020%2C95%2C9%2C5%0A06%2F24%2F2020%2C69%2C12%2C7%0A06%2F25%2F2020%2C40%2C9%2C3%0A06%2F26%2F2020%2C37%2C3%2C2%0A06%2F27%2F2020%2C18%2C2%2C1%0A06%2F28%2F2020%2C10%2C0%2C0%0A06%2F29%2F2020%2C3%2C0%2C0'

    staten_island = "data:application/octet-stream;charset=utf-8,DATE_OF_INTEREST%2CCases%2CHospitalizations%2CDeaths%0A02%2F29%2F2020%2C0%2C0%2C0%0A03%2F01%2F2020%2C0%2C1%2C0%0A03%2F02%2F2020%2C0%2C0%2C0%0A03%2F03%2F2020%2C0%2C1%2C0%0A03%2F04%2F2020%2C0%2C2%2C0%0A03%2F05%2F2020%2C0%2C1%2C0%0A03%2F06%2F2020%2C1%2C2%2C0%0A03%2F07%2F2020%2C1%2C0%2C0%0A03%2F08%2F2020%2C1%2C0%2C0%0A03%2F09%2F2020%2C3%2C3%2C0%0A03%2F10%2F2020%2C2%2C5%2C0%0A03%2F11%2F2020%2C3%2C3%2C0%0A03%2F12%2F2020%2C13%2C5%2C0%0A03%2F13%2F2020%2C26%2C3%2C0%0A03%2F14%2F2020%2C23%2C8%2C0%0A03%2F15%2F2020%2C46%2C16%2C1%0A03%2F16%2F2020%2C91%2C17%2C0%0A03%2F17%2F2020%2C108%2C21%2C0%0A03%2F18%2F2020%2C150%2C24%2C0%0A03%2F19%2F2020%2C258%2C32%2C4%0A03%2F20%2F2020%2C309%2C30%2C3%0A03%2F21%2F2020%2C248%2C35%2C1%0A03%2F22%2F2020%2C317%2C32%2C6%0A03%2F23%2F2020%2C209%2C46%2C8%0A03%2F24%2F2020%2C349%2C48%2C6%0A03%2F25%2F2020%2C394%2C49%2C4%0A03%2F26%2F2020%2C403%2C47%2C10%0A03%2F27%2F2020%2C370%2C57%2C7%0A03%2F28%2F2020%2C266%2C53%2C13%0A03%2F29%2F2020%2C230%2C57%2C17%0A03%2F30%2F2020%2C397%2C68%2C11%0A03%2F31%2F2020%2C234%2C69%2C21%0A04%2F01%2F2020%2C263%2C74%2C16%0A04%2F02%2F2020%2C370%2C79%2C30%0A04%2F03%2F2020%2C344%2C64%2C29%0A04%2F04%2F2020%2C347%2C51%2C20%0A04%2F05%2F2020%2C323%2C65%2C22%0A04%2F06%2F2020%2C730%2C81%2C24%0A04%2F07%2F2020%2C629%2C70%2C29%0A04%2F08%2F2020%2C561%2C57%2C34%0A04%2F09%2F2020%2C297%2C56%2C25%0A04%2F10%2F2020%2C300%2C54%2C19%0A04%2F11%2F2020%2C312%2C49%2C28%0A04%2F12%2F2020%2C252%2C45%2C26%0A04%2F13%2F2020%2C185%2C56%2C25%0A04%2F14%2F2020%2C290%2C52%2C24%0A04%2F15%2F2020%2C317%2C33%2C24%0A04%2F16%2F2020%2C210%2C38%2C14%0A04%2F17%2F2020%2C280%2C38%2C15%0A04%2F18%2F2020%2C153%2C25%2C19%0A04%2F19%2F2020%2C134%2C31%2C19%0A04%2F20%2F2020%2C224%2C29%2C16%0A04%2F21%2F2020%2C216%2C27%2C11%0A04%2F22%2F2020%2C173%2C20%2C14%0A04%2F23%2F2020%2C128%2C19%2C13%0A04%2F24%2F2020%2C143%2C34%2C14%0A04%2F25%2F2020%2C88%2C26%2C9%0A04%2F26%2F2020%2C46%2C23%2C7%0A04%2F27%2F2020%2C107%2C20%2C9%0A04%2F28%2F2020%2C129%2C19%2C8%0A04%2F29%2F2020%2C124%2C19%2C14%0A04%2F30%2F2020%2C130%2C19%2C11%0A05%2F01%2F2020%2C77%2C12%2C8%0A05%2F02%2F2020%2C60%2C18%2C12%0A05%2F03%2F2020%2C35%2C15%2C15%0A05%2F04%2F2020%2C90%2C15%2C8%0A05%2F05%2F2020%2C78%2C12%2C12%0A05%2F06%2F2020%2C60%2C7%2C8%0A05%2F07%2F2020%2C60%2C7%2C4%0A05%2F08%2F2020%2C42%2C10%2C5%0A05%2F09%2F2020%2C32%2C7%2C3%0A05%2F10%2F2020%2C14%2C5%2C8%0A05%2F11%2F2020%2C27%2C4%2C3%0A05%2F12%2F2020%2C53%2C8%2C6%0A05%2F13%2F2020%2C48%2C9%2C6%0A05%2F14%2F2020%2C42%2C13%2C6%0A05%2F15%2F2020%2C33%2C7%2C6%0A05%2F16%2F2020%2C25%2C9%2C2%0A05%2F17%2F2020%2C10%2C4%2C2%0A05%2F18%2F2020%2C38%2C4%2C2%0A05%2F19%2F2020%2C42%2C8%2C5%0A05%2F20%2F2020%2C57%2C6%2C7%0A05%2F21%2F2020%2C77%2C10%2C3%0A05%2F22%2F2020%2C32%2C7%2C5%0A05%2F23%2F2020%2C37%2C6%2C2%0A05%2F24%2F2020%2C14%2C4%2C5%0A05%2F25%2F2020%2C17%2C5%2C3%0A05%2F26%2F2020%2C56%2C3%2C1%0A05%2F27%2F2020%2C44%2C3%2C2%0A05%2F28%2F2020%2C26%2C8%2C1%0A05%2F29%2F2020%2C26%2C9%2C2%0A05%2F30%2F2020%2C15%2C3%2C1%0A05%2F31%2F2020%2C11%2C2%2C2%0A06%2F01%2F2020%2C39%2C2%2C3%0A06%2F02%2F2020%2C33%2C6%2C1%0A06%2F03%2F2020%2C42%2C5%2C3%0A06%2F04%2F2020%2C28%2C1%2C2%0A06%2F05%2F2020%2C9%2C1%2C1%0A06%2F06%2F2020%2C7%2C0%2C0%0A06%2F07%2F2020%2C4%2C0%2C1%0A06%2F08%2F2020%2C16%2C2%2C0%0A06%2F09%2F2020%2C19%2C1%2C2%0A06%2F10%2F2020%2C13%2C2%2C2%0A06%2F11%2F2020%2C15%2C0%2C1%0A06%2F12%2F2020%2C18%2C1%2C0%0A06%2F13%2F2020%2C1%2C1%2C1%0A06%2F14%2F2020%2C4%2C0%2C2%0A06%2F15%2F2020%2C17%2C0%2C2%0A06%2F16%2F2020%2C20%2C0%2C0%0A06%2F17%2F2020%2C16%2C0%2C0%0A06%2F18%2F2020%2C23%2C0%2C1%0A06%2F19%2F2020%2C7%2C0%2C2%0A06%2F20%2F2020%2C5%2C0%2C2%0A06%2F21%2F2020%2C9%2C2%2C2%0A06%2F22%2F2020%2C17%2C2%2C3%0A06%2F23%2F2020%2C13%2C1%2C0%0A06%2F24%2F2020%2C5%2C0%2C1%0A06%2F25%2F2020%2C17%2C1%2C1%0A06%2F26%2F2020%2C7%2C1%2C1%0A06%2F27%2F2020%2C3%2C1%2C0%0A06%2F28%2F2020%2C1%2C0%2C0%0A06%2F29%2F2020%2C0%2C0%2C0"

    nyFIPS = {"bronx" : "36005", "brooklyn": "36047", "manhattan":"36061", "queens":"36081", "staten_island":"36085"}

    def read_NYC_county(county_link, fips):
        with urlopen(county_link) as response:
            data = response.read().decode("utf8")
            df = pd.read_csv(io.StringIO(data))
            df.insert(0,"FIPS", [nyFIPS[fips]]*len(df))
            df = df.drop(['Hospitalizations','Deaths'], axis=1)
            df = df.rename({'DATE_OF_INTEREST':'date', 'Cases':'confirmed_cases'}, axis=1)
            df['date'] = pd.to_datetime(df['date'])
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
    jhu_data['date'] = pd.to_datetime(jhu_data['date'])
    jhu_data = jhu_data.sort_values(['FIPS', 'date'])

    # Case counts are cumulative and will be converted into daily change
    jhu_data['confirmed_cases'] = jhu_data.groupby('FIPS')['confirmed_cases'].diff().dropna()

    # Merge Johns Hopkins Data with NYC data
    ny_fips_list = ["36005","36047","36061", "36081", "36085"]
    jhu_data = jhu_data[~jhu_data['FIPS'].isin(ny_fips_list)]
    full_data = pd.concat([jhu_data, bronx, brooklyn, manhattan, queens, staten_island])

    full_data = full_data.sort_values(['FIPS','date'], axis=0)
    full_data = full_data.reset_index(drop=True)

    # Compute 7-day (weekly) rolling average of cases for each county
    full_data['confirmed_cases'] = pd.Series(full_data.groupby("FIPS")['confirmed_cases'].rolling(14).mean()).reset_index(drop=True)
    full_data = full_data[full_data['confirmed_cases'].notnull()]

    # Move dates forward by 1 day so that movement averages represent data from past week
    full_data['date'] = pd.to_datetime(full_data['date'])
    full_data['date'] = full_data['date'].apply(pd.DateOffset(1))

    # Normalize confirmed cases for population and export to csv
    census_data = preprocess_census(drop_tot = False, use_reduced=True)[['TOT_POP', 'FIPS']].reset_index(drop=True)

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

    merged_df = merged_df.sort_values(['FIPS', 'state'])
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
    testing['positiveIncrease'] = pd.Series(testing.groupby("state")['positiveIncrease'].rolling(14).mean()).reset_index(drop=True)
    testing['totalTestResultsIncrease'] = pd.Series(testing.groupby("state")['totalTestResultsIncrease'].rolling(14).mean()).reset_index(drop=True)

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
    testing_pop['test_positivity'] = testing_pop['positiveIncrease'] / testing_pop['totalTestResultsIncrease']
    #testing_pop = testing_pop.drop(['positiveIncrease', 'totalTestResultsIncrease'], axis=1)

    # Get dataframe of all dates mapped to all FIPS from the Rt data
    fips_df = pd.read_csv("data/rt_data.csv", dtype={'FIPS':str,'state':str}, usecols=['FIPS','date','state'])

    merged_df = pd.merge(left=fips_df, right=testing_pop, how='left', on=['state', 'date'], copy=False)
    merged_df = merged_df.drop(['state'], axis=1)

    merged_df.to_csv("data/testing_data.csv", sep=',', index=False)

    return merged_df

def merge_data(save_files = False, ag=False):
    pd.options.mode.chained_assignment = None

    print("[ ] Preprocess Census and Health Data", end='\r')
    census = preprocess_census(use_reduced=True)
    disparities = preprocess_disparities()
    health = merge_health_data()
    smoking = preprocess_smoking_prevalence()
    print('[' + u'\u2713' + ']\n')


    print("[ ] Reading Google and Apple Mobility Data", end='\r')
    other_mobility_path = get_latest_file('14-days-mobility')
    google_apple_mobility = pd.read_csv(other_mobility_path)
    google_apple_mobility = google_apple_mobility.rename(columns={'fips':'FIPS'})
    saving_path = 'processed_data/merged/' + date.today().isoformat() + '.csv.gz'
    print('[' + u'\u2713' + ']\n')

    print('[ ] Get Facebook Mobility Data', end='\r')
    status = get_facebook_data()
    if status == 'success':
        print('[' + u'\u2713' + ']\n')
    else:
        print('[' + u'\u2718' + ']\n')
        print('\n Facebook Mobility Data could not be found\n')

    print("[ ] Preprocess Facebook Mobility Data", end='\r')
    mobility = preprocess_facebook()
    print('[' + u'\u2713' + ']\n')

    print("[ ] Update JHU Data", end='\r')
    cases = preprocess_JHU()
    print('[' + u'\u2713' + ']\n')

    print("[ ] Update Rt Data", end='\r')
    rt = preprocess_Rt()
    print('[' + u'\u2713' + ']\n')

    print("[ ] Update Testing Data", end='\r')
    testing = preprocess_testing()
    print('[' + u'\u2713' + ']\n')

    print("[ ] Process and export data", end='\r')

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
    if ag: # do not delete
        merged_DF = pd.merge(left=merged_DF, right=google_apple_mobility, how='left', on=['FIPS', 'date'], copy=False).sort_values(['FIPS', 'date']).reset_index(drop=True)

    locations = merged_DF['Location']
    merged_DF = merged_DF.drop('Location', axis=1)
    merged_DF.insert(0, 'Location', locations)

    if ag: # do not delete
        apple_google_df = merged_DF.dropna() # do not delete
        merged_DF = merged_DF.drop(['google_mobility_14d', 'apple_mobility_14d'], 1) # do not delete

    columns = merged_DF.columns.tolist()
    columns.remove('fb_stationary')
    columns.remove('fb_movement_change')

    cleaned_DF = merged_DF.dropna(subset=columns)
    unused_DF = merged_DF[~merged_DF.index.isin(cleaned_DF.index)]
    training_mobility = cleaned_DF.dropna()
    training_mobility = training_mobility.sort_values(['FIPS', 'date'])
    #maxes = training_mobility.groupby('FIPS')['date'].transform(max)
    #latest_mobility = training_mobility.loc[training_mobility['date'] == maxes]
    #latest_mobility = training_mobility.groupby('FIPS', as_index=False).nth([-27, -20, -13, -7, -1])
    no_mobility = cleaned_DF[~cleaned_DF.index.isin(training_mobility.index)]
    no_mobility = no_mobility.drop(['fb_stationary', 'fb_movement_change'], axis=1)
    no_mobility = no_mobility.sort_values(['FIPS', 'date'])
    #maxes = no_mobility.groupby('FIPS')['date'].transform(max)
    #latest_no_mobility = no_mobility.loc[no_mobility['date'] == maxes]
    #latest_no_mobility = no_mobility.groupby('FIPS', as_index=False).nth([-27, -20, -13, -7, -1])
    training_no_mobility = cleaned_DF.drop(['fb_stationary', 'fb_movement_change'], axis=1)

    if save_files == True:
        if ag:
            apple_google_df.to_csv(saving_path, compression='gzip', index=False) # DO NOT DELETE
        if not ag:
            unused_DF.to_csv(os.path.split(os.getcwd())[0] + "/unused_data.csv.gz", index=False, compression='gzip')
            training_mobility.to_csv(os.path.split(os.getcwd())[0] + "/training_mobility.csv.gz", index=False, compression='gzip')
            #latest_mobility.to_csv(os.path.split(os.getcwd())[0] + "/latest_mobility.csv.gz", index=False, compression='gzip')
            #latest_no_mobility.to_csv(os.path.split(os.getcwd())[0] + "/latest_no_mobility.csv.gz", index=False, compression='gzip')
            training_no_mobility.to_csv(os.path.split(os.getcwd())[0] + "/training_no_mobility.csv.gz", index=False, compression='gzip')

    print('[' + u'\u2713' + ']\n')

    pd.options.mode.chained_assignment = 'warn' # return to default

    return training_mobility, training_no_mobility

if __name__ == '__main__':
    merge_data(save_files=True)
