"""
This module preprocesses JHU and NYC Public Health Department data.

Data source:
    https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
    https://www1.nyc.gov/site/doh/covid/covid-19-data.page
"""

import pandas as pd
from urllib.request import urlopen
import io
import os
from datetime import datetime

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'

def get_rt_live_state_lv():
    print('• Processing JHU Data - State Level')
    df = pd.read_csv('data/JHU/jhu_data.csv',\
                    usecols=['FIPS', 'date', 'confirmed_cases', 'confirmed_cases_norm'],\
                    dtype={'FIPS':'str'},
                    low_memory=False)
    df_death = pd.read_csv('data/JHU/jhu_data_deaths.csv',\
                    usecols=['FIPS', 'date', 'confirmed_deaths', 'confirmed_deaths_norm'],\
                    dtype={'FIPS':'str'},
                    low_memory=False)
    df = df.merge(df_death, on=['FIPS', 'date'])
    geo = pd.read_csv('data/geodata/state_fips.csv',\
                    usecols=[1,2])
    geo_dict = dict(zip(geo.fips, geo.abbr))
    df['FIPS'] = df['FIPS'].str[:2].astype('int').replace(geo_dict)
    df = df.groupby(['FIPS', 'date']).sum().reset_index()
    df = df.rename(columns={'FIPS':'state'})
    df.to_csv('data/JHU/state_jhu_data.csv', index=False)
    print('  Finished\n')

def preprocess_JHU(type='cases'):
    print(f'• Processing JHU {type.capitalize()} Data - County Level')

    # Get all other data from Johns Hopkins
    if type == 'cases':
        jhu_data = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv").dropna()
    elif type == 'deaths':
        jhu_data = pd.read_csv(f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_{type}_US.csv").dropna()

    jhu_data['FIPS'] = jhu_data['FIPS'].astype(int).astype(str)

    jhu_data = jhu_data[jhu_data['FIPS'].notnull()]

    def process_FIPS(fips):
        missing_zeroes = "0" * (5-len(fips))
        return missing_zeroes + fips

    jhu_data['FIPS'] = jhu_data['FIPS'].apply(lambda x : process_FIPS(x))

    if type == 'cases':
        jhu_data = jhu_data.drop(["Admin2","Province_State","Country_Region","Lat","Long_","Combined_Key","UID","iso2","iso3","code3"], axis=1)
    elif type == 'deaths':
        jhu_data = jhu_data.drop(["Admin2","Province_State","Country_Region","Lat","Long_","Combined_Key","UID","iso2","iso3","code3", "Population"], axis=1)

    jhu_data = jhu_data.melt(id_vars=['FIPS'], var_name = 'date', value_name = f'confirmed_{type}')
    jhu_data['date'] = pd.to_datetime(jhu_data['date'])
    jhu_data = jhu_data.sort_values(['FIPS', 'date'])

    # Case counts are cumulative and will be converted into daily change
    jhu_data[f'confirmed_{type}'] = jhu_data.groupby('FIPS')[f'confirmed_{type}'].diff().dropna()
    full_data = jhu_data
    full_data = full_data.sort_values(['FIPS','date'], axis=0)
    full_data = full_data.reset_index(drop=True)

    # Compute 14-day (weekly) rolling average of cases for each county
    full_data[f'confirmed_{type}'] = pd.Series(full_data.groupby("FIPS")[f'confirmed_{type}'].rolling(7).mean()).reset_index(drop=True)
    full_data = full_data[full_data[f'confirmed_{type}'].notnull()]

    # Move dates forward by 1 day so that movement averages represent data from past week
    full_data['date'] = pd.to_datetime(full_data['date'])
    full_data['date'] = full_data['date'] + pd.Timedelta(value=1, unit='day')
    full_data['date'] = full_data['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    full_data = full_data.reset_index(drop=True)

    # Normalize confirmed cases for population and export to csv
    census_data = pd.read_csv("data/census/census.csv", dtype={'FIPS':str})[['FIPS', 'TOT_POP']]

    merged_df = pd.merge(left=census_data, right=full_data, how='left', on='FIPS', copy=False)

    merged_df[f'confirmed_{type}_norm'] = (merged_df[f'confirmed_{type}']/merged_df['TOT_POP'] * 100000).round()
    merged_df = merged_df.drop('TOT_POP', axis=1)
    startdate = datetime.strptime('2020-2-15', '%Y-%m-%d')
    merged_df['date'] = pd.to_datetime(merged_df['date'])
    merged_df = merged_df[merged_df['date'] >= startdate]

    if type == 'cases':
        merged_df.to_csv('data/JHU/jhu_data.csv', sep=",", index=False)
    elif type == 'deaths':
        merged_df.to_csv(f'data/JHU/jhu_data_{type}.csv', sep=",", index=False)

    print('  Finished\n')

    if type == 'cases':
        preprocess_JHU(type='deaths')
    elif type == 'deaths':
        get_rt_live_state_lv()

if __name__ == "__main__":
    preprocess_JHU()
