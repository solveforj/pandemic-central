"""
This module loads processed and merged data into Pandas dataframe, and trains a
Random Forest Regression model in SciKit Learn
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import pickle
import os
from datetime import date
from sklearn.preprocessing import StandardScaler
from generate_data import merge_data
from sklearn.cluster import KMeans
from sklearn.metrics import mean_absolute_error

date_today = date.today().strftime('%Y-%m-%d')

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

    to_drop = ['Land Area', 'positiveIncrease','confirmed_cases','mortality_risk_25-45',\
     'mortality_risk_45-65', 'meningitis_mortality', 'mortality_risk_65-85', 'mortality_risk_5-25', 'mortality_risk_0-5', \
     'asthma_mortality', 'TOM_MALE', 'IA_FEMALE', 'IA_MALE', 'Female_Obesity_%', 'Housing Type & Transportation', \
     'other_resp_mortality', 'BA_FEMALE', 'coal_pneumoconiosis_mortality', 'diarrheal_mortality', \
     'interstitial_lung_mortality', 'COPD_mortality', 'other_pneumoconiosis_mortality', 'TOT_POP', 'TOM_FEMALE', 'H_FEMALE', 'lower_respiratory_mortality',\
      'Household Composition & Disability', 'pneumoconiosis_mortality', 'NA_FEMALE', 'Male_Obesity_%', 'chronic_respiratory_mortality', \
      'hepatitis_mortality', 'asbestosis_mortality', 'AIDS_mortality', 'silicosis_mortality']

    data_mod = data_train.drop(to_drop, axis=1)
    print(data_mod.columns)
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
    regr = RandomForestRegressor(n_estimators=20, n_jobs=4).fit(X_train, y_train)
    #regr = SVR().fit(X_train, y_train)
    #regr = MLPRegressor(random_state=1, max_iter=10000).fit(X_train, y_train)
    print("R^2 Score on unseen data subset:")
    r2_test = regr.score(X_test, y_test)
    print(r2_test)

    print("R^2 Score on training data subset:")
    r2_train = regr.score(X_train, y_train)
    print(r2_train)

    print("Mean Absolute Error on unseen data subset:")
    mae_test = mean_absolute_error(y_test,regr.predict(X_test))
    print(mae_test)

    print("Mean Absolute Error on unseen data subset:")
    mae_train = mean_absolute_error(y_train,regr.predict(X_train))
    print(mae_train)

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

    #pkl_filename = os.path.split(os.getcwd())[0] + "/" + output +".pkl"
    #with open(pkl_filename, 'wb') as file:
    #    pickle.dump(regr, file)
    return r2_test, r2_train, mae_test, mae_train

def main():


    print("Making mobility model")
    training_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/training_mobility.csv.gz")
    m_r2_test, m_r2_train, m_mae_test, m_mae_train =  make_ML_model(training_mobility, "mobility")

    print("Making non-mobility model")
    training_no_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/training_no_mobility.csv.gz")
    n_r2_test, n_r2_train, n_mae_test, n_mae_train = make_ML_model(training_no_mobility, "no_mobility")

    data_list = [["mobility",m_r2_train, m_mae_train, m_r2_test, m_mae_test], ["non-mobility",n_r2_train, n_mae_train, n_r2_test, n_mae_test]]
    modelstats = pd.DataFrame(data_list, columns=["mobility","trainingr2", "trainingmae", "testingr2", "testingmae"])
    modelstats.iloc[:, 1:] = modelstats.iloc[:, 1:].round(3)
    modelstats.to_csv("predictions/modelstats_" + date_today + ".csv", index=False)

if __name__ == '__main__':
    main()
