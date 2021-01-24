"""
This module preprocesses Facebook Mobility Data.

Data source: https://data.humdata.org/dataset/movement-range-maps
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
def get_facebook_data():
    url = 'https://data.humdata.org/dataset/movement-range-maps'
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')
    download_url = soup.find_all('a',\
        {"class": "btn btn-empty btn-empty-blue hdx-btn resource-url-analytics ga-download"},\
         href=True)[1]['href']
    download_url = 'https://data.humdata.org' + download_url
    zip = requests.get(download_url)
    os.mkdir('temp')
    temp_path = ('temp/data.zip')
    with open(temp_path, 'wb') as temp:
        temp.write(zip.content)
    with ZipFile(temp_path, 'r') as unzip:
        unzip.extractall('temp/')
    files = os.listdir('temp')

    return files


# PROCESS
def facebook_mobility_to_pd(files):
    for filename in files:
        if filename.startswith('movement-range'):
            path = 'temp/' + filename

    # Read and compress data file
    df_load = pd.read_csv(path, sep='\t', dtype={'polygon_id':str})
    df_load = df_load[df_load['country'] == 'USA']
    df = df_load[['ds', 'polygon_id', 'all_day_bing_tiles_visited_relative_change', 'all_day_ratio_single_tile_users']]
    df = df.rename({'polygon_id':'FIPS','ds':'date','all_day_bing_tiles_visited_relative_change':'fb_movement_change', 'all_day_ratio_single_tile_users':'fb_stationary'}, axis=1)
    df = df.reset_index(drop=True)

    # Compute 14 day rolling averages for movement data
    df['fb_movement_change'] = pd.Series(df.groupby("FIPS")['fb_movement_change'].rolling(7).mean()).reset_index(drop=True)
    df['fb_stationary'] = pd.Series(df.groupby("FIPS")['fb_stationary'].rolling(7).mean()).reset_index(drop=True)

    # Move dates forward by 1 day so that movement averages represent data from past week
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'] + pd.Timedelta(value=1, unit='day')
    df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df = df.dropna()

    final = 'data/facebook/mobility.csv.gz'
    df.to_csv(final, compression='gzip', index=False)

    for filename in files:
        os.remove('temp/' + filename)
    os.rmdir('temp/')

def facebook_mobility_state_level():
    print('• Processing Facebook Mobility Data - State Level')
    # Download files
    files = get_facebook_data()
    for filename in files:
        if filename.startswith('movement-range'):
            path = 'temp/' + filename

    # Read latest Facebook data
    df_load = pd.read_csv(path, sep='\t', dtype={'polygon_id':str}, usecols=list(range(0,6)))
    df_load = df_load[df_load['country'] == 'USA']
    df_load = df_load.drop(['country'], 1)
    df_load = df_load.rename(columns={'polygon_id':'fips','ds':'date','all_day_bing_tiles_visited_relative_change':'fb_movement_change'})

    # Get county population data
    df_fips = pd.read_csv('data/geodata/county_fips_2017_06.csv',\
                        usecols=['STATE', 'STCOUNTYFP'], dtype='str')
    df_fips = df_fips.rename(columns={'STATE':'state', 'STCOUNTYFP':'fips'})
    df_load = df_load.merge(df_fips, on='fips', how='inner')

    # Get state population data
    df_population = pd.read_csv('data/census/Reichlab_Population.csv',
                                usecols=['abbreviation', 'location', 'population'],
                                dtype={'location':'str'})
    df_state = df_population.drop(['location'],1)
    df_state = df_state.dropna(subset=['abbreviation'])
    df_state = df_state.rename(columns={'abbreviation':'state', \
                                                'population':'state_pop'})
    df_county = df_population[df_population['abbreviation'].isnull()]
    df_county = df_county.drop(['abbreviation'],1)
    df_county = df_county.rename(columns={'location':'fips', \
                                                'population':'county_pop'})

    # Merge population data into DataFrame
    df_load = df_load.merge(df_state, on='state', how='inner')
    df_load = df_load.merge(df_county, on='fips', how='inner')

    # Take weighed average
    df_load['fb_movement_change'] = df_load['fb_movement_change']*(df_load['county_pop']/df_load['state_pop'])
    df_load = df_load.drop(['fips', 'polygon_source', 'state_pop', 'county_pop', 'polygon_name'], 1)
    df_load = df_load.groupby(['state', 'date']).sum().reset_index().sort_values(by=['state', 'date'])

    for filename in files:
        os.remove('temp/' + filename)
    os.rmdir('temp/')

    df_load.to_csv('data/facebook/state_mobility.csv', index=False)

    print('  Finished\n')

def preprocess_facebook():
    print('• Processing Facebook Mobility Data - County Level')
    files = get_facebook_data()
    facebook_mobility_to_pd(files)
    print('  Finished\n')

if __name__ == "__main__":
    preprocess_facebook()
