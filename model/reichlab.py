"""
This module processes output data into right format.
Processed data can be found at
"""

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
import os
import yaml
from isoweek import Week

PREDICTION_FILE = 'predictions/web/predictions_latest.csv'
PREDICTION_COLUMNS = ['FIPS', 'date', 'model_predictions']

# Require isoweek
def get_saturday(d):
    #
    # EPIWEEK ENDS ON SATURDAY
    # If the forecast date is Sunday or Monday, the first week will end on the
    # next Saturday. Otherwise, first week should end on the Saturday of the second
    # week.
    #
    date = d.isocalendar()
    if date[2] == 1:
        final = str(date[0]) + 'W' + str((date[1]))
        next_sat = Week.fromstring(final).saturday()
    else:
        final = str(date[0]) + 'W' + str((date[1] + 1))
        next_sat = Week.fromstring(final).saturday()
    return next_sat

def read_prediction():
    # Read CSV predictions and get the last date data
    #
    # In which:
    #   - 'model_predictions': prediction data for the week after next week
    #   - 'nextweek_predictions': predictions for the next closest week

    df_predict = pd.read_csv(PREDICTION_FILE, usecols=PREDICTION_COLUMNS)
    df_predict = df_predict.groupby('FIPS').tail(2).reset_index(drop=True)
    df_predict = df_predict.rename(columns={'model_predictions': 'value'})

    # Write FIPS in 5-digit string format
    df_predict['FIPS'] = df_predict['FIPS'].astype('str')
    df_predict['FIPS'] = df_predict['FIPS'].str.zfill(5)
    df_predict = df_predict.reset_index(drop=True)

    # Rename some columns
    df_predict = df_predict.rename(columns={'FIPS': 'location', 'date': 'forecast_date'})

    # 1st week from forecast date
    df_predict_1 = df_predict.groupby('location').head(1).reset_index(drop=True)
    df_predict_1['value'] = df_predict_1['value'] * 7
    # Calculate end date of the first week
    df_predict_1['target_end_date'] = pd.to_datetime(df_predict_1['forecast_date'])
    df_predict_1['target_end_date'] = get_saturday(pd.to_datetime(df_predict_1['forecast_date'])[0])
    df_predict_1['target'] = '1 wk ahead inc case'
    # Remove some counties with day lag
    latest = df_predict_1['forecast_date'].unique()[0]
    df_predict_1 = df_predict_1[df_predict_1['forecast_date'] == latest]

    # 2nd week from forecast date
    df_predict_2 = df_predict.groupby('location').tail(1).reset_index(drop=True)
    df_predict_2['value'] = df_predict_2['value'] * 7
    # Calculate end date of the second week
    df_predict_2['target_end_date'] = pd.to_datetime(df_predict_2['forecast_date'])
    df_predict_2['target_end_date'] = get_saturday(pd.to_datetime(df_predict_2['forecast_date'])[0])
    df_predict_2['target'] = '2 wk ahead inc case'
    # Remove some counties with day lag
    latest = df_predict_2['forecast_date'].unique()[0]
    df_predict_2 = df_predict_2[df_predict_2['forecast_date'] == latest]

    # Merge two datasets together
    df_predict = pd.concat([df_predict_1, df_predict_2], ignore_index=True, sort=False)
    df_predict = df_predict.sort_values(by=['location', 'target']).reset_index(drop=True)

    # Fix negative value bug and round number
    df_predict['value'] = df_predict['value'].mask(df_predict['value'] < 0, 0)
    df_predict['value'] = df_predict['value'].round().astype(int)

    # Add required columns for convention
    df_predict['type'] = 'point'
    df_predict['quantile'] = 'NA'

    latest = df_predict['forecast_date'].unique()[0]
    df_predict['forecast_date'] = latest

    # Export data
    filename = latest

    if not os.path.exists('predictions/covid19-forecast-hub'):
        os.mkdir('predictions/covid19-forecast-hub')

    filepath = 'predictions/covid19-forecast-hub/' + filename + '-PandemicCentral-USCounty.csv'
    df_predict.to_csv(filepath, index=False)

    print('Unique forecast date:', df_predict['forecast_date'].unique(), '\n')
    print('Unique end date:', df_predict['target_end_date'].unique(), '\n')
    print(df_predict.head(10))

def metadata():
    meta = {
        'team_name': 'Pandemic Central (itsonit.com)',
        'model_name': 'USCounty',
        'model_abbr': 'PandemicCentral-USCounty',
        'model_contributors': ['Joseph Galasso (University of Dallas) <jgalasso@udallas.edu>',
            'Duy Cao (University of Dallas) <caominhduy@gmail.com>'],
        'website_url': 'https://itsonit.com',
        'license': 'MIT',
        'team_model_designation': 'MIT',
        'data_inputs': ['Apple Mobility Trends', 'Google Mobility Reports', 'Facebook Movement Ranges',
          'CCVI', 'Census', 'COVIDTracking', 'IHME', 'JHU CSSEGISandData']
    }

if __name__ == '__main__':
    read_prediction()
