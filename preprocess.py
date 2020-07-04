"""
This module preprocesses Apple, Google, a bit of JHU datasets and merges them
into final data.
Notice that at early developing stage, we are only focusing on US counties.
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
__version__ = '1.0.2'
__status__ = 'released'
__url__ = 'https://github.com/solveforj/pandemic-central'

def get_latest_file(src, dir='raw_data/'): # get the directory of the lastest file
    if src == 'apple': # get path of the lastest Apple Mobility Report
        files = os.listdir(dir + src)
        new_files = []
        for file in files:
            new_file = file.replace('applemobilitytrends', '')
            new_file = new_file.replace('-', '')
            new_file = new_file.replace('.csv.gz', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = 'applemobilitytrends-' + max_[:4] + '-' + max_[4:6] + \
            '-' + max_[6:] + '.csv.gz'
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

    if src == 'google': # get path of the lastest Google Mobility Report
        files = os.listdir(dir + src)
        new_files = []
        for file in files:
            new_file = file.replace('-', '')
            new_file = new_file.replace('.csv.gz', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + '.csv.gz'
        path = dir + src + '/' + lastest_file

    if src == 'mobility': # get path to the lastest mobility (google + apple)
        files = os.listdir('processed_data/' + src)
        new_files = []
        for file in files:
            new_file = file.replace('mobility-', '')
            new_file = new_file.replace('.csv.gz', '')
            new_file = new_file.replace('-', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = 'mobility-' + max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + \
            '.csv.gz'
        path = 'processed_data/' + src + '/' + lastest_file

    if src == '14-days-mobility': # get path to the lastest 14-days-mobility (google + apple)
        files = os.listdir('processed_data/' + src)
        new_files = []
        for file in files:
            new_file = file.replace('14d-mobility-', '')
            new_file = new_file.replace('.csv', '')
            new_file = new_file.replace('-', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = '14d-mobility-' + max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + \
            '.csv'
        path = 'processed_data/' + src + '/' + lastest_file

    if src == 'facebook': # get path to lastest Facebook Mobility Data
        files = os.listdir(dir + src)
        new_files = []
        for file in files:
            new_file = file.replace('.csv.gz', '')
            new_file = new_file.replace('movement-range-', '')
            new_file = new_file.replace('-', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = 'movement-range-' + max_[:4] + '-' + max_[4:6] + \
            '-' + max_[6:] + '.csv.gz'
        path = dir + src + '/' + lastest_file

    if src == 'merged': # get path to the lastest merged file
        files = os.listdir('processed_data/' + src)
        new_files = []
        for file in files:
            new_file = file.replace('.csv.gz', '')
            new_file = new_file.replace('-', '')
            new_files.append(new_file)
        max_ = max(new_files)
        lastest_file = max_[:4] + '-' + max_[4:6] + '-' + max_[6:] + \
            '.csv.gz'
        path = 'processed_data/' + src + '/' + lastest_file

    return path

def check_lastest_file(dir): # verify the lastest file with system time
    src = dir.split('/')[1]
    if src == 'apple':
        t = date.today().isoformat()
        if t == dir.split('applemobilitytrends-')[1].replace('.csv.gz', ''):
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
        path = dir + src + '/' + 'applemobilitytrends-' + date + '.csv.gz'
    if src == 'jhu':
        path = dir + src + '/county_renamed/' + date + '.csv'
    return path

# Download Google Mobility Data and compress
def get_google_data():
    # Get file name
    content = requests.get('https://www.google.com/covid19/mobility/').content
    soup = BeautifulSoup(content, 'html.parser')
    findings = soup.findAll("p", {"class": "report-info-text"})[0].text.strip()
    filename = findings.replace('Reports created ', '')
    filename = filename.replace('.', '')
    # Get file from source
    filepath = 'raw_data/google/' + filename + '.csv.gz'
    url = 'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'
    url_health = requests.get(url).status_code
    if url_health == requests.codes.ok:
        google_df = pd.read_csv(url, low_memory=False)
        google_df.to_csv(filepath, compression='gzip', index=False)
        return 'success'
    else:
        return 'fail'

# Download Apple Mobility Data and compress
def get_apple_data():
    json_url = 'https://covid19-static.cdn-apple.com/covid19-mobility-data/current/v3/index.json'
    url_health = requests.get(json_url).status_code
    if url_health == requests.codes.ok:
        content = requests.get(json_url).text
        js = json.loads(content)
        url = 'https://covid19-static.cdn-apple.com' + js['basePath'] + \
            js['regions']['en-us']['csvPath']
        apple_df = pd.read_csv(url, low_memory=False)
        filename = url.split('/')[-1] + '.gz'
        filepath = 'raw_data/apple/' + filename
        apple_df.to_csv(filepath, compression='gzip', index=False)
        return 'success'
    else:
        return 'fail'

# Download Facebook Mobility Data and compress
def get_facebook_data():
    url = 'https://data.humdata.org/dataset/movement-range-maps'
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')
    download_url = soup.find_all('a',\
        {"class": "btn btn-empty btn-empty-blue hdx-btn resource-url-analytics ga-download"},\
         href=True)[0]['href']
    download_url = 'https://data.humdata.org' + download_url
    url_health = requests.get(download_url).status_code
    if url_health == requests.codes.ok:
        zip = requests.get(download_url)
        os.mkdir('raw_data/facebook/temp')
        temp_path = ('raw_data/facebook/temp/data.zip')
        with open(temp_path, 'wb') as temp:
            temp.write(zip.content)
        with ZipFile(temp_path, 'r') as unzip:
            unzip.extractall('raw_data/facebook/temp')

        files = os.listdir('raw_data/facebook/temp/')
        for filename in files:
            if filename.startswith('movement-range'):
                path = 'raw_data/facebook/temp/' + filename

        # Read and compress data file
        df_load = pd.read_csv(path, sep='\t', dtype={'polygon_id':str})
        df_load = df_load[df_load['country'] == 'USA']
        final = 'raw_data/facebook/' + \
            path.split('/')[-1].replace('.txt', '.csv') + '.gz'
        df_load.to_csv(final, compression='gzip', index=False)

        # Remove temp
        for filename in files:
            os.remove('raw_data/facebook/temp/' + filename)
        os.rmdir('raw_data/facebook/temp/')

        return 'success'
    else:
        return 'fail'

def apple_mobility_to_pd(): # process Apple Mobility Report as Pandas dataframe
    path = get_latest_file('apple')
    df_load = pd.read_csv(path, header=0, low_memory=False)

    # Read state abbreviations
    with open('raw_data/dicts/state_abbr.txt', 'r') as f:
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
    df_fips = pd.read_csv('raw_data/census/county_fips_2017_06.csv',\
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
    df_apple = df_apple.melt(id_vars=['fips'], var_name='date', \
        value_name='apple_mobility').sort_values(['fips', 'date'])
    df_apple = df_apple.reset_index(drop=True)

    return df_apple

def google_mobility_to_pd(): # process Google Mobility Report
    path = get_latest_file('google')
    new_path = path
    date = new_path.replace('raw_data/google/', '')
    date = date.replace('.csv.gz', '')
    date = date.replace('-', '')
    if int(date) < 20200611: # Google added new columns after this date
        df_load = pd.read_csv(
            path,
            header=0,
            low_memory=False
        )
        df_load = df_load.drop(['country_region'], 1) # filter out 'country_region'
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
        with open('raw_data/dicts/fips_codes_jhu.txt', 'r') as f:
            contents = f.read()
            fips_dict = ast.literal_eval(contents)
        df_google['fips'] = df_google['id'].replace(fips_dict)
        pd.options.mode.chained_assignment='warn' # return to default
        df_google = df_google.drop(['id'], 1) # drop ID column
        cols = df_google.columns.tolist()
        cols = cols[4:] # get the column names of mobility records

        # Take the average of the categories as a new column
        df_google['google_mobility'] = df_google[cols].mean(axis=1, skipna=True)

        # drop all the unnecessary columns
        df_google = df_google.drop(cols, 1)
        df_google = df_google.reset_index(drop=True)

    else: # Google Mobility Data already includes FIPS after 2020-06-11
        drop_list = ['country_region_code', 'country_region', 'sub_region_1', \
            'sub_region_2', 'iso_3166_2_code']
        df_load = pd.read_csv(
            path,
            header=0,
            dtype={'census_fips_code':np.str},
            low_memory=False
        )
        df_load = df_load.drop(drop_list, 1)
        # Drop rows that do not represent county properly
        df_google = df_load.dropna(subset=['census_fips_code'])
        df_google = df_google.rename(columns={'census_fips_code': 'fips'})
        cols = df_google.columns.tolist()
        cols = cols[2:] # get the column names of mobility records
        # Take the average of the categories as a new column
        df_google['google_mobility'] = df_google[cols].mean(axis=1, skipna=True)
        df_google = df_google.drop(cols, 1) # drop all the unnecessary columns
        df_google = df_google.astype({'fips': 'float'})
        df_google = df_google.astype({'fips': 'int32'})
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

# merge all the mobility reports into one csv file
def merger(dst='processed_data/mobility/mobility'):
    t = date.today().isoformat()
    dst = dst + '-' + t + '.csv.gz'
    df_google = google_mobility_to_pd()
    df_apple = apple_mobility_to_pd()
    df_merged = pd.merge(df_google, df_apple, how='outer', on=['fips', 'date'])
    if os.path.exists(dst): # overwrite the old dataset (if any)
        os.remove(dst)
    df_merged.to_csv(dst, index=False, compression='gzip') # export as csv file
    return df_merged

def final(dst='processed_data/14-days-mobility/14d-mobility'):
    t = date.today().isoformat()
    dst = dst + '-' + t + '.csv'
    path = get_latest_file('mobility')
    mobility = pd.read_csv(path, dtype={'fips':int})

    # drop rows with empty entries in any column
    mobility = mobility.sort_values(['fips', 'date'], axis=0).dropna()
    fips_list = pd.read_csv("raw_data/census/census-2018.csv",\
        dtype={'FIPS': int})['FIPS'].tolist()
    mobility = mobility[mobility['fips'].isin(fips_list)].sort_values(['fips',\
        'date']).reset_index(drop=True)

    cols = ['google_mobility', 'apple_mobility']
    new_cols = ['google_mobility_14d', 'apple_mobility_14d']

    for i in range(len(cols)):
        mobility[new_cols[i]] = \
            pd.Series(mobility.groupby('fips')[cols[i]].rolling(14).mean()).reset_index(drop=True)

    # Shift the col down by one row to make sense (past 7 days from a date)
    mobility['date'] = pd.to_datetime(mobility['date'])
    mobility['date'] = mobility['date'].apply(pd.DateOffset(1))
    mobility['date'] = mobility['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    mobility = mobility.drop(cols, 1)

    if os.path.exists(dst): # to overwrite the old data (if any)
        os.remove(dst)

    mobility.to_csv(dst, index=False)

    return mobility

def renamer(src='raw_data/jhu/county', dst='raw_data/jhu/county_renamed'):
    files = os.listdir(src)
    if not os.path.exists(dst):
        os.mkdir(dst)
    for file in files:
        m = file[:2]
        d = file[3:5]
        y = file[6:10]
        date_ = date(int(y), int(m), int(d)).isoformat()
        if not os.path.exists(dst + '/' + date_ + '.csv'):
            shutil.copy(src + '/' + file, dst + '/' + date_ + '.csv')

def main():
    renamer()
    # Download and compress Apple Mobility Data
    print('[ ] Get Apple Mobility Data', end='\r')
    status = get_apple_data()
    if status == 'success':
        print('[' + u'\u2713' + ']\n')
    else:
        print('[' + u'\u2718' + ']\n')
        print('\n Apple Mobility Data could not be found\n')

    # Download and compress Apple Mobility Data
    print('[ ] Get Google Mobility Data', end='\r')
    status = get_google_data()
    if status == 'success':
        print('[' + u'\u2713' + ']\n')
    else:
        print('[' + u'\u2718' + ']\n')
        print('\n Google Mobility Data could not be found\n')

    # PREPROCESS APPLE AND GOOGLE DATA
    print('[ ] Preprocess Apple Mobility Data', end='\r')
    apple_mobility_to_pd()
    print('[' + u'\u2713' + ']\n')

    print('[ ] Preprocess Google Mobility Data', end='\r')
    google_mobility_to_pd()
    print('[' + u'\u2713' + ']\n')

    print('[ ] Merging data', end='\r')
    merger()
    print('[' + u'\u2713' + ']\n')

    print('[ ] Calculating 14-day moving average', end='\r')
    final()
    print('[' + u'\u2713' + ']\n')

if __name__ == '__main__':
    main()
