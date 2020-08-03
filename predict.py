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
__version__ = '1.0.2'
__status__ = 'released'
__url__ = 'https://github.com/solveforj/pandemic-central'

date_today = date.today().strftime('%Y-%m-%d')

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

#latest_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/mobility_latest.csv.gz")
#latest_no_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/no_mobility_latest.csv.gz")

mobility_data = pd.read_csv(os.path.split(os.getcwd())[0] + "/" + "mobility_full_predictions.csv.gz", dtype={"label":float})
no_mobility_data = pd.read_csv(os.path.split(os.getcwd())[0] + "/" + "no_mobility_full_predictions.csv.gz",dtype={"label":float})

latest_dates = list(range(((9*-7)-1), 6, 7))
latest_mobility = mobility_data.groupby("FIPS", as_index=False).nth(latest_dates)
latest_no_mobility = no_mobility_data.groupby("FIPS", as_index=False).nth(latest_dates)




#print(latest_mobility[['Location', 'label', 'model_predictions', 'confirmed_cases']])

combined_predictions = latest_mobility.append(latest_no_mobility, ignore_index=True)
combined_predictions = combined_predictions.sort_values(['FIPS', 'date', 'fb_movement_change'], na_position='first').groupby(['FIPS', 'date']).tail(1)
combined_predictions = combined_predictions.groupby("FIPS").tail(10)


combined_predictions['fb_movement_change'] = combined_predictions['fb_movement_change'].astype(float)
combined_predictions['fb_stationary'] = combined_predictions['fb_stationary'].astype(float)
combined_predictions.iloc[:, 5:] = combined_predictions.iloc[:, 5:].round(3)

id = combined_predictions['Location'] + ", " + combined_predictions['FIPS'].astype(str) + ", " + combined_predictions['region']
combined_predictions.insert(0, 'ID', id)
combined_predictions = combined_predictions.fillna("NULL")
combined_predictions = combined_predictions.astype(str)

combined_predictions.to_csv("predictions/full_predictions_" + date_today + ".csv", index=False)

#combined_predictions = combined_predictions[['ID', 'FIPS','date', 'fb_movement_change', 'test_positivity',\
#'rt_mean_MIT', 'confirmed_cases','model_predictions','POP_DENSITY', 'ELDERLY_POP',\
#'BA_MALE', 'BA_FEMALE', 'H_MALE','H_FEMALE']]


#combined_predictions.to_csv(os.path.split(os.getcwd())[0] + "/" + date_today + "_webdata.csv", index=False)
