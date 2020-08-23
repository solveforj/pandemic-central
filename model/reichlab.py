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

# Epiweek ends on Saturday
def next_two_saturday(d):
    date = d.isocalendar()
    final = str(date[0]) + 'W' + str((date[1] + 2))
    next_sat = Week.fromstring(final).saturday()
    return next_sat

def read_prediction():
    # Read CSV predictions and get the last date data
    #
    # In which:
    #   - 'model_predictions': prediction data for the week after next week
    #   - 'nextweek_predictions': predictions for the next closest week

    df_predict = pd.read_csv(PREDICTION_FILE, usecols=PREDICTION_COLUMNS)
    df_predict_2 = df_predict.groupby('FIPS').tail(2)
    df_predict_2 = df_predict_2.groupby('FIPS').head(1).reset_index(drop=True)
    df_predict_2 = df_predict_2.rename(columns={'model_predictions': 'nextweek_predictions'})

    df_predict = df_predict.groupby('FIPS').tail(1)
    df_predict = df_predict.drop(['date'], 1).reset_index(drop=True)

    df_predict['date'] = df_predict_2['date']
    df_predict = df_predict.merge(right=df_predict_2, how='left', on=['FIPS', 'date'])

    # Write FIPS in 5-digit string format
    df_predict['FIPS'] = df_predict['FIPS'].astype('str')
    df_predict['FIPS'] = df_predict['FIPS'].str.zfill(5)
    df_predict = df_predict.reset_index(drop=True)

    # Rename some columns
    df_predict = df_predict.rename(columns={'FIPS': 'location', 'date': 'forecast_date'})

    # Calculate estimated new cases
    df_predict['value'] = df_predict['nextweek_predictions'] * 7
    df_predict['value'] = df_predict['value'] + df_predict['model_predictions'] * 7

    df_predict = df_predict.drop(['model_predictions', 'nextweek_predictions'], 1)

    # Fix negative value bug and round number
    df_predict['value'] = df_predict['value'].mask(df_predict['value'] < 0, 0)
    df_predict['value'] = df_predict['value'].round().astype(int)

    # Calculate end date of the prediced period
    df_predict['target_end_date'] = pd.to_datetime(df_predict['forecast_date'])
    df_predict['target_end_date'] = next_two_saturday(pd.to_datetime(df_predict['forecast_date'])[0])

    # Add required columns for convention
    df_predict['target'] = '2 wk ahead inc case'
    df_predict['type'] = 'point'
    df_predict['quantile'] = 'NA'

    # Export data
    filename = df_predict['forecast_date'][0]

    if not os.path.exists('predictions/covid19-forecast-hub'):
        os.mkdir('predictions/covid19-forecast-hub')

    filepath = 'predictions/covid19-forecast-hub/' + filename + '-PandemicCentral-USCounty.csv'
    print('Unique forecast date:', df_predict['forecast_date'].unique(), '\n')

    # Remove some counties with day lag
    latest = df_predict['forecast_date'].unique()[0]
    df_predict = df_predict[df_predict['forecast_date'] == latest]

    print(df_predict.head())

    print('\nProcessed final forecast date:', df_predict['forecast_date'].unique(), '\n')

    df_predict.to_csv(filepath, index=False)



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
