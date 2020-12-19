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

def preprocess_JHU():
    print('• Processing JHU Case Data')

    # Get all other data from Johns Hopkins
    jhu_data = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv").dropna()
    jhu_data['FIPS'] = jhu_data['FIPS'].astype(int).astype(str)

    jhu_data = jhu_data[jhu_data['FIPS'].notnull()]

    def process_FIPS(fips):
        missing_zeroes = "0" * (5-len(fips))
        return missing_zeroes + fips

    jhu_data['FIPS'] = jhu_data['FIPS'].apply(lambda x : process_FIPS(x))

    jhu_data = jhu_data.drop(["Admin2","Province_State","Country_Region","Lat","Long_","Combined_Key","UID","iso2","iso3","code3"], axis=1)
    jhu_data = jhu_data.melt(id_vars=['FIPS'], var_name = 'date', value_name = 'confirmed_cases')
    jhu_data['date'] = pd.to_datetime(jhu_data['date'])
    jhu_data = jhu_data.sort_values(['FIPS', 'date'])

    # Case counts are cumulative and will be converted into daily change
    jhu_data['confirmed_cases'] = jhu_data.groupby('FIPS')['confirmed_cases'].diff().dropna()
    full_data = jhu_data
    full_data = full_data.sort_values(['FIPS','date'], axis=0)
    full_data = full_data.reset_index(drop=True)

    # Compute 14-day (weekly) rolling average of cases for each county
    full_data['confirmed_cases'] = pd.Series(full_data.groupby("FIPS")['confirmed_cases'].rolling(7).mean()).reset_index(drop=True)
    full_data = full_data[full_data['confirmed_cases'].notnull()]

    # Move dates forward by 1 day so that movement averages represent data from past week
    full_data['date'] = pd.to_datetime(full_data['date'])
    full_data['date'] = full_data['date'] + pd.TimeDelta(value=1, unit='day')
    full_data['date'] = full_data['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    full_data = full_data.reset_index(drop=True)

    # Normalize confirmed cases for population and export to csv
    census_data = pd.read_csv("data/census/census.csv", dtype={'FIPS':str})[['FIPS', 'TOT_POP']]

    merged_df = pd.merge(left=census_data, right=full_data, how='left', on='FIPS', copy=False)

    merged_df['confirmed_cases_norm'] = (merged_df['confirmed_cases']/merged_df['TOT_POP'] * 100000).round()
    merged_df = merged_df.drop('TOT_POP', axis=1)
    startdate = datetime.strptime('2020-2-15', '%Y-%m-%d')
    merged_df = merged_df[merged_df['date'] >= startdate]

    merged_df.to_csv('data/JHU/jhu_data.csv', sep=",", index=False)

    print('  Finished\n')

if __name__ == "__main__":
    preprocess_JHU()
