"""
This module preprocesses Google Mobility Data.

Data source: https://www.google.com/covid19/mobility/
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
__version__ = '2.0.0'
__status__ = 'beta'
__url__ = 'https://github.com/solveforj/pandemic-central'

# DOWNLOAD
def google_url_health():
    download_url = \
        'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'
    url_health = requests.get(download_url).status_code
    if url_health == requests.codes.ok:
        return True
    else:
        return False

def get_google_data():
    url = \
        'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'
    google_df = pd.read_csv(url, low_memory=False)
    return google_df

# PROCESS
def google_mobility_to_pd(df_load):
    path = 'data/google/mobility.csv.gz'
    drop_list = ['country_region_code', 'country_region', 'sub_region_1', \
        'sub_region_2', 'iso_3166_2_code', 'metro_area']
    df_load = df_load.drop(drop_list, 1)

    # Drop rows that do not represent county properly
    df_google = df_load.dropna(subset=['census_fips_code'])
    df_google = df_google.rename(columns={'census_fips_code': 'fips'})

    cols = ['retail_and_recreation_percent_change_from_baseline',\
            'grocery_and_pharmacy_percent_change_from_baseline',\
            'parks_percent_change_from_baseline',\
            'transit_stations_percent_change_from_baseline',\
            'workplaces_percent_change_from_baseline',\
            'residential_percent_change_from_baseline']

    # Take the average of the categories as a new column
    df_google['google_mobility'] = df_google[cols].mean(axis=1, skipna=True)
    df_google = df_google.drop(cols, 1) # drop all the unnecessary columns
    df_google = df_google.astype({'fips': 'float'})
    df_google = df_google.astype({'fips': 'int32'})
    df_google = df_google.reset_index(drop=True)

    # Compute 14 day rolling averages for movement data
    df_google['google_mobility'] = pd.Series(df_google.groupby('fips')['google_mobility'].rolling(14).mean()).reset_index(drop=True)

    # Move dates forward by 1 day so that movement averages represent data from past week
    df_google['date'] = pd.to_datetime(df_google['date'])
    df_google['date'] = df_google['date'].apply(pd.DateOffset(1))
    df_google['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df_google = df_google.dropna()

    df_google.to_csv(path, compression='gzip', index=False)

def main():
    print('•  Processing Google Mobility Data')
    status = google_url_health()
    if status:
        df = get_google_data()
        google_mobility_to_pd(df)
        print('  Finished\n')
    else:
        print('  Error - Google Mobility Data could not be found from server\n')
