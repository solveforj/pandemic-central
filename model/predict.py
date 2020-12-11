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
    combined_predictions.iloc[:, 5:] = combined_predictions.iloc[:, 5:].round(3)

    id = combined_predictions['Location'] + ", " + combined_predictions['FIPS'].astype(str) + ", " + combined_predictions['region']
    combined_predictions.insert(0, 'ID', id)
    combined_predictions = combined_predictions.fillna("NULL")
    combined_predictions = combined_predictions.astype(str)

    # Fix bugs
    if not os.path.exists('predictions'):
        os.mkdir('predictions')
    if not os.path.exists('predictions/projections'):
        os.mkdir('predictions/projections')

    combined_predictions.iloc[:, 65:-1] = combined_predictions.iloc[:, 65:-1].astype(float)
    combined_predictions.iloc[:, 65:-1] = combined_predictions.iloc[:, 65:-1].clip(lower=0)

    print("Here are the latest dates for predictions of all counties")
    print(combined_predictions.groupby("FIPS").tail(1)['date'].unique())
    #combined_predictions = combined_predictions.rename({"model_predictions":"model_predictions_norm"}, axis=1)

    combined_predictions.to_csv("predictions/projections/predictions_" + date_today + ".csv", index=False)
    combined_predictions.to_csv("predictions/projections/predictions_latest.csv", index=False)
    print("Finished\n")


if __name__ == "__main__":
    predict()
