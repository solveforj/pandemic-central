"""
This module performs predictions on recent data with Random Forest Regressors
from Scikit-learn.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
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

def make_predictions(data, output, model):
    with open(os.path.split(os.getcwd())[0] + "/" + model, 'rb') as file:
        model = pickle.load(file)
    X = data[data.columns[5:-1]]
    scaler = StandardScaler()
    nX = scaler.fit_transform(X)
    data['prediction'] = model.predict(nX)
    data.to_csv("predictions/" + output + "_" + date_today + ".csv")
    file.close()
    return data

latest_mobility, latest_no_mobility = merge_data(mode="predictions", save_files=True)

print("Making mobility predictions")
latest_mobility = make_predictions(latest_mobility, "latest_mobility", "mobility.pkl")

print("Making non-mobility predictions")
latest_no_mobility = make_predictions(latest_no_mobility, "latest_no_mobility", "no_mobility.pkl")

mobility_fips = set(latest_mobility['FIPS'].tolist())
filtered_no_mobility = latest_no_mobility[~latest_no_mobility['FIPS'].isin(mobility_fips)]
combined_predictions = latest_mobility.append(filtered_no_mobility, ignore_index=True)

combined_predictions.to_csv("predictions/full_predictions_" + date_today + ".csv")
