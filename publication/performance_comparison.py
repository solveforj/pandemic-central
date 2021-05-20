import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
import glob

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

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

def get_common_fips():
    gh = pd.read_csv("publication/data/comparison_models/Google_Harvard/2020-12-27-Google_Harvard-CPF.csv", dtype={'location':'str'})
    jhu_idd = pd.read_csv("publication/data/comparison_models/JHU_IDD-CovidSP/2020-12-27-JHU_IDD-CovidSP.csv", dtype={'location':'str'})
    jhu_apl = pd.read_csv("publication/data/comparison_models/JHUAPL-Bucky/2020-12-28-JHUAPL-Bucky.csv", dtype={'location':'str'})
    oqn = pd.read_csv("publication/data/comparison_models/OneQuietNight/2020-12-27-OneQuietNight-ML.csv", dtype={'location':'str'})

    targets = ["1 wk ahead inc case", "2 wk ahead inc case", "3 wk ahead inc case", "4 wk ahead inc case"]

    fips_list = []
    df_list = [gh, jhu_idd, jhu_apl, oqn]
    for df in df_list:
        df = df[df['location'].str.len() > 4] # Filter for counties
        df = df.reset_index(drop=True)
        df['location'] = df['location'].astype(int)
        df = df[df['target'].isin(targets)] # Filter for incident case projections for next 4 weeks
        df = df[df['type']=="point"] # Filter out quantiles
        fips_list.append(df['location'].unique().tolist())

    predictions_df = pd.read_csv("output/raw_predictions/publication/raw_predictions_2020-12-27.csv")
    pc = predictions_df[predictions_df['model'] == "mobility"]['FIPS'].unique().tolist()
    fips_list.append(pc)

    result = list(set(fips_list[0]).intersection(*fips_list[1:]))
    result.sort()
    return result

def process_Reich_original(file, data):

    pc = pd.read_csv(file, dtype={'location':'str'})

    date = pc['forecast_date'].loc[0]
    targets = ["1 wk ahead inc case", "2 wk ahead inc case", "3 wk ahead inc case", "4 wk ahead inc case"]
    pc = pc[pc['location'].str.len() > 4] # Filter for counties
    pc = pc.reset_index(drop=True)
    pc['location'] = pc['location'].astype(int)
    pc = pc[pc['target'].isin(targets)] # Filter for incident case projections for next 4 weeks
    pc = pc[pc['type']=="point"] # Filter out quantiles
    pc = pc.sort_values(["location", "target"]).reset_index(drop=True)

    # Shift date to start dates of forecast weeks
    shift_dict = {"1 wk ahead inc case": 7, "2 wk ahead inc case": 14,"3 wk ahead inc case": 21,"4 wk ahead inc case": 28, }
    pc['shift'] = pc['target'].apply(lambda x: shift_dict[x])
    pc['shift'] = pd.to_timedelta(pc['shift'], unit='D')
    pc['shift_date'] = pd.to_datetime(pc['forecast_date']) + pc['shift']
    pc['shift_date'] = pc['shift_date'].astype(str)
    pc = pc.drop(['shift','forecast_date'], axis=1).rename({'shift_date': 'date'}, axis=1).reset_index(drop=True)


    pc = pc.rename({'location': 'FIPS', 'value': 'pc_cases'}, axis=1)[['FIPS', 'date', 'pc_cases','target']]
    pc = pd.merge(left=pc, right=data.copy(deep=True), how='left', on=['FIPS', 'date'], copy=False) # Add in case data

    density_d, pop_d = read_census()
    pc['population_density'] = pc['FIPS'].map(density_d) # Add population to each county
    pc['population'] = pc['FIPS'].map(pop_d) # Add population to each county
    pc = pc.dropna()

    fips_list = get_common_fips()
    pc = pc[pc['FIPS'].isin(fips_list)]
    pc = pc[(pc['population_density'] > 0) & (pc['weekly_sum'] > 0)]

    pc['normalized_JHU'] = pc['weekly_sum']/pc['population'] * 100000
    pc['normalized_PC'] = pc['pc_cases']/pc['population'] * 100000
    pc['MAE'] = (pc['normalized_PC'] - pc['normalized_JHU']).abs()
    pc['MSE'] = (pc['MAE'])**2

    correlation = pc['weekly_sum'].corr(pc['pc_cases'])
    r2 = r2_score(pc['weekly_sum'], pc['pc_cases'])

    #print(date, correlation, r2, pc['MAE'].mean(), pc['MSE'].mean())
    #print()
    output_df = []

    for i in targets:
        target_pc = pc[pc['target'] == i]
        correlation = target_pc['weekly_sum'].corr(target_pc['pc_cases'])
        r2 = r2_score(target_pc['weekly_sum'], target_pc['pc_cases'])
        output_df.append([date, i, correlation, r2, target_pc['MAE'].mean(), target_pc['MSE'].mean()])

    output_df = pd.DataFrame(output_df, columns=['date', 'target', 'correlation','R2', 'MAE','MSE'])
    return output_df

def ReichLabModelStats(directory, model_name, skip=[]):
    files = glob.glob(directory + "*.csv")
    print("Generating performance statistics for the " + model_name + " model")
    #print(files)
    jhu = jhu_pc()
    performance_df = pd.DataFrame()
    for file in files:
        #print(file)
        inskip=False
        for i in skip:
            if i in file:
                inskip = True
                break
        if inskip==False:
            #df = pd.read_csv(file, dtype={'location':'str'})
            output_df = process_Reich_original(file, jhu)
            performance_df = pd.concat([performance_df, output_df], axis=0).reset_index(drop=True)
            #print(output_df)
    performance_df['model'] = [model_name]*len(performance_df)
    performance_df.to_csv("publication/output/model_performance/" + model_name + "_performance.csv", index=False)

def performance_comparison():
    print("GENERATING PERFORMANCE STATISTICS FOR ALL MODELS\n")
    ReichLabModelStats("publication/data/comparison_models/OneQuietNight/", "OneQuietNight")
    ReichLabModelStats("publication/data/comparison_models/JHU_IDD-CovidSP/", "JHU_IDD", ["2020-11-08"])
    ReichLabModelStats("publication/data/comparison_models/JHUAPL-Bucky/", "JHUAPL-Bucky")
    ReichLabModelStats("publication/data/comparison_models/Google_Harvard/","Google_Harvard")
    ReichLabModelStats("output/ReichLabFormat/publication/", "RF")
    print("\n")
