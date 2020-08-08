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
