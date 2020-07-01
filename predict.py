"""
This module performs predictions on recent data with Random Forest Regressors
from Scikit-learn.
"""

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
__version__ = '1.0.0'
__status__ = 'released'
__url__ = 'https://github.com/solveforj/pandemic-central'

date_today = date.today().strftime('%Y-%m-%d')

def timeseries(df, days, col):
    # dataframe must (1) have a 'FIPS' column and a date column
    df = df.sort_values(['FIPS', 'date'], axis=0, ascending=True)
    grouped_df = df.groupby(['FIPS']).tail(30)
    joined = grouped_df.groupby(['FIPS'])[col].apply(lambda x: ",".join(x.apply(str)))
    joined_df = pd.DataFrame(joined).reset_index(drop=True)
    joined_df.insert(0, 'FIPS', joined.index)
    joined_df = joined_df.rename({col:col+"_graph"}, axis=1)
    return joined_df


def make_predictions(data, output, model):
    with open(os.path.split(os.getcwd())[0] + "/" + model, 'rb') as file:
        model = pickle.load(file)
    data_mod = data.drop('confirmed_cases', axis=1)
    X = data_mod[data_mod.columns[5:-1]]
    scaler = StandardScaler()
    nX = scaler.fit_transform(X)
    data['prediction'] = model.predict(nX)
    file.close()
    return data

#latest_mobility, latest_no_mobility = merge_data(mode="predictions", save_files=True)
latest_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/latest_mobility.csv.gz")
latest_no_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/latest_no_mobility.csv.gz")
print("Making mobility predictions")
latest_mobility = make_predictions(latest_mobility, "latest_mobility", "mobility.pkl")

print("Making non-mobility predictions")
latest_no_mobility = make_predictions(latest_no_mobility, "latest_no_mobility", "no_mobility.pkl")

combined_predictions = latest_mobility.append(latest_no_mobility, ignore_index=True)
combined_predictions = combined_predictions.sort_values(['FIPS', 'date']).groupby(['FIPS']).tail(1)
print(combined_predictions)
#mobility_fips = set(latest_mobility['FIPS'].tolist())
#filtered_no_mobility = latest_no_mobility[~latest_no_mobility['FIPS'].isin(mobility_fips)]
#combined_predictions = latest_mobility.append(filtered_no_mobility, ignore_index=True)
combined_predictions.iloc[:, 5:] = combined_predictions.iloc[:, 5:].round(2)

id = combined_predictions['Location'] + ", " + combined_predictions['FIPS'].astype(str) + ", " + combined_predictions['region']
combined_predictions.insert(0, 'ID', id)
cases_data = pd.read_csv('data/jhu_data.csv')
cases_graph = timeseries(df=cases_data, days=30, col='confirmed_cases')
combined_predictions = pd.merge(left=combined_predictions, right=cases_graph, how='left', on='FIPS', copy=False)

combined_predictions.to_csv("predictions/full_predictions_" + date_today + ".csv", index=False)
