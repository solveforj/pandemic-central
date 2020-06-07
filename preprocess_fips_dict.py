"""
This module reads Johns Hopkins COVID-19 dataset and returns dictionary to map
county and its FIPS code.

We also manually added few missing FIPS codes that JHU missed.
"""

import os, sys
import numpy as np
import pandas as pd
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


def get_fips_dict(): # Read Johns Hopkins dataset and export FIPS dictionary for county
    # Please don't run this again
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
    # Add the following missing county FIPS, too (since JHU missed them)
    dict['Utah Weber'] = '49057'
    dict['Utah Washington'] = '49053'
    dict['Utah Uintah'] = '49047'
    dict['Utah Sevier'] = '49041'
    dict['Utah Millard'] = '49027'
    dict['Utah Juab'] = '49023'
    dict['Utah Iron'] = '49021'
    dict['Utah Grand'] = '49019'
    dict['Utah Garfield'] = '49017'
    dict['Utah Cache'] = '49005'
    dict['Utah Box Elder'] = '49003'
    dict['Texas Upton'] = '48461'
    dict['Texas Sutton'] = '48435'
    dict['Texas Somervell'] = '48425'
    dict['Texas McMullen'] = '48311'
    dict['Texas Loving'] = '48301'
    dict['Texas Culberson'] = '48109'
    dict['New York Richmond'] = '36085'
    dict['New York Queens'] = '36081'
    dict['New York New York'] = '36061'
    dict['New York Kings'] = '36047'
    dict['New York Bronx'] = '36005'
    dict['New Mexico Doña Ana'] = '35013'
    dict['Nevada Carson'] = '32510'
    dict['Massachusetts Dukes'] = '25007'
    dict['Kansas Thomas'] = '20193'

    # Export dictionary of FIPS codes as text file
    if not os.path.exists('raw_data/dicts'):
        os.mkdir('raw_data/dicts')
    if os.path.exists('raw_data/dicts/fips_codes.txt'):
        os.remove('raw_data/dicts/fips_codes.txt')
    with open('raw_data/dicts/fips_codes.txt', 'w') as f:
        print(dict, file=f)
