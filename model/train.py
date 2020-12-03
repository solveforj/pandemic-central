import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import os
from datetime import date
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'

date_today = date.today().strftime('%Y-%m-%d')
#date_today = "2020-08-22"

np.random.seed(1)
pd.set_option('display.max_columns', 500)


def make_ML_model(data, output, density = 0):
    data = data[data['POP_DENSITY'] >= density]
    data = data[data['date'] < date_today].reset_index(drop=True)
    data = data.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)
    quantiles = [0.01, 0.025, 0.05, 0.50, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975, 0.99]

    prediction_df = pd.DataFrame()

    for shift in range(1, 5):
        data_train = data.copy()

        data_train['label'] = data_train.groupby('FIPS')['confirmed_cases_norm'].shift(periods=-7*shift)
        to_drop = ['confirmed_cases', 'confirmed_cases_norm', 'normalized_cases_norm', 'positiveIncrease_norm', 'positiveIncrease', 'TOT_POP']
        data_train = data_train.drop(to_drop, axis=1)

        data_mod = data_train.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)
        X = data_mod[data_mod.columns[5:-1]]

        scaler = StandardScaler()
        nX = scaler.fit_transform(X)
        y = data_mod['label']
        X_train, X_test, y_train, y_test = train_test_split(nX, y, train_size=0.9)
        regr = RandomForestRegressor(n_estimators=20, min_samples_split=10, n_jobs=4).fit(X_train, y_train)

        print("R^2 Score on unseen data subset:")
        r2_test = regr.score(X_test, y_test)
        print(r2_test)

        print("R^2 Score on training data subset:")
        r2_train = regr.score(X_train, y_train)
        print(r2_train)

        print("Mean Absolute Error on unseen data subset:")
        mae_test = mean_absolute_error(y_test,regr.predict(X_test))
        print(mae_test)

        print("Mean Absolute Error on training data subset:")
        mae_train = mean_absolute_error(y_train,regr.predict(X_train))
        print(mae_train)

        print("Relative feature importances:")
        n = pd.DataFrame()
        n['features'] = X.columns
        n['value'] = regr.feature_importances_
        print(n.sort_values('value'))

        data_predict = data.drop(to_drop, axis=1)
        nX = scaler.fit_transform(data_predict[data_predict.columns[5:]])

        prediction_df['point_' + str(shift) + "_weeks"] = regr.predict(nX)

        pred_Q = pd.DataFrame()

        for pred in regr.estimators_:
            temp = pd.Series(pred.predict(nX).round(2))
            pred_Q = pd.concat([pred_Q, temp], axis=1)

        RF_actual_pred = pd.DataFrame()

        quantile_labels = []
        for q in quantiles:
            quantile_labels.append("quantile_" + str(q) + "_" + str(shift) + "_weeks")
            s = pred_Q.quantile(q=q, axis=1)
            RF_actual_pred = pd.concat([RF_actual_pred,s],axis=1,sort=False)

        RF_actual_pred.columns=quantile_labels
        prediction_df = pd.concat([prediction_df, RF_actual_pred], axis=1)

    data = pd.concat([data, prediction_df], axis=1)
    data.to_csv(os.path.split(os.getcwd())[0] + "/" + output + "_full_predictions.csv.gz", index=False, compression='gzip')

    return r2_test, r2_train, mae_test, mae_train


def train():
    print("TRAINING MODELS\n")

    print("• Training mobility model")
    training_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/training_mobility.csv.gz")
    training_mobility = training_mobility[training_mobility['FIPS'].astype(str).str.startswith("36")]
    m_r2_test, m_r2_train, m_mae_test, m_mae_train =  make_ML_model(training_mobility, "mobility")
    print("  Finished\n")

    print("• Training non-mobility model")
    training_no_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/training_no_mobility.csv.gz")
    n_r2_test, n_r2_train, n_mae_test, n_mae_train = make_ML_model(training_no_mobility, "no_mobility")
    print("  Finished\n")

    data_list = [["mobility",m_r2_train, m_mae_train, m_r2_test, m_mae_test], ["non-mobility",n_r2_train, n_mae_train, n_r2_test, n_mae_test]]
    modelstats = pd.DataFrame(data_list, columns=["mobility","trainingr2", "trainingmae", "testingr2", "testingmae"])
    modelstats.iloc[:, 1:] = modelstats.iloc[:, 1:].round(3)
    # Create directory (if it does not exist yet)
    if not os.path.exists('predictions'):
        os.mkdir('predictions')
    if not os.path.exists('predictions/model_stats'):
        os.mkdir('predictions/model_stats')

    modelstats.to_csv("predictions/model_stats/model_stats_" + date_today + ".csv", index=False)
    modelstats.to_csv("predictions/model_stats/model_stats_latest.csv", index=False)

if __name__ == '__main__':
    train()
