"""
This module preprocesses raw datasets into usable Pandas df before merging into
final dataset.
Notice that at early developing stage, we are only focusing on US counties.
"""

import os, sys
import numpy as np
import pandas as pd
from datetime import datetime, date
from scripts/jhu_rename import rename_em
import csv

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

def create_fips_dict():
    fips = {}

def apple_mobility_to_pd(): # read Apple Mobility Report as Pandas dataframe
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
    return df_apple

def google_mobility_to_pd():
    path = get_latest_file('google')
    with open(path) as data:
        reader = csv.reader(data)
        cols = next(reader)
    _ = cols.pop(1) # filter out 'country_region'
    df_load = pd.read_csv(
        path,
        header=0,
        usecols=cols
    )
    # Keep only rows that are in the US
    df_google = df_load.loc[df_load['country_region_code'] == 'US']
    #df_google.insert(len(df_google.columns), 'fips', 'NaN', allow_duplicates=False)
    return df_google


if __name__ == '__main__':
    rename_em()
    test = get_latest_file('apple')
    print(test)
    print(check_lastest_file(test))
    print(google_mobility_to_pd())
