"""
This module preprocesses Apple Mobility Data.

Data source: https://www.apple.com/covid19/mobility
"""

import os, sys
import numpy as np
import pandas as pd
from datetime import datetime, date
import csv
import ast
import shutil
import requests
import json
from zipfile import ZipFile
from bs4 import BeautifulSoup

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'

# DOWNLOAD
def apple_url_health():
    json_url = \
        'https://covid19-static.cdn-apple.com/covid19-mobility-data/current/v3/index.json'
    url_health = requests.get(json_url).status_code
    if url_health == requests.codes.ok:
        return True
    else:
        return False

def get_apple_data():
    json_url = \
        'https://covid19-static.cdn-apple.com/covid19-mobility-data/current/v3/index.json'
    content = requests.get(json_url).text
    js = json.loads(content)
    url = 'https://covid19-static.cdn-apple.com' + js['basePath'] + \
        js['regions']['en-us']['csvPath']
    apple_df = pd.read_csv(url, low_memory=False)
    return apple_df


# PROCESS
def apple_mobility_to_pd(df_load):
    with open('data/geodata/state_abbr.txt', 'r') as f:
        contents = f.read()
        state_abbr_dict = ast.literal_eval(contents)

    # Keep only rows that belong to some 'county'
    df_apple = df_load.loc[df_load['geo_type'] == 'county']

    # Keep only rows that represent 'driving'
    df_apple = df_apple.loc[df_apple['transportation_type'] == 'driving']
    df_apple = df_apple.drop(['alternative_name', 'country', 'geo_type'], 1)
    df_apple['sub-region'] = df_apple['sub-region'].replace(state_abbr_dict)

    # Correct some non-Eng county names
    df_apple['region'] = df_apple['region'].str.replace('Bayamón', 'Bayamon')
    df_apple['region'] = df_apple['region'].str.replace('Doña', 'Dona')
    df_apple['region'] = df_apple['region'].str.replace('Mayagüez', 'Mayaguez')
    df_apple['region'] = df_apple['region'].str.replace('Río', 'Rio')
    df_apple['fips'] = df_apple['region'] + ' ' + df_apple['sub-region']

    # Preprocess Census Bureau FIPS list
    df_fips = pd.read_csv('data/geodata/county_fips_2017_06.csv',\
                            header=0,\
                            low_memory=False,\
                            usecols=['COUNTYNAME', 'STATE', 'STCOUNTYFP'])
    df_fips['COUNTYNAME'] = df_fips['COUNTYNAME'].str.replace('city', 'City')
    df_fips['id'] = df_fips['COUNTYNAME'] + ' ' + df_fips['STATE']
    df_fips = df_fips.drop_duplicates(subset=['id'])
    fips_dict = pd.Series(df_fips['STCOUNTYFP'].values, index=df_fips['id']).to_dict()

    # Get FIPS column for Apple dataset
    df_apple['fips'] = df_apple['fips'].replace(fips_dict)
    df_apple = df_apple.drop(['region', 'transportation_type', 'sub-region'], 1)
    df_apple = df_apple.melt(id_vars=['fips'], \
                            var_name='date', \
                            value_name='apple_mobility')
    df_apple = df_apple.sort_values(['fips', 'date'])
    df_apple = df_apple.reset_index(drop=True)
    df_apple = df_apple.interpolate()

    # Compute 14 day rolling averages for movement data
    df_apple['apple_mobility'] = pd.Series(df_apple.groupby('fips')['apple_mobility'].rolling(14).mean()).reset_index(drop=True)

    # Move dates forward by 1 day so that movement averages represent data from past week
    df_apple['date'] = pd.to_datetime(df_apple['date'])
    df_apple['date'] = df_apple['date'].apply(pd.DateOffset(1))
    df_apple['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df_apple = df_apple.dropna()
    df_apple = df_apple.rename(columns={'fips': 'FIPS'})

    df_apple.to_csv('data/apple/mobility.csv.gz',\
                    compression='gzip',\
                    index=False)

def preprocess_apple():
    print('• Processing Apple Mobility Data')
    status = apple_url_health()
    if status:
        df = get_apple_data()
        apple_mobility_to_pd(df)
        print('  Finished\n')
    else:
        print('  Error - Apple Mobility Data could not be found from server\n')

if __name__ == "__main__":
    preprocess_apple()
