import pandas as pd

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

fipsData = pd.read_csv("raw_data/health_data/all-geocodes-v2017.csv",encoding = "ISO-8859-1", dtype={'State Code (FIPS)': str, 'County Code (FIPS)': str})

# Map 040 level fips code to state name in dictionary
stateData = fipsData[fipsData['Summary Level'] == 40]
stateData['state_abbrev'] = stateData['Area Name (including legal/statistical area description)'].apply(lambda x : us_state_abbrev[x])
stateMap = pd.Series(stateData['State Code (FIPS)'].values,index=stateData['state_abbrev']).to_dict()
stateMap['AS'] = "60"
stateMap['GU'] = "66"
stateMap['MP'] = "69"
stateMap['PR'] = "72"
stateMap['VI'] = "78"


testing = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv", usecols = ['date', 'state', 'totalTestResultsIncrease', 'positiveIncrease'], dtype = {'date':str})
testing['state'] = testing['state'].apply(lambda x : stateMap[x])
testing['date'] = pd.to_datetime(testing['date'])
testing = testing.sort_values(['state','date']).reset_index(drop=True)

print(testing.head(20))
# ==============================================================================
# The two lines below each perform a rolling average of a column of the DataFrame
testing['positiveIncrease'] = pd.Series(testing.groupby("state")['positiveIncrease'].rolling(7).mean()).reset_index(drop=True)
testing['totalTestResultsIncrease'] = pd.Series(testing.groupby("state")['totalTestResultsIncrease'].rolling(7).mean()).reset_index(drop=True)

print(testing.head(20))
# Rolling average applies to the previous week for the day of interest, thus, dates need to be incremented up by 1, which is done below
testing['date'] = testing['date'].apply(pd.DateOffset(1))
# ==============================================================================

testing['date'] = testing['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

statePopulations = pd.read_csv("raw_data/testing_data/nst-est2019-alldata.csv", usecols = ['SUMLEV', 'STATE', 'POPESTIMATE2019'], dtype={'STATE':str, 'POPESTIMATE2019':float})
statePopulations = statePopulations[statePopulations['SUMLEV'] == 40].drop(['SUMLEV'], axis=1).rename({'STATE':'state', 'POPESTIMATE2019': 'population'}, axis=1).reset_index(drop=True)

testing_pop = pd.merge(left=testing, right=statePopulations, how='left', on='state', copy=False)
testing_pop['positiveIncrease'] = (testing_pop['positiveIncrease']/testing_pop['population']) * 100000
testing_pop['totalTestResultsIncrease'] = (testing_pop['totalTestResultsIncrease']/testing_pop['population']) * 100000
testing_pop = testing_pop.dropna().drop('population', axis=1)


fips_DF = pd.read_csv("raw_data/rt_data/rt_data.csv", dtype={'FIPS':str,'state':str}, usecols=['FIPS','date','state'])

merged_DF = pd.merge(left=fips_DF, right=testing_pop, how='left', on=['state', 'date'], copy=False)

merged_DF.to_csv("raw_data/testing_data/testing_data.csv", sep=',', index=False)
