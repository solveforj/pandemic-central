"""
This module loads processed and merged data into Pandas dataframe, and trains a
Random Forest Regression model in SciKit Learn
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import pickle
import os
from sklearn.preprocessing import StandardScaler
from generate_data import merge_data

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__version__ = '1.0.1'
__status__ = 'released'
__url__ = 'https://github.com/solveforj/pandemic-central'

def make_ML_model(data, output, density = 0):
    data['label'] = data.groupby('FIPS')['confirmed_cases'].shift(periods=-7)
    data = data[data['POP_DENSITY'] >= density]
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    X = data[data.columns[5:-2]]
    print(X.columns)
    scaler = StandardScaler()
    nX = scaler.fit_transform(X)
    y = data['label']
    X_train, X_test, y_train, y_test = train_test_split(nX, y, random_state=1, train_size=0.9)
    regr = RandomForestRegressor(random_state=1, n_estimators=10, n_jobs=4).fit(X_train, y_train)
    print("Accuracy on unseen data subset:")
    print(regr.score(X_test, y_test))
    print("Relative feature importances:")
    n = pd.DataFrame()
    n['features'] = X.columns
    n['value'] = regr.feature_importances_
    print(n.sort_values('value'))
    pkl_filename = os.path.split(os.getcwd())[0] + "/" + output +".pkl"
    with open(pkl_filename, 'wb') as file:
        pickle.dump(regr, file)

def main():
    training_mobility, training_no_mobility = merge_data(mode="training", save_files=True)

    print("Making mobility model")
    training_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/training_mobility.csv")
    make_ML_model(training_mobility, "mobility")

    print("Making non-mobility model")
    training_no_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/training_no_mobility.csv")
    make_ML_model(training_no_mobility, "no_mobility")

if __name__ == '__main__':
    main()
