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
    quantiles = [0.025,0.1,0.25,0.5,0.75,0.9,0.975]

    prediction_df = pd.DataFrame()
    model_stats = pd.DataFrame()

    week_number = []
    model_type = []
    r2_training = []
    r2_testing = []
    mae_training = []
    mae_testing = []

    for shift in range(1, 5):

        week_number.append(shift)
        model_type.append(output)

        data_train = data.copy()

        data_train['label'] = data_train.groupby('FIPS')['confirmed_cases_norm'].shift(periods=-7*shift)
        #print(data['confirmed_cases_norm'].corr(data['prediction_aligned_int_7']))
        data_train = data_train.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)
        rt_compare = data_train['prediction_aligned_int_' + str(7*shift)] * data_train['totalTestResultsIncrease_norm']
        to_drop = ['confirmed_cases', 'confirmed_cases_norm', 'normalized_cases_norm', 'positiveIncrease_norm', 'positiveIncrease', 'TOT_POP']
        data_mod = data_train.drop(to_drop, axis=1)


        X = data_mod[data_mod.columns[3:-1]]

        scaler = StandardScaler()
        nX = scaler.fit_transform(X)
        y = data_mod['label']
        X_train, X_test, y_train, y_test = train_test_split(nX, y, train_size=0.9)
        regr = RandomForestRegressor(n_estimators=20, min_samples_split=10, n_jobs=-1).fit(X_train, y_train)

        r2_test = regr.score(X_test, y_test)
        print(r2_test)
        r2_testing.append(r2_test)
        r2_train = regr.score(X_train, y_train)
        print(r2_train)
        print()
        r2_training.append(r2_train)
        mae_test = mean_absolute_error(y_test,regr.predict(X_test))
        mae_testing.append(mae_test)
        mae_train = mean_absolute_error(y_train,regr.predict(X_train))
        mae_training.append(mae_train)

        print("Overall MAE")
        print(mean_absolute_error(y, regr.predict(nX)))

        print("Rt MAE")
        print(mean_absolute_error(y, rt_compare))

        print()

        print("Relative feature importances:")
        n = pd.DataFrame()
        n['features'] = X.columns
        n['value'] = regr.feature_importances_
        print(n.sort_values('value'))

        data_predict = data.drop(to_drop, axis=1)
        nX = scaler.fit_transform(data_predict[data_predict.columns[3:]])

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
    data['model'] = [output] * len(data)

    data.to_csv(os.path.split(os.getcwd())[0] + "/" + output + "_full_predictions.csv.gz", index=False, compression='gzip')

    for i in range(len(model_type)):
        model_type[i] = model_type[i].replace('_',' ')

    model_stats['model_type'] = model_type
    model_stats['week'] = week_number
    model_stats['R2_testing'] = r2_testing
    model_stats['R2_training'] = r2_training
    model_stats['MAE_testing'] = mae_testing
    model_stats['MAE_training'] = mae_training
    model_stats = model_stats.round(3)
    print(model_stats)

    return model_stats


def train():
    print("TRAINING MODELS\n")

    print("• Training mobility model")
    training_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/training_mobility.csv.gz")
    #training_mobility = training_mobility[training_mobility['date'] < "2020-12-07"]
    #training_mobility = training_mobility[training_mobility['FIPS'].astype(str).str.startswith("36")]
    mobility_model_stats = make_ML_model(training_mobility, "mobility")
    print("  Finished\n")


    print("• Training non-mobility model")
    training_no_mobility = pd.read_csv(os.path.split(os.getcwd())[0] + "/training_no_mobility.csv.gz")
    #training_no_mobility = training_no_mobility[training_no_mobility['FIPS'].astype(str).str.startswith("36")]
    nonmobility_model_stats = make_ML_model(training_no_mobility, "no_mobility")
    print("  Finished\n")

    full_model_stats = pd.concat([mobility_model_stats, nonmobility_model_stats], axis=0)

    # Create directory (if it does not exist yet)
    if not os.path.exists('predictions'):
        os.mkdir('predictions')
    if not os.path.exists('predictions/model_stats'):
        os.mkdir('predictions/model_stats')

    full_model_stats.to_csv("predictions/model_stats/model_stats_" + date_today + ".csv", index=False)
    full_model_stats.to_csv("predictions/model_stats/model_stats_latest.csv", index=False)

if __name__ == '__main__':
    train()
