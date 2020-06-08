"""
This module reads Johns Hopkins COVID-19 dataset and returns dictionary to map
county and its FIPS code.

We also manually added few missing FIPS codes that JHU missed or the inconsitence
in naming between datasets.
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
    # Add the following missing county FIPS, too
    dict['Virginia Winchester-'] = '51840'
    dict['Virginia Williamsburg-'] = '51830'
    dict['Virginia Waynesboro-'] = '51820'
    dict['Virginia Virginia Beach-'] = '51810'
    dict['Virginia Suffolk-'] = '51800'
    dict['Virginia Staunton-'] = '51790'
    dict['Virginia Salem-'] = '51775'
    dict['Virginia Roanoke-'] = '51770'
    dict['Virginia Richmond-'] = '51760'
    dict['Virginia Radford-'] = '51750'
    dict['Virginia Portsmouth-'] = '51740'
    dict['Virginia Poquoson-'] = '51735'
    dict['Virginia Petersburg-'] = '51730'
    dict['Virginia Norton-'] = '51720'
    dict['Virginia Norfolk-'] = '51710'
    dict['Virginia Newport News-'] = '51700'
    dict['Virginia Martinsville-'] = '51690'
    dict['Virginia Manassas Park-'] = '51685'
    dict['Virginia Manassas-'] = '51683'
    dict['Virginia Lynchburg-'] = '51680'
    dict['Virginia Lexington-'] = '51678'
    dict['Virginia Hopewell-'] = '51670'
    dict['Virginia Harrisonburg-'] = '51660'
    dict['Virginia Hampton-'] = '51650'
    dict['Virginia Galax-'] = '51640'
    dict['Virginia Fredericksburg-'] = '51630'
    dict['Virginia Franklin-'] = '51620'
    dict['Virginia Falls Church-'] = '51610'
    dict['Virginia Fairfax-'] = '51600'
    dict['Virginia Emporia-'] = '51595'
    dict['Virginia Danville-'] = '51590'
    dict['Virginia Covington-'] = '51580'
    dict['Virginia Colonial Heights-'] = '51570'
    dict['Virginia Chesapeake-'] = '51550'
    dict['Virginia Charlottesville-'] = '51540'
    dict['Virginia Buena Vista-'] = '51530'
    dict['Virginia Bristol-'] = '51520'
    dict['Virginia Alexandria-'] = '51510'
    dict['Utah Weber'] = '49057'
    dict['Utah Washington'] = '49053'
    dict['Utah Uintah'] = '49047'
    dict['Utah Sevier'] = '49041'
    dict['Utah Sanpete'] = '49039'
    dict['Utah Morgan'] = '49029'
    dict['Utah Millard'] = '49027'
    dict['Utah Kane'] = '49025'
    dict['Utah Juab'] = '49023'
    dict['Utah Iron'] = '49021'
    dict['Utah Grand'] = '49019'
    dict['Utah Garfield'] = '49017'
    dict['Utah Emery'] = '49015'
    dict['Utah Duchesne'] = '49013'
    dict['Utah Carbon'] = '49007'
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
    dict['Nebraska Deuel'] = '31049'
    dict['Montana Valley'] = '30105'
    dict['Montana Teton'] = '30099'
    dict['Montana Sanders'] = '30089'
    dict['Montana Powell'] = '30077'
    dict['Montana Mineral'] = '30061'
    dict['Montana Dawson'] = '30021'
    dict['Montana Custer'] = '30017'
    dict['Montana Blaine'] = '30005'
    dict['Missouri Wayne'] = '29223'
    dict['Missouri Shannon'] = '29203'
    dict['Missouri St. Louis-'] = '29189'
    dict['Missouri Putnam'] = '29171'
    dict['Missouri Monroe'] = '29137'
    dict['Missouri Hickory'] = '29085'
    dict['Missouri Grundy'] = '29079'
    dict['Missouri Douglas'] = '29067'
    dict['Missouri Dent'] = '29065'
    dict['Missouri Monroe'] = '29011'
    dict['Missouri Ozark'] = '29153'
    dict['Minnesota Lake of the Woods'] = '27077'
    dict['Massachusetts Nantucket'] = '25019'
    dict['Massachusetts Dukes'] = '25007'
    dict['Maryland Baltimore-'] = '24005'
    dict['Kansas Thomas'] = '20193'
    dict['Kansas Kingman'] = '20095'
    dict['California Modoc'] = '06049'
    dict['Alaska Valdez-Cordova-'] = '02261'
    dict['Alaska Southeast Fairbanks-'] = '02240'
    dict['Alaska Sitka-'] = '02220'
    dict['Alaska North Slope-'] = '02185'
    dict['Alaska Matanuska-Susitna-'] = '02170'
    dict['Alaska Kodiak'] = '02150'
    dict['Alaska Ketchikan Gateway-'] = '02130'
    dict['Alaska Juneau-'] = '02110'
    dict['Alaska Fairbanks North Star-'] = '02090'
    dict['Alaska Bethel-'] = '02050'
    dict['Alaska Anchorage-'] = '02020'
    dict['Idaho Oneida'] = '16071'
    dict['Utah Beaver'] = '49001'
    dict['Missouri Dade'] = '29057'
    dict['Idaho Bear Lake'] = '16007'
    dict['West Virginia Webster'] = '54101'
    dict['Michigan Alger'] = '26003'
    dict['Kansas Russell'] = '20167'
    dict['Idaho Boise'] = '16015'
    dict['Louisiana La Salle'] = '17099'
    dict['Idaho Clearwater'] = '16035'
    dict['Missouri Barton'] = '20009'
    dict['Illinois Scott'] = '17171'
    dict['Missouri Schuyler'] = '29197'
    dict['Kansas Marshall'] = '20117'
    dict['Idaho Shoshone'] = '16079'
    dict['Minnesota Cook'] = '17031'
    dict['Colorado Kiowa'] = '08061'
    # Export dictionary of FIPS codes as text file
    if not os.path.exists('raw_data/dicts'):
        os.mkdir('raw_data/dicts')
    if os.path.exists('raw_data/dicts/fips_codes.txt'):
        os.remove('raw_data/dicts/fips_codes.txt')
    with open('raw_data/dicts/fips_codes.txt', 'w') as f:
        print(dict, file=f)
