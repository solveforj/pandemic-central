import pandas as pd
import numpy as np
from sklearn.metrics import r2_score

TEST_PATH = 'predictions/analytics/state.png'

pd.set_option('display.max_columns', 500)

s_state_abbrev = {
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

predictions = pd.read_csv("predictions/website/web_latest.csv", usecols=['FIPS','ID','total_cases_percent','POP_DENSITY'])
predictions['FIPS'] = predictions['FIPS'].astype(str).str.zfill(5)
predictions['state'] = predictions['ID'].apply(lambda x: x.split(", ")[-1])
predictions['state'] = predictions['state'].map(s_state_abbrev)
to_select = range(3, len(predictions) + 1, 4)

county = predictions.iloc[to_select, :].reset_index(drop=True)
county['Percent Change'] = county['total_cases_percent'].diff()/county['total_cases_percent'].shift(1) * 100
county = county.groupby("FIPS").tail(1)
county['FIPS'] = county['FIPS'].astype(str).str.zfill(5)
county['state'] = county['ID'].apply(lambda x: x.split()[-1])
county_danger = county[(county['POP_DENSITY'] > 500) & (county['Percent Change'] > 0)].sort_values("Percent Change").reset_index(drop=True)

state = predictions.iloc[to_select, :].reset_index(drop=True)
state_past = state.iloc[::2,:].reset_index(drop=True)
state_past['state_case_percent'] = state_past.groupby("state")['total_cases_percent'].transform('sum')
state_future = state.iloc[1::2, :].reset_index(drop=True)
state_future['state_case_percent'] = state_future.groupby("state")['total_cases_percent'].transform('sum')
state = state_future[['state']].reset_index(drop=True)
state['Percent Change'] = (state_future['state_case_percent'] - state_past['state_case_percent'])/state_past['state_case_percent'] * 100
state = state.groupby("state").head(1).sort_values("Percent Change").reset_index(drop=True)
state_danger = state[state['Percent Change'] > 0].reset_index(drop=True)

print(state)

import plotly.express as px  # Be sure to import express
from urllib.request import urlopen
import json
from map import add_watermark
import plotly.io as pio


def state_choropleth():
    fig = px.choropleth(state,  # Input Pandas DataFrame
                        locations="state",  # DataFrame column with locations
                        color="Percent Change",  # DataFrame column with color values
                        hover_name="Percent Change", # DataFrame column hover info
                        labels={'Percent Change':'% Change'},
                        locationmode = 'USA-states',
                        color_continuous_midpoint=0,
                        color_continuous_scale="Spectral_r",
                        width=1100,
                        height=600) # Set to plot as US States
    fig.update_layout(
        title_text = 'Percent Change in Infected Population Projected Next Month vs. Last Month', # Create a Title
        geo_scope='usa',  # Plot only the USA instead of globe
        title_x = 0.5,
        # font=dict(
        #     family="Times New Roman",
        #     size=18,
        #     color="Black"
        # )
    )
    pio.write_image(fig, file=TEST_PATH)

state_choropleth()
#add_watermark(TEST_PATH, type='vaccinations')

def county_choropleth():
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    fig = px.choropleth(state,  # Input Pandas DataFrame
                        locations="state",  # DataFrame column with locations
                        color="Percent Change",  # DataFrame column with color values
                        hover_name="Percent Change", # DataFrame column hover info
                        locationmode = 'USA-counties',
                        color_continuous_midpoint=0,
                        color_continuous_scale=["blue","white","red"], # Set to plot as US States
                        width=1100,
                        height=600)
    fig.update_layout(
        title_text = 'Percent Change in Infected Population Next Month vs. Last Month', # Create a Title
        geo_scope='usa',  # Plot only the USA instead of globe
        title_x = 0.5)

        # font=dict(
        #     family="Times New Roman",
        #     size=18,
        #     color="Black"

    fig.show()  # Output the plot to the screen



def jhu():
    data = pd.read_csv("predictions/analytics/truth-Incident-Cases.txt", low_memory=False)
    data = data[data['location'].str.len() > 4]

    data = data.sort_values(["location", "date"]).reset_index(drop=True)

    # For each day in each county, calculate number of cumulative cases for past 7 days
    data['weekly_sum'] = data.groupby('location').rolling(window=7).sum().reset_index(drop=True)
    data = data.dropna()

    # Shift dates back 7 days so rolling mean of cases represents cumulative cases for the 7 days ahead
    data['shift'] = [-7] * len(data)
    data['shift'] = pd.to_timedelta(data['shift'], unit='D')
    data['shift_date'] = pd.to_datetime(data['date']) + data['shift']
    data['shift_date'] = data['shift_date'].astype(str)
    data = data.drop(['shift'], axis=1)[['location', 'shift_date', 'weekly_sum']]
    data['location'] = data['location'].astype(int)
    data = data.rename({'location': 'FIPS', 'shift_date': 'date'}, axis=1).reset_index(drop=True)
    #print(data[(data['location'] == 48113) & (data['shift_date'] > "2020-08-01")].head(30))
    return data

def read_census():
    #census = pd.read_csv("data/census/Reichlab_Population.csv").iloc[58:]
    #census['location'] = census['location'].astype(int)
    #d = dict(zip(census['location'], census['population']))
    census = pd.read_csv("data/census/census.csv")
    density_d = dict(zip(census['FIPS'], census['POP_DENSITY']))
    pop_d = dict(zip(census['FIPS'], census['TOT_POP']))
    return density_d, pop_d

def jhu_pc():
    data = pd.read_csv("data/JHU/jhu_data.csv")
    data = data[['FIPS', 'date', 'confirmed_cases']]
    data = data.rename({'confirmed_cases':'weekly_sum'}, axis=1)

    data['shift'] = [-7] * len(data)
    data['shift'] = pd.to_timedelta(data['shift'], unit='D')
    data['shift_date'] = pd.to_datetime(data['date']) + data['shift']
    data['shift_date'] = data['shift_date'].astype(str)
    data = data.drop(['shift'], axis=1)[['FIPS', 'shift_date', 'weekly_sum']]
    data = data.rename({'shift_date': 'date'}, axis=1).reset_index(drop=True)
    return data

def error_for_week(pc_website_file):
    data = jhu()

    pc = pd.read_csv(pc_website_file)
    pc = pc[pc['type']=="projection"][['FIPS','date','cases']]
    pc = pd.merge(left=pc, right=data, how='left', on=['FIPS', 'date'], copy=False)
    print(pc.head(20))
    census = read_census()
    pc['population'] = pc['FIPS'].map(census)
    #data = data[data['location'] >= 1001]
    pc['normalized_JHU'] = pc['weekly_sum']
    pc['normalized_PC'] = (pc['cases'] * 7)/pc['population'] * 100000
    pc['MAE'] = (pc['normalized_PC'] - pc['normalized_JHU']).abs()
    pc = pc.dropna()

    from sklearn.metrics import r2_score

    r2 = r2_score(pc['weekly_sum'], pc['cases'])
    print(r2, pc['MAE'].mean())

# Finds counties that had Rt values since August 2020
def get_rt_counties():
    data = pd.read_csv("data/Rt/rt_data.csv")
    data = data[data['date'] > "2020-08-01"]
    filtered_data = data.groupby("FIPS").filter(lambda g: (len(g['RtIndicator']) == len(g['RtIndicator'].dropna())))
    return filtered_data['FIPS'].unique()

def get_rt_predictions():
    date = "2020-12-26"
    week1 = pd.read_csv("data/Rt/aligned_rt_7.csv", dtype={'FIPS':'str'})
    week2 = pd.read_csv("data/Rt/aligned_rt_14.csv", dtype={'FIPS':'str'})
    week3 = pd.read_csv("data/Rt/aligned_rt_21.csv", dtype={'FIPS':'str'})
    week4 = pd.read_csv("data/Rt/aligned_rt_28.csv", dtype={'FIPS':'str'})


    testing_data = pd.read_csv("data/COVIDTracking/testing_data.csv.gz", dtype={"FIPS":'str'})[['FIPS', 'date', 'totalTestResultsIncrease_norm']]

    census = pd.read_csv("data/census/census.csv", dtype={'FIPS':'str'})[['FIPS','TOT_POP']]



    weeks = [week1, week2, week3, week4]
    shift = ['7', '14', '21', '28']
    combined = pd.DataFrame()

    for i in range(len(weeks)):
        week = weeks[i]
        week = pd.merge(left=week, right=testing_data, how='left', on=['FIPS', 'date'], copy=False)
        week = pd.merge(left=week, right=census, how='left', on=['FIPS'], copy=False)
        week['value'] = (week['prediction_aligned_int_' + shift[i]] * week['totalTestResultsIncrease_norm'] * week['TOT_POP'] / 100000).round(0)
        week['shift'] = [-7] * len(week)
        week['shift'] = pd.to_timedelta(week['shift'], unit='D')
        week['shift_date'] = pd.to_datetime(week['date']) + week['shift']
        week['shift_date'] = week['shift_date'].astype(str)
        week = week.drop(['shift','date'], axis=1).rename({'shift_date': 'date'}, axis=1).reset_index(drop=True)
        week = week[week['date'] == date][['FIPS', 'date', 'value']]
        week['target'] = [int(shift[i])] * len(week)
        combined = pd.concat([combined, week], axis=0)

    combined = combined.sort_values(['FIPS', 'target'])

    combined['type'] = ['point'] * len(combined)
    combined['target'] = ["1 wk ahead inc case", "2 wk ahead inc case", "3 wk ahead inc case", "4 wk ahead inc case"] * int(len(combined)/4)
    combined = combined.rename({'FIPS': 'location', 'date': 'forecast_date'}, axis=1)
    return combined


def process_Reich(file, data, file_is_var = False):
    if not file_is_var:
        pc = pd.read_csv(file, dtype={'location':'str'})
    else:
        pc = file

    date = "2020-12-26"
    # The output of reichlab.py will have start date of its generation, so this must be overwritten with the actual date for which it was computed
    pc['forecast_date'] = [date] * len(pc)

    pc = pc[pc['location'].str.len() > 4] # Filter for counties
    pc['location'] = pc['location'].astype(int)
    pc = pc[pc['target'].isin(["1 wk ahead inc case", "2 wk ahead inc case", "3 wk ahead inc case", "4 wk ahead inc case"])] # Filter for incident case projections for next 4 weeks
    pc = pc[pc['type']=="point"] # Filter out quantiles
    pc = pc.sort_values(["location", "target"]).reset_index(drop=True)

    # Shift date to start dates of forecast weeks
    pc['shift'] = [7, 14, 21, 28] * int(len(pc)/4)
    pc['shift'] = pd.to_timedelta(pc['shift'], unit='D')
    pc['shift_date'] = pd.to_datetime(pc['forecast_date']) + pc['shift']
    pc['shift_date'] = pc['shift_date'].astype(str)
    pc = pc.drop(['shift','forecast_date'], axis=1).rename({'shift_date': 'date'}, axis=1).reset_index(drop=True)


    pc = pc.rename({'forecast_date': 'date', 'location': 'FIPS', 'value': 'pc_cases'}, axis=1)[['FIPS', 'date', 'pc_cases']]
    pc = pd.merge(left=pc, right=data.copy(deep=True), how='left', on=['FIPS', 'date'], copy=False) # Add in case data

    #print(pc.head(30))
    fips = get_rt_counties() # Get FIPS that have county Rt

    density_d, pop_d = read_census()
    pc['population_density'] = pc['FIPS'].map(density_d) # Add population to each county
    pc['population'] = pc['FIPS'].map(pop_d) # Add population to each county
    pc = pc.dropna()

    not_fips = pc[~pc['FIPS'].isin(fips)] # Filter for counties with county Rt

    print(len(pc['FIPS'].unique()))
    pc = pc[(pc['population_density'] <= 500) & (pc['weekly_sum'] > 0) & pc['FIPS'].isin(fips)]
    print(len(pc['FIPS'].unique()))
    pc['normalized_JHU'] = pc['weekly_sum']/pc['population'] * 100000
    pc['normalized_PC'] = pc['pc_cases']/pc['population'] * 100000
    pc['MAE'] = (pc['normalized_PC'] - pc['normalized_JHU']).abs()
    pc['MAPE'] = (((pc['normalized_PC']) - (pc['normalized_JHU']+1))/(pc['normalized_JHU'] +1)).abs()

    correlation = pc['weekly_sum'].corr(pc['pc_cases'])
    r2 = r2_score(pc['weekly_sum'], pc['pc_cases'])

    print(correlation, r2, pc['MAE'].mean(), pc['MAPE'].mean())


reichs = ["predictions/covid19-forecast-hub/2021-01-29-PandemicCentral-USCounty.csv",\
 "https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-processed/COVIDhub-ensemble/2020-12-28-COVIDhub-ensemble.csv", \
 "https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-processed/Google_Harvard-CPF/2020-12-27-Google_Harvard-CPF.csv", \
 "https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-processed/UCLA-SuEIR/2020-12-27-UCLA-SuEIR.csv", \
 #"https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-processed/CMU-TimeSeries/2020-12-28-CMU-TimeSeries.csv", \
 "https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-processed/Microsoft-DeepSTIA/2020-12-28-Microsoft-DeepSTIA.csv", \
 "https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-processed/OneQuietNight-ML/2021-01-24-OneQuietNight-ML.csv", \
 #"https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-processed/OliverWyman-Navigator/2020-12-27-OliverWyman-Navigator.csv", \
 #"https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-processed/UMass-MechBayes/2020-12-27-UMass-MechBayes.csv", \
]

#reichs = ["predictions/covid19-forecast-hub/2021-01-29-PandemicCentral-USCounty.csv"]
#data = jhu()
#data = jhu_pc()
#for i in reichs:
#    print(i.split('/')[-1].split('-')[-2:])
#    process_Reich(i, data)
#get_rt_counties()
#data = jhu()
#print(data)
#jhu_pc()
#jhu()
#error_for_week("predictions/website/web_2020-12-27.csv")
#read_census()

#data = jhu_pc()
#print(data[(data['FIPS'] == 1001) & (data['date'] > "2021-01-20Q")])
#rt_predictions = get_rt_predictions()
#print(rt_predictions)
#process_Reich(rt_predictions, data, file_is_var=True)

#rf_predictions = "predictions/covid19-forecast-hub/2021-01-29-PandemicCentral-USCounty.csv"
#process_Reich(rt_predictions, data, file_is_var=True)

#for i in reichs:
#    print(i.split('/')[-1].split('-')[-2:])
#    process_Reich(i, data)
