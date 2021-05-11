import pandas as pd
import sys

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District Of Columbia': 'DC',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

def get_state_fips():

    # Source: US census
    # Link: www.census.gov/geographies/reference-files/2017/demo/popest/2017-fips.html
    # File:  2017 State, County, Minor Civil Division, and Incorporated Place FIPS Codes
    # Note: .xslx file header was removed and sheet was exported to csv
    fips_data = pd.read_csv("data/geodata/all-geocodes-v2017.csv",encoding = "ISO-8859-1", dtype={'State Code (FIPS)': str, 'County Code (FIPS)': str})

    # Map 040 level fips code to state name in dictionary
    state_data = fips_data[fips_data['Summary Level'] == 40].copy(deep=True)
    state_data['state_abbrev'] = state_data['Area Name (including legal/statistical area description)'].apply(lambda x : us_state_abbrev[x])
    state_map = pd.Series(state_data['State Code (FIPS)'].values,index=state_data['state_abbrev']).to_dict()
    state_map['AS'] = "60"
    state_map['GU'] = "66"
    state_map['MP'] = "69"
    state_map['PR'] = "72"
    state_map['VI'] = "78"

    # Get all county fips codes
    fips_data = fips_data[fips_data['Summary Level'] == 50]
    fips_data.insert(0, 'FIPS', fips_data['State Code (FIPS)'] + fips_data['County Code (FIPS)'])
    fips_data = fips_data[['FIPS', 'State Code (FIPS)']]

    return state_map, fips_data


def preprocess_testing(after_mar_the_seventh = True):
    print("• Processing COVID Tracking Project Testing Data")

    state_map, fips_data = get_state_fips()

    # State testing data obtained from the COVID Tracking Project (www.covidtracking.com)

    # COVID Tracking Project stopped updating since Mar 7th, 2021
    # API is last accessed on 2021-05-11
    # Original API: https://covidtracking.com/api/v1/states/daily.csv
    testing = pd.read_csv("data/COVIDTracking/covidtracking_2021_03_07.csv", usecols = ['date', 'state', 'totalTestResultsIncrease', 'positiveIncrease'], dtype = {'date':str})
    testing['state'] = testing['state'].apply(lambda x : state_map[x])
    testing['date'] = pd.to_datetime(testing['date'])
    testing = testing.sort_values(['state','date']).reset_index(drop=True)

    if after_mar_the_seventh:
        new_testing = pd.read_csv("https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/testing_data/time_series_covid19_US.csv", usecols=['date', 'state', 'tests_combined_total', 'cases_conf_probable'], dtype={'date':str})
        new_testing = new_testing.rename(columns = {'cases_conf_probable': 'positiveIncrease', 'tests_combined_total':'totalTestResultsIncrease'})
        new_testing['date'] = pd.to_datetime(new_testing['date'])
        new_testing['state'] = new_testing['state'].apply(lambda x : state_map[x])
        new_testing = new_testing.sort_values(['state','date']).reset_index(drop=True)
        new_testing['positiveIncrease'] = new_testing.groupby("state")['positiveIncrease'].diff()
        new_testing['totalTestResultsIncrease'] = new_testing.groupby("state")['totalTestResultsIncrease'].diff()
        new_testing = new_testing.dropna()
        new_testing[['positiveIncrease', 'totalTestResultsIncrease']] = new_testing[['positiveIncrease', 'totalTestResultsIncrease']].astype(int)
        new_testing = new_testing[new_testing['date'] > "2021-03-07"].reset_index(drop=True)

        testing = pd.concat([testing, new_testing], axis=0)
        
    testing = testing.sort_values(['state', 'date']).reset_index(drop=True)

    # Compute 7 day (weekly) rolling averages for state testing data
    testing['positiveIncrease'] = pd.Series(testing.groupby("state")['positiveIncrease'].rolling(14).mean()).reset_index(drop=True)
    testing['totalTestResultsIncrease'] = pd.Series(testing.groupby("state")['totalTestResultsIncrease'].rolling(14).mean()).reset_index(drop=True)

    # Move dates forward by 1 day so that movement averages represent data from past week
    testing['date'] = testing['date'] + pd.Timedelta(value=1, unit='day')
    testing['date'] = testing['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    # Source: US Census
    # Link: www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/
    # File: nst-est2019-alldata.csv
    state_populations = pd.read_csv("data/census/nst-est2019-alldata.csv", usecols = ['SUMLEV', 'STATE', 'POPESTIMATE2018'], dtype={'STATE':str, 'POPESTIMATE2018':float})

    # Process state population data (from 2018)
    state_populations = state_populations[state_populations['SUMLEV'] == 40].drop(['SUMLEV'], axis=1).rename({'STATE':'state', 'POPESTIMATE2018': 'population'}, axis=1).reset_index(drop=True)

    # Merge state population and state testing data
    testing_pop = pd.merge(left=testing, right=state_populations, how='left', on='state', copy=False)
    testing_pop['positiveIncrease_norm'] = (testing_pop['positiveIncrease']/testing_pop['population']) * 100000
    testing_pop['totalTestResultsIncrease_norm'] = (testing_pop['totalTestResultsIncrease']/testing_pop['population']) * 100000
    testing_pop = testing_pop.dropna().drop('population', axis=1)
    testing_pop['test_positivity'] = testing_pop['positiveIncrease'] / testing_pop['totalTestResultsIncrease']
    #testing_pop['test_positivity_norm'] = testing_pop['positiveIncrease_norm'] / testing_pop['totalTestResultsIncrease_norm']
    #testing_pop = testing_pop.drop(['positiveIncrease', 'totalTestResultsIncrease'], axis=1)

    # Get dataframe of all dates mapped to all FIPS from the Rt data
    fips_df = pd.read_csv("data/JHU/jhu_data.csv", dtype={'FIPS':str,'state':str}, usecols=['FIPS','date'])
    fips_df['state'] = fips_df['FIPS'].str.slice(stop=2)

    merged_df = pd.merge(left=fips_df, right=testing_pop, how='left', on=['state', 'date'], copy=False)
    merged_df = merged_df.drop(['state'], axis=1)

    merged_df.to_csv("data/COVIDTracking/testing_data.csv.gz", sep=',', compression='gzip', index=False)

    print("  Finished\n")

if __name__ == "__main__":
    preprocess_testing()
