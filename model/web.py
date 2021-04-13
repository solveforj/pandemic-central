import pandas as pd
import urllib3
import json

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

def web(date_today):

    print("GENERATING WEBSITE DATA\n")
    # WEB DATA
    projections = pd.read_csv("output/raw_predictions/raw_predictions_" + date_today + ".csv")
    census = pd.read_csv("data/census/census.csv")
    projections = projections[projections['FIPS'].groupby(projections['FIPS']).transform('size')>4]
    past = projections.groupby("FIPS").tail(4).reset_index(drop=True)
    projections = projections.groupby("FIPS").tail(1).reset_index(drop=True)
    df_population = pd.read_csv('data/census/Reichlab_Population.csv',\
                                usecols=['location', 'population'])
    df_population['location'] = df_population['location'].astype('str')
    df_population['location'] = df_population['location'].str.zfill(5)
    df_population = df_population.rename(columns={'location':'FIPS'})

    projections = projections[['FIPS', 'date', 'ID', 'model', 'ELDERLY_POP', 'BA_FEMALE', 'BA_MALE', 'H_FEMALE', 'H_MALE', 'POP_DENSITY', 'TOT_POP', 'fb_movement_change', 'point_1_weeks', 'point_2_weeks', 'point_3_weeks', 'point_4_weeks']].round(2).reset_index(drop=True)
    projections['combined_predictions'] = projections.iloc[:, 12:].values.tolist()
    projections = projections.drop(['point_1_weeks', 'point_2_weeks', 'point_3_weeks', 'point_4_weeks'], axis=1)
    projections = projections.explode('combined_predictions')
    projections['shift'] = [0, 7, 14, 21] * int(len(projections)/4)
    projections['shift'] = pd.to_timedelta(projections['shift'], unit='D')
    projections['date'] = pd.to_datetime(projections['date']) + projections['shift']
    projections['date'] = projections['date'].astype(str)
    projections = projections.drop(['shift'], axis=1)
    projections['type'] = ['projection'] * len(projections)
    projections = projections.reset_index(drop=True)

    # Use latest population data
    projections['FIPS'] = projections['FIPS'].astype('str')
    projections['FIPS'] = projections['FIPS'].str.zfill(5)
    projections = projections.merge(df_population, how='left', on='FIPS')
    projections['TOT_POP'] = projections['population']
    projections = projections.drop(['population'], 1)
    projections['FIPS'] = projections['FIPS'].astype('int')

    projections['cases'] = (projections['combined_predictions'] * projections['TOT_POP'] / 100000).astype(float).round(0)
    projections['TOT_H'] = (projections['H_FEMALE'] + projections['H_MALE'])
    projections['TOT_BA'] = (projections['BA_FEMALE'] + projections['BA_MALE'])
    projections['total_cases'] = projections.groupby("FIPS")['cases'].transform('sum')
    projections['total_cases_percent'] = projections['total_cases']/projections['TOT_POP'] * 100
    projections['total_cases_mean'] = [projections['total_cases_percent'].mean()] * len(projections)

    projections = projections[['FIPS', 'date', 'ID',  'cases', 'type', 'model', 'POP_DENSITY', 'TOT_H', 'TOT_BA', 'ELDERLY_POP', 'fb_movement_change','total_cases_percent', 'total_cases_mean']]

    past['shift'] = [-7, -7, -7, -7] * int(len(past)/4)
    past['shift'] = pd.to_timedelta(past['shift'], unit='D')
    past['date'] = pd.to_datetime(past['date']) + past['shift']
    past['date'] = past['date'].astype(str)
    past = past.drop(['shift'], axis=1)

    # Use latest population data
    past['FIPS'] = past['FIPS'].astype('str')
    past['FIPS'] = past['FIPS'].str.zfill(5)
    past = past.merge(df_population, how='left', on='FIPS')
    past['TOT_POP'] = past['population']
    past = past.drop(['population'], 1)
    past['FIPS'] = past['FIPS'].astype('int')

    past['cases'] = (past['confirmed_cases_norm'] * past['TOT_POP'] / 100000).astype(float).round(0)
    past['TOT_H'] = (past['H_FEMALE'] + past['H_MALE'])
    past['TOT_BA'] = (past['BA_FEMALE'] + past['BA_MALE'])
    past['type'] = ['actual'] * len(past)
    past['total_cases'] = past.groupby("FIPS")['cases'].transform('sum')
    past['total_cases_percent'] = past['total_cases']/past['TOT_POP'] * 100
    past['total_cases_mean'] = [past['total_cases_percent'].mean()] * len(past)

    past = past[['FIPS', 'date', 'ID', 'cases', 'type', 'model', 'POP_DENSITY', 'TOT_H', 'TOT_BA', 'ELDERLY_POP', 'fb_movement_change', 'test_positivity', 'total_cases_percent', 'total_cases_mean']]

    rt = pd.read_csv("data/Rt/rt_data.csv", usecols=['FIPS','date','state_rt'])
    projections = pd.merge(left=projections, right=rt, how='left', on=['FIPS', 'date'], copy=False)
    projections['movement_mean'] = [projections.groupby("FIPS")['fb_movement_change'].take([0]).mean()] * len(projections)
    projections['rt_mean'] = [projections.groupby("FIPS")['state_rt'].take([0]).mean()] * len(projections)
    projections = projections.rename({'state_rt':'rt_mean_rt.live'}, axis=1)

    combined_web = pd.concat([past, projections], axis=0).sort_values(['FIPS','date']).reset_index(drop=True)

    combined_web.iloc[:, 6:] = combined_web.iloc[:, 6:].astype(float).round(3)
    combined_web = combined_web.fillna("NULL")
    combined_web = combined_web[['FIPS', 'date', 'ID', 'cases', 'type', 'model', 'POP_DENSITY', 'TOT_H', 'TOT_BA', 'ELDERLY_POP', 'fb_movement_change', 'test_positivity', 'rt_mean_rt.live', 'movement_mean', 'rt_mean', 'total_cases_percent', 'total_cases_mean']]
    combined_web.to_csv("output/website/web_latest.csv", index=False)

    # WEB JSON
    with open ("data/geodata/us-counties-topojson.json", "r") as myfile:
        data="".join(myfile.readlines())

    j = json.loads(data)

    df = pd.read_csv("output/website/web_latest.csv", dtype={"FIPS":str}).groupby("FIPS").tail(4).reset_index(drop=True)

    df = df[['FIPS', 'date', 'cases']]

    df['FIPS'] = df['FIPS'].apply(lambda x: "0" + x if len(x) < 5 else x)
    census = pd.read_csv("data/census/census.csv", dtype={'FIPS':str})[['FIPS', 'TOT_POP']]
    df = pd.merge(left=df, right=census, how='left', on=['FIPS'], copy=False)

    df['cases_p'] = (df['cases'] / df['TOT_POP'] * 7).round(5)
    df['cases'] = (df['cases'] * 7).round(0)
    df = df[['FIPS','date','cases', 'cases_p']]

    quantiles_ = df['cases_p'].quantile([0.8, 0.6, 0.4, 0.2]).tolist()

    imploded_df = df.groupby("FIPS").agg({'FIPS': lambda x: x.iloc[0], 'date': lambda x: x.tolist(), 'cases': lambda x: x.tolist(), 'cases_p': lambda x: x.tolist()}).reset_index(drop=True)

    imploded_df = imploded_df.set_index("FIPS")

    imploded_dict = imploded_df.T.to_dict("list")

    from collections import defaultdict

    present = 0
    tot_county = len(j['objects']['us-counties']['geometries'])
    for i in range(tot_county):
        county = j['objects']['us-counties']['geometries'][i]['id']
        if county in imploded_dict.keys():
            present += 1
            dates = imploded_dict[county][0]
            cases = imploded_dict[county][1]
            cases_p = imploded_dict[county][2]
            cases_dict = dict(zip(dates, cases))
            cases_p_dict = dict(zip(dates, cases_p))
            merged_dict = defaultdict(list)
            for d in (cases_dict, cases_p_dict): # you can list as many input dicts as you want here
                for key, value in d.items():
                    merged_dict[key].append(value)
            j['objects']['us-counties']['geometries'][i]['properties']['cases'] = merged_dict
        else:
            merged_dict = {"NULL0":[0, 0], "NULL1":[0, 0],"NULL2":[0, 0],"NULL3":[0, 0]}
            j['objects']['us-counties']['geometries'][i]['properties']['cases'] = merged_dict

        j['objects']['us-counties']['geometries'][i]['properties']['quantile'] = quantiles_

    with open('output/website/county-data.topojson', 'w') as f:
        f.write(json.dumps(j))

    # WEB MODEL STATISTICS
    df = pd.read_csv("output/model_stats/model_stats_" + date_today + ".csv").round(3)
    df.to_csv("output/website/model_stats_latest.csv", index=False)

    print('finished\n')
