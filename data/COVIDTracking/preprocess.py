import pandas as pd
import sys
import os
sys.path.append(os.getcwd() + "/data/")
from geodata.utils import get_state_fips

def preprocess_testing():

    state_map, fips_data = get_state_fips()

    # State testing data obtained from the COVID Tracking Project (www.covidtracking.com)
    testing = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv", usecols = ['date', 'state', 'totalTestResultsIncrease', 'positiveIncrease'], dtype = {'date':str})
    testing['state'] = testing['state'].apply(lambda x : state_map[x])
    testing['date'] = pd.to_datetime(testing['date'])
    testing = testing.sort_values(['state','date']).reset_index(drop=True)

    # Compute 7 day (weekly) rolling averages for state testing data
    testing['positiveIncrease'] = pd.Series(testing.groupby("state")['positiveIncrease'].rolling(14).mean()).reset_index(drop=True)
    testing['totalTestResultsIncrease'] = pd.Series(testing.groupby("state")['totalTestResultsIncrease'].rolling(14).mean()).reset_index(drop=True)

    # Move dates forward by 1 day so that movement averages represent data from past week
    testing['date'] = testing['date'].apply(pd.DateOffset(1))
    testing['date'] = testing['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    # Source: US Census
    # Link: www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/
    # File: nst-est2019-alldata.csv
    state_populations = pd.read_csv("data/census/nst-est2019-alldata.csv", usecols = ['SUMLEV', 'STATE', 'POPESTIMATE2019'], dtype={'STATE':str, 'POPESTIMATE2019':float})

    # Process state population data
    state_populations = state_populations[state_populations['SUMLEV'] == 40].drop(['SUMLEV'], axis=1).rename({'STATE':'state', 'POPESTIMATE2019': 'population'}, axis=1).reset_index(drop=True)

    # Merge state population and state testing data
    testing_pop = pd.merge(left=testing, right=state_populations, how='left', on='state', copy=False)
    testing_pop['positiveIncrease_norm'] = (testing_pop['positiveIncrease']/testing_pop['population']) * 100000
    testing_pop['totalTestResultsIncrease_norm'] = (testing_pop['totalTestResultsIncrease']/testing_pop['population']) * 100000
    testing_pop = testing_pop.dropna().drop('population', axis=1)
    testing_pop['test_positivity'] = testing_pop['positiveIncrease'] / testing_pop['totalTestResultsIncrease']
    #testing_pop['test_positivity_norm'] = testing_pop['positiveIncrease_norm'] / testing_pop['totalTestResultsIncrease_norm']
    #testing_pop = testing_pop.drop(['positiveIncrease', 'totalTestResultsIncrease'], axis=1)

    # Get dataframe of all dates mapped to all FIPS from the Rt data
    fips_df = pd.read_csv("data/Rt/rt_data.csv", dtype={'FIPS':str,'state':str}, usecols=['FIPS','date','state'])

    merged_df = pd.merge(left=fips_df, right=testing_pop, how='left', on=['state', 'date'], copy=False)
    merged_df = merged_df.drop(['state'], axis=1)

    merged_df.to_csv("data/COVIDTracking/testing_data.csv", sep=',', index=False)

def main():
    print("• Processing COVID Tracking Project Testing Data")
    preprocess_testing()
    print("  Finished\n")

main()
