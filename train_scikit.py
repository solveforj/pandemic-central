import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
import matplotlib.pyplot as plt
import pickle
import os

data = pd.read_csv("processed_data/merged/2020-06-09.csv")

diff = data.groupby('FIPS')['confirmed_cases'].shift(periods=-7)
percent_change = diff

#print(percent_change)
data['label'] = percent_change
data = data.replace([np.inf, -np.inf], np.nan)
data = data.dropna()


print(data['Male_Obesity_%'].corr(data['label']))
#ax = data.boxplot(column=['label'])
#plt.show()


data = data.drop(['Location', 'fb_movement_change', 'fb_stationary'], axis=1)

data1 = data[data['POP_DENSITY'] > 300]
print(len(data1))
X = data1[data.columns[:-1]]
y = data1['label']
print(X.columns)

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1, train_size=0.9)
#regr = MLPRegressor(random_state=1, max_iter=1000).fit(X_train.iloc[:,2:], y_train)
regr = RandomForestRegressor(random_state=1, n_estimators=10, n_jobs=4).fit(X_train.iloc[:,2:], y_train)

print(regr.score(X_test.iloc[:,2:], y_test))

#if os.path.exists:
#    os.mkdir("models")


pkl_filename = "models/sk-learn-model-rf.pkl"
with open(pkl_filename, 'wb') as file:
    pickle.dump(regr, file)

with open(pkl_filename, 'rb') as file:
    model = pickle.load(file)

data1['predictions'] = model.predict(data1[data.columns[:-1]].iloc[:,2:])
data1.to_csv("models/sk-learn-predictions.csv", index=None, sep=",")
