"""
This module preprocesses raw datasets into usable Pandas df
"""

import os, sys
import numpy as np
import pandas as pd
from datetime import datetime, date

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
        lastest_dir = dir + src + '/' + lastest_file
    return lastest_dir

def check_lastest_file(dir): # verify the lastest file with system time
    src = dir.split('/')[1]
    if src == 'apple':
        t = date.today().isoformat()
        if t == dir.split('applemobilitytrends-')[1].replace('.csv', ''):
            return True
        else:
            return False

def get_file_on_date(src, date, dir='raw_data/'): # get the directory of the file on specified date
    if src == 'apple':
        new_dir = dir + src + '/' + 'applemobilitytrends-' + date + '.csv'
    if src == 'unacast':
        new_dir = dir + src + '/county/' + 'COVID_' + date + \
            '_sds-v3-full-county.csv'
    return new_dir

if __name__ == '__main__':
    test = get_latest_file('apple')
    print(test)
    print(check_lastest_file(test))
