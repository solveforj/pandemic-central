"""
This module loads processed and merged data into Pandas dataframe, and does
predictions in Scikit-learn.
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
from sklearn.preprocessing import StandardScaler

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'released'
__url__ = 'https://github.com/solveforj/pandemic-central'

data = pd.read_csv("processed_data/merged/2020-06-19.csv")
print("Original number of FIPS")
print(len(set(data['FIPS'])))
diff = data.groupby('FIPS')['confirmed_cases'].shift(periods=-7)

data['label'] = diff

data_mobility = data.drop(['Location', 'google_mobility_7d','apple_mobility_7d'], axis=1)
data_mobility = data_mobility.replace([np.inf, -np.inf], np.nan)
print(len(data_mobility))
data_mobility = data_mobility.dropna()
print(len(data_mobility))


print("Number of FIPS with mobility")
print(len(set(data_mobility['FIPS'])))
X = data_mobility[data_mobility.columns[:-1]]
scaler = StandardScaler()
X = scaler.fit_transform(X.iloc[:,2:])
y = data_mobility['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1, train_size=0.9)
#regr = MLPRegressor(random_state=1, max_iter=1000).fit(X_train, y_train)
regr = RandomForestRegressor(random_state=1, n_estimators=10, n_jobs=4).fit(X_train, y_train)
print(regr.score(X_test, y_test))
#if os.path.exists:
#    os.mkdir("models")
pkl_filename = "models/sk-learn-model-rf-mobility.pkl"
with open(pkl_filename, 'wb') as file:
    pickle.dump(regr, file)

with open(pkl_filename, 'rb') as file:
    model = pickle.load(file)

nscaler = StandardScaler()
nX = scaler.fit_transform(data_mobility[data_mobility.columns[:-1]].iloc[:,2:])
data_mobility['predictions'] = model.predict(nX)
data_mobility.to_csv("models/sk-learn-predictions-mobility.csv", index=None, sep=",")




data_no_mobility = data.drop(['Location', 'google_mobility_7d','apple_mobility_7d', 'fb_movement_change','fb_stationary'], axis=1)
data_no_mobility = data_no_mobility[~data_no_mobility['FIPS'].isin(set(data_mobility['FIPS']))]
data_no_mobility = data_no_mobility.replace([np.inf, -np.inf], np.nan)
print(len(data_no_mobility))
data_no_mobility = data_no_mobility.dropna()
print(len(data_no_mobility))

print("Number of FIPS without mobility")
print(len(set(data_no_mobility['FIPS'])))
X = data_no_mobility[data_no_mobility.columns[:-1]]
scaler = StandardScaler()
X = scaler.fit_transform(X.iloc[:,2:])
y = data_no_mobility['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1, train_size=0.9)
#regr = MLPRegressor(random_state=1, max_iter=1000).fit(X_train, y_train)
regr = RandomForestRegressor(random_state=1, n_estimators=10, n_jobs=4).fit(X_train, y_train)
print(regr.score(X_test, y_test))
#if os.path.exists:
#    os.mkdir("models")
pkl_filename = "models/sk-learn-model-rf-no-mobility.pkl"
with open(pkl_filename, 'wb') as file:
    pickle.dump(regr, file)

with open(pkl_filename, 'rb') as file:
    model = pickle.load(file)

nscaler = StandardScaler()
nX = scaler.fit_transform(data_no_mobility[data_no_mobility.columns[:-1]].iloc[:,2:])
data_no_mobility['predictions'] = model.predict(nX)
data_no_mobility.to_csv("models/sk-learn-predictions-no-mobility.csv", index=None, sep=",")

original_fips = set(list(data['FIPS']))
data_fips = set(list(data_no_mobility['FIPS']) + list(data_mobility['FIPS']))
unused_fips = list(original_fips - data_fips)
unused_data = data[data['FIPS'].isin(unused_fips)]
unused_data.to_csv("models/sk-learn-unused-data.csv", index=None, sep=",",)
