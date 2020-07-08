"""
This module loads processed and merged data into Pandas dataframe, and trains a
Random Forest Regression model in SciKit Learn
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
import matplotlib.pyplot as plt
import pickle
import os
from sklearn.preprocessing import StandardScaler
from generate_data import merge_data
from sklearn.cluster import KMeans
from sklearn.metrics import mean_absolute_error

np.random.seed(1)

pd.set_option('display.max_columns', 500)
__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__version__ = '1.0.2'
__status__ = 'released'
__url__ = 'https://github.com/solveforj/pandemic-central'

def make_ML_model(data, output, density = 0):
    data['label'] = data.groupby('FIPS')['confirmed_cases'].shift(periods=-14)
    data = data[data['POP_DENSITY'] >= density]
    data_train = data.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)
    to_drop = ['Land Area', 'positiveIncrease', 'confirmed_cases']
    data_mod = data_train.drop(to_drop, axis=1)
    X = data_mod[data_mod.columns[5:-1]]
    scaler = StandardScaler()
    nX = scaler.fit_transform(X)
    y = data_mod['label']
    #nX = pd.DataFrame(scaler.fit_transform(X))
    #kmeans = KMeans(n_clusters=3, random_state=0).fit_predict(nX)
    #nX['kmeans'] = pd.Series(kmeans)
    #nX['label'] = data_mod['label']
    #nX = nX.groupby('kmeans').apply(lambda x: x.sample(30000))
    #y = nX['label']
    #nX = nX.drop(['kmeans', 'label'], axis=1)
    X_train, X_test, y_train, y_test = train_test_split(nX, y, train_size=0.9)
    regr = RandomForestRegressor(n_estimators=10, n_jobs=4).fit(X_train, y_train)
    #regr = MLPRegressor(random_state=1, max_iter=10000).fit(X_train, y_train)
    print("R^2 Score on unseen data subset:")
    print(regr.score(X_test, y_test))
    print("R^2 Score on training data subset:")
    print(regr.score(X_train, y_train))
    print("Mean Absolute Error on unseen data subset:")
    print(mean_absolute_error(y_test,regr.predict(X_test)))
    print("Mean Absolute Error on unseen data subset:")
    print(mean_absolute_error(y_train,regr.predict(X_train)))
    print("Relative feature importances:")
    n = pd.DataFrame()
    n['features'] = X.columns
    n['value'] = regr.feature_importances_
    print(n.sort_values('value'))
    data_predict = data.drop(to_drop, axis=1)
    nX = scaler.fit_transform(data_predict[data_predict.columns[5:-1]])
    data['model_predictions'] = regr.predict(nX)
    data = data.sort_values(['FIPS', 'date'])
    data.to_csv(os.path.split(os.getcwd())[0] + "/" + output + "_full_predictions.csv.gz", index=False, compression='gzip')
    latest = data.groupby('FIPS', as_index=False).nth([-29, -22, -15, -8, -1])
    latest.to_csv(os.path.split(os.getcwd())[0] + "/" + output + "_latest.csv.gz", index=False, compression='gzip')

    #pkl_filename = os.path.split(os.getcwd())[0] + "/" + output +".pkl"
    #with open(pkl_filename, 'wb') as file:
    #    pickle.dump(regr, file)

def main():

    print("Making mobility model")
    training_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/training_mobility.csv.gz")
    make_ML_model(training_mobility, "mobility")

    print("Making non-mobility model")
    training_no_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/training_no_mobility.csv.gz")
    make_ML_model(training_no_mobility, "no_mobility")

if __name__ == '__main__':
    main()
