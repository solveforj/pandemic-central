import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import pickle
import os
from datetime import date
from sklearn.preprocessing import StandardScaler

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'

def predict():
    print("MAKING PREDICTIONS\n")

    date_today = date.today().strftime('%Y-%m-%d')
    #date_today = "2020-08-22"

    mobility_data = pd.read_csv(os.path.split(os.getcwd())[0] + "/" + "mobility_full_predictions.csv.gz", dtype={"label":float})
    no_mobility_data = pd.read_csv(os.path.split(os.getcwd())[0] + "/" + "no_mobility_full_predictions.csv.gz",dtype={"label":float})

    latest_dates = list(range(((9*-7)-1), 6, 7))
    latest_mobility = mobility_data.groupby("FIPS", as_index=False).nth(latest_dates)
    latest_no_mobility = no_mobility_data.groupby("FIPS", as_index=False).nth(latest_dates)

    combined_predictions = latest_mobility.append(latest_no_mobility, ignore_index=True)
    combined_predictions = combined_predictions.sort_values(['FIPS', 'date', 'fb_movement_change'], na_position='first').groupby(['FIPS', 'date']).tail(1)
    combined_predictions = combined_predictions.groupby("FIPS").tail(10)

    combined_predictions['fb_movement_change'] = combined_predictions['fb_movement_change'].astype(float)
    combined_predictions['fb_stationary'] = combined_predictions['fb_stationary'].astype(float)
    combined_predictions = combined_predictions.round(3)

    id = combined_predictions['Location'] + ", " + combined_predictions['FIPS'].astype(str) + ", " + combined_predictions['region']
    combined_predictions.insert(0, 'ID', id)
    #combined_predictions = combined_predictions.fillna("NULL")
    #combined_predictions = combined_predictions.astype(str)

    # Fix bugs
    if not os.path.exists('predictions'):
        os.mkdir('predictions')
    if not os.path.exists('predictions/projections'):
        os.mkdir('predictions/projections')

    combined_predictions.iloc[:, 65:-1] = combined_predictions.iloc[:, 65:-1].astype(float)
    combined_predictions.iloc[:, 65:-1] = combined_predictions.iloc[:, 65:-1].clip(lower=0)

    print("Here are the latest dates for predictions of all counties:")
    print(combined_predictions.groupby("FIPS").tail(1)['date'].unique())
    #combined_predictions = combined_predictions.rename({"model_predictions":"model_predictions_norm"}, axis=1)

    combined_predictions.to_csv("predictions/projections/predictions_" + date_today + ".csv", index=False)
    combined_predictions.to_csv("predictions/projections/predictions_latest.csv", index=False)


    projections = pd.read_csv("predictions/projections/predictions_latest.csv")
    census = pd.read_csv("data/census/census.csv")

    past = projections.groupby("FIPS").tail(4).reset_index(drop=True)

    projections = projections.groupby("FIPS").tail(1).reset_index(drop=True)

    df_population = pd.read_csv('data/census/Reichlab_Population.csv',\
                                usecols=['location', 'population'])
    df_population['location'] = df_population['location'].astype('str')
    df_population['location'] = df_population['location'].str.zfill(5)
    df_population = df_population.rename(columns={'location':'FIPS'})

    projections = projections[['FIPS', 'date', 'ID', 'model', 'ELDERLY_POP', 'BA_FEMALE', 'BA_MALE', 'H_FEMALE', 'H_MALE', 'POP_DENSITY', 'TOT_POP', 'point_1_weeks', 'point_2_weeks', 'point_3_weeks', 'point_4_weeks']].round(2).reset_index(drop=True)
    projections['combined_predictions'] = projections.iloc[:, 11:].values.tolist()
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
    projections = projections[['FIPS', 'date', 'ID',  'cases', 'type', 'model', 'POP_DENSITY', 'TOT_H', 'TOT_BA', 'ELDERLY_POP']]

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

    past = past[['FIPS', 'date', 'ID', 'cases', 'type', 'model', 'POP_DENSITY', 'TOT_H', 'TOT_BA', 'ELDERLY_POP', 'fb_movement_change', 'test_positivity']]

    rt = pd.read_csv("data/Rt/rt_data.csv", usecols=['FIPS','date','rt_mean_rt.live'])
    past = pd.merge(left=past, right=rt, how='left', on=['FIPS', 'date'], copy=False)

    combined_web = pd.concat([past, projections], axis=0).sort_values(['FIPS','date']).reset_index(drop=True)
    combined_web.iloc[:, 6:] = combined_web.iloc[:, 6:].astype(float).round(3)
    combined_web = combined_web.round(3).fillna("NULL")

    combined_web.to_csv("predictions/website/web_" + date_today + ".csv", index=False)
    combined_web.to_csv("predictions/website/web_latest.csv", index=False)

    print("Finished\n")

if __name__ == "__main__":
    predict()
