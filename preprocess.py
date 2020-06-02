"""
This module preprocesses raw datasets into usable Pandas df.
Notice that at early developing stage, we are only focusing on US counties.
"""

import os, sys
import numpy as np
import pandas as pd
from datetime import datetime, date
from jhu_rename import rename_em

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

if __name__ == '__main__':
    rename_em()
    test = get_latest_file('jhu')
    print(test)
    print(check_lastest_file(test))
