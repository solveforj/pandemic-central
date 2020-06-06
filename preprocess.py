"""
This module preprocesses raw datasets into usable Pandas df before merging into
final dataset.
Notice that at early developing stage, we are only focusing on US counties.
"""

import os, sys
import numpy as np
import pandas as pd
from datetime import datetime, date
from jhu_rename import rename_em
import csv
import ast

def get_latest_file(src, dir='raw_data/'): # get the directory of the lastest file
    if src == 'apple':
        files = os.listdir(dir + src)
        new_files = []
        for file in files:
            new_file = file.replace('applemobilitytrends', '')
            new_file = new_file.replace('-', '')
            new_file = new_file.replace('.csv', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = 'applemobilitytrends-' + max_[:4] + '-' + max_[4:6] + \
            '-' + max_[6:] + '.csv'
        path = dir + src + '/' + lastest_file

    if src == 'jhu':
        files = os.listdir(dir + src + '/county_renamed')
        new_files = []
        for file in files:
            new_file = file.replace('-', '')
            new_file = new_file.replace('.csv', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + '.csv'
        path = dir + src + '/county_renamed/' + lastest_file

    if src == 'kaggle':
        files = os.listdir(dir + src + '/county')
        new_files = []
        for file in files:
            new_file = file.replace('county-', '')
            new_file = new_file.replace('.csv', '')
            new_file = new_file.replace('-', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = 'county-' + max_[:4] + '-' + max_[4:6] + \
            '-' + max_[6:] + '.csv'
        path = dir + src + '/county/' + lastest_file

    if src == 'google':
        files = os.listdir(dir + src)
        new_files = []
        for file in files:
            new_file = file.replace('-', '')
            new_file = new_file.replace('.csv', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + '.csv'
        path = dir + src + '/' + lastest_file

    if src == 'unacast':
        files = os.listdir(dir + src + '/county')
        new_files = []
        for file in files:
            new_file = file.replace('COVID-', '')
            new_file = new_file.replace('-sds-v3-full-county.csv', '')
            new_file = new_file.replace('-', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = 'COVID-' + max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + \
            '-sds-v3-full-county.csv'
        path = dir + src + '/county/' + lastest_file

    return path

def check_lastest_file(dir): # verify the lastest file with system time
    src = dir.split('/')[1]
    if src == 'apple':
        t = date.today().isoformat()
        if t == dir.split('applemobilitytrends-')[1].replace('.csv', ''):
            return True
        else:
            return False

    if src == 'kaggle':
        t = date.today().isoformat()
        if t == dir.split('county-')[1].replace('.csv', ''):
            return True
        else:
            return False

    if src == 'jhu':
        t = date.today().isoformat()
        if t == dir.replace('.csv', ''):
            return True
        else:
            return False

def get_file_on_date(src, date, dir='raw_data/'): # get the directory of the file on specified date
    if src == 'apple':
        path = dir + src + '/' + 'applemobilitytrends-' + date + '.csv'
    if src == 'unacast':
        path = dir + src + '/county/' + 'COVID_' + date + \
            '_sds-v3-full-county.csv'
    if src == 'jhu':
        path = dir + src + '/county_renamed/' + date + '.csv'
    return path

def get_fips_dict(): # Read Johns Hopkins dataset and export FIPS dictionary for county
    src = get_latest_file('jhu')
    dataset_path = get_latest_file('jhu')
    # Read Johns Hopkins lastest dataset
    df_jhu = pd.read_csv(
        dataset_path,
        header=0,
        low_memory=False,
        dtype={'FIPS': str}
    )
    df_jhu.insert(len(df_jhu.columns), 'id', df_jhu['Province_State'] + ' ' + \
        df_jhu['Admin2'])
    # Drop the rows that do not represent county properly
    df_jhu = df_jhu.dropna(subset=['FIPS', 'id'])

    dict = pd.Series(df_jhu['FIPS'].values, index=df_jhu['id']).to_dict()
    # Export dictionary of FIPS codes as text file
    if not os.path.exists('raw_data/dicts'):
        os.mkdir('raw_data/dicts')
    if os.path.exists('raw_data/dicts/fips_codes.txt'):
        os.remove('raw_data/dicts/fips_codes.txt')
    with open('raw_data/dicts/fips_codes.txt', 'w') as f:
        print(dict, file=f)

def apple_mobility_to_pd(): # process Apple Mobility Report as Pandas dataframe
    path = get_latest_file('apple')
    with open(path) as data:
        reader = csv.reader(data)
        cols = next(reader)
    _ = cols.pop(3) # filter out 'alternative_name'
    _ = cols.pop(4) # filter out 'country'
    df_load = pd.read_csv(
        path,
        header=0,
        usecols=cols # final move for filtering
    )
    # Keep only rows that belong to some 'county'
    df_apple = df_load.loc[df_load['geo_type'] == 'county']

    # Insert a new 'id' column (state name + county name)
    df_apple.insert(0, 'id', \
        df_apple['sub-region'] + ' ' + df_apple['region'] + '-',\
        allow_duplicates=False)
    pd.options.mode.chained_assignment = None
    df_apple['id'] = df_apple['id'].str.replace(' County-', '')
    df_apple['id'] = df_apple['id'].str.replace(' Borough-', '')
    df_apple['id'] = df_apple['id'].str.replace(' Parish-', '')
    # Read FIPS dictionary
    with open('raw_data/dicts/fips_codes.txt', 'r') as f:
        contents = f.read()
        fips_dict = ast.literal_eval(contents)
    df_apple['fips'] = df_apple['id'].replace(fips_dict)
    pd.options.mode.chained_assignment = 'warn' # return to default
    # Drop the all the unnecessary columns
    df_apple = df_apple.drop(['geo_type', 'region', 'sub-region', 'id'], 1)

    return df_apple

def google_mobility_to_pd(): # process Google Mobility Report
    path = get_latest_file('google')
    with open(path) as data:
        reader = csv.reader(data)
        cols = next(reader)
    _ = cols.pop(1) # filter out 'country_region'
    df_load = pd.read_csv(
        path,
        header=0,
        usecols=cols,
        low_memory=False
    )
    # Keep only rows that are in the US
    df_google = df_load.loc[df_load['country_region_code'] == 'US']
    # Insert a new 'id' column (state name + county name)
    df_google.insert(len(df_google.columns), 'id', \
        df_google['sub_region_1'] + ' ' + df_google['sub_region_2'] + '-',\
        allow_duplicates=False)
    pd.options.mode.chained_assignment = None
    df_google['id'] = df_google['id'].str.replace(' County-', '')
    df_google['id'] = df_google['id'].str.replace(' Borough-', '')
    df_google['id'] = df_google['id'].str.replace(' Parish-', '')
    # Drop rows that do not represent county properly
    df_google = df_google.dropna(subset=['sub_region_1', 'sub_region_2'])
    # Remove unnecessary columns
    df_google = df_google.drop(['sub_region_1', 'sub_region_2', \
     'country_region_code'], 1)
    # Read FIPS dictionary
    with open('raw_data/dicts/fips_codes.txt', 'r') as f:
        contents = f.read()
        fips_dict = ast.literal_eval(contents)
    df_google['fips'] = df_google['id'].replace(fips_dict)
    pd.options.mode.chained_assignment = 'warn' # return to default
    df_google = df_google.drop(['id'], 1) # drop ID column

    return df_google

def unacast_to_pd(): # process Unacast data as Pandas dataframe
    path = get_latest_file('unacast')
    with open(path) as data:
        reader = csv.reader(data)
        cols = next(reader)
    for i in range(3):
        _ = cols.pop(0) # remove 'state_code', 'state_fips', and 'state_name'
    _ = cols.pop(1) # remove 'county_name'
    _ = cols.pop(2) # remove 'last_updated'
    df_unacast = pd.read_csv(
        path,
        header=0,
        usecols=cols,
        low_memory=False
    )

    return df_unacast

if __name__ == '__main__':
    rename_em()
    test = get_latest_file('apple')
    print(test)
    print(check_lastest_file(test))
    print(apple_mobility_to_pd())
    print(google_mobility_to_pd())
    print(unacast_to_pd())
