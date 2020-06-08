"""
This module preprocesses raw datasets into usable Pandas df before merging into
final dataset.
Notice that at early developing stage, we are only focusing on US counties.
"""

import os, sys
import numpy as np
import pandas as pd
from datetime import datetime, date
from preprocess_jhu_rename import rename_em
import csv
import ast
from preprocess_fips_dict import get_fips_dict


def get_latest_file(src, dir='raw_data/'): # get the directory of the lastest file
    if src == 'apple': # get path of the lastest Apple Mobility Report
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

    if src == 'jhu': # get path to the lastest Johns Hopkins Report
        files = os.listdir(dir + src + '/county_renamed')
        new_files = []
        for file in files:
            new_file = file.replace('-', '')
            new_file = new_file.replace('.csv', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + '.csv'
        path = dir + src + '/county_renamed/' + lastest_file

    if src == 'kaggle': # WE ARE TEMPORARILY NOT USING THIS ANYMORE
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

    if src == 'google': # get path of the lastest Google Mobility Report
        files = os.listdir(dir + src)
        new_files = []
        for file in files:
            new_file = file.replace('-', '')
            new_file = new_file.replace('.csv', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + '.csv'
        path = dir + src + '/' + lastest_file

    if src == 'unacast': # WE ARE TEMPORARILY NOT USING THIS ANYMORE
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

    if src == 'mobility': # get path to the lastest mobility (google + apple)
        files = os.listdir('processed_data/' + src)
        new_files = []
        for file in files:
            new_file = file.replace('mobility-', '')
            new_file = new_file.replace('.csv', '')
            new_file = new_file.replace('-', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = 'mobility-' + max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + \
            '.csv'
        path = 'processed_data/' + src + '/' + lastest_file

    if src == '7-days-mobility': # get path to the lastest 7-days-mobility (google + apple)
        files = os.listdir('processed_data/' + src)
        new_files = []
        for file in files:
            new_file = file.replace('7d-mobility-', '')
            new_file = new_file.replace('.csv', '')
            new_file = new_file.replace('-', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = '7d-mobility-' + max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + \
            '.csv'
        path = 'processed_data/' + src + '/' + lastest_file

    if src == 'facebook': # get path to lastest facebook Mobility Data
        files = os.listdir(dir + src)
        new_files = []
        for file in files:
            new_file = file.replace('.csv', '')
            new_file = new_file.replace('-', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + \
            '.csv'
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
    # Keep only rows that represent 'driving'
    df_apple = df_apple.loc[df_apple['transportation_type'] == 'driving']

    # Filter out Virgin Islands, Puerto Rico, and Guam since there is not enough
    # relavant data for further analysis
    pd.options.mode.chained_assignment = None
    df_apple = df_apple.replace('Virgin Islands', np.NaN)
    df_apple = df_apple.replace('Puerto Rico', np.NaN)
    df_apple = df_apple.replace('Guam', np.NaN)
    df_apple = df_apple.dropna(subset=['region'])

    # Insert a new 'id' column (state name + county name)
    df_apple.insert(0, 'id', \
        df_apple['sub-region'] + ' ' + df_apple['region'] + '-',\
        allow_duplicates=False)
    df_apple['id'] = df_apple['id'].str.replace(' City and Borough-', '')
    df_apple['id'] = df_apple['id'].str.replace(' County-', '')
    df_apple['id'] = df_apple['id'].str.replace(' Borough-', '')
    df_apple['id'] = df_apple['id'].str.replace(' Parish-', '')
    df_apple['id'] = df_apple['id'].str.replace(' City-', '')
    df_apple['id'] = df_apple['id'].str.replace(' Island-', '')
    df_apple['id'] = df_apple['id'].str.replace(' Municipality-', '')

    # Read FIPS dictionary
    with open('raw_data/dicts/fips_codes.txt', 'r') as f:
        contents = f.read()
        fips_dict = ast.literal_eval(contents)
    df_apple['fips'] = df_apple['id'].replace(fips_dict)
    pd.options.mode.chained_assignment = 'warn' # return to default

    # Drop the all the unnecessary columns
    df_apple = df_apple.drop(['geo_type', 'region', 'sub-region', 'id',
        'transportation_type'], 1)

    # Switch the date header columns into row of dates
    df_apple = df_apple.melt(id_vars=['fips'], var_name='date', \
        value_name='apple_mobility').sort_values(['fips', 'date'])
    df_apple = df_apple.dropna(subset=['fips']).sort_values(['fips', 'date'])
    df_apple = df_apple.reset_index(drop=True)

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
    pd.options.mode.chained_assignment=None
    df_google['id'] = df_google['id'].str.replace(' City and Borough-', '')
    df_google['id'] = df_google['id'].str.replace(' County-', '')
    df_google['id'] = df_google['id'].str.replace(' Borough-', '')
    df_google['id'] = df_google['id'].str.replace(' Parish-', '')
    df_google['id'] = df_google['id'].str.replace(' City-', '')
    df_google['id'] = df_google['id'].str.replace(' Island-', '')
    df_google['id'] = df_google['id'].str.replace(' Municipality-', '')
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
    pd.options.mode.chained_assignment='warn' # return to default
    df_google = df_google.drop(['id'], 1) # drop ID column

    cols = cols[4:] # get the column names of mobility records
    # Take the average of the categories as a new column
    df_google['google_mobility'] = df_google[cols].mean(axis=1, skipna=True)

    df_google = df_google.drop(cols, 1) # drop all the unnecessary columns

    df_google = df_google.reset_index(drop=True)

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
    # drop unnecessary columns
    df_unacast = df_unacast.drop(['covid', 'grade_total', 'n_grade_total', \
        'grade_distance', 'n_grade_distance', 'grade_visitation', 'n_grade_visitation',
        'grade_encounters', 'n_grade_encounters'], 1)
    return df_unacast

def merger(dst='processed_data/mobility'): # merge all the mobility reports into one csv file
    t = date.today().isoformat()
    dst = dst + '-' + t + '.csv'
    df_google = google_mobility_to_pd()
    df_apple = apple_mobility_to_pd()
    df_merged = pd.merge(df_google, df_apple, how='outer', on=['fips', 'date'])
    if os.path.exists(dst): # overwrite the old dataset (if any)
        os.remove(dst)
    df_merged.to_csv(dst, index=False) # export as csv file
    return df_merged

def final(dst='processed_data/7-days-mobility/7d-mobility-'):
    t = date.today().isoformat()
    dst = dst + t + '.csv'
    path = get_latest_file('mobility')
    mobility = pd.read_csv(path, dtype={'fips':str})
    # drop rows with empty entries in any column
    mobility = mobility.sort_values(['fips', 'date'], axis=0).dropna()
    fips_list = pd.read_csv("raw_data/census/census-2018.csv",\
        dtype={'FIPS': str})['FIPS'].tolist()
    mobility = mobility[mobility['fips'].isin(fips_list)].sort_values(['fips',\
        'date']).reset_index(drop=True)

    cols = ['google_mobility', 'apple_mobility']
    new_cols = ['google_mobility_7d', 'apple_mobility_7d']

    for i in range(len(cols)):
        mobility[new_cols[i]] = \
            pd.Series(mobility.groupby('fips')[cols[i]].rolling(7).mean()).reset_index(drop=True)

    if os.path.exists(dst): # to overwrite the old data (if any)
        os.remove(dst)

    mobility.to_csv(dst, index=False)

    return mobility

if __name__ == '__main__':
    rename_em()
    get_fips_dict()
    test = get_latest_file('google')
    print(test)
    print(check_lastest_file(test))
    print(apple_mobility_to_pd())
    print(google_mobility_to_pd())
    print(merger())
    print(final())
