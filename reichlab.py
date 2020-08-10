import numpy as np
import pandas as pd
from datetime import datetime, date
import os
import yaml

PREDICTION_FILE = 'predictions/projections/predictions_latest.csv'
CENSUS_PATH = 'data/census/census.csv'
PREDICTION_COLUMNS = ['FIPS', 'date', 'model_predictions']

def read_prediction():
    # Read CSV predictions and get the last date data
    df_predict = pd.read_csv(PREDICTION_FILE, usecols=PREDICTION_COLUMNS)
    df_census = pd.read_csv(CENSUS_PATH, usecols=['FIPS', 'TOT_POP'])
    df_predict = df_predict.groupby('FIPS').tail(1)

    # Write FIPS in 5-digit string format
    df_predict['FIPS'] = df_predict['FIPS'].astype('str')
    df_predict['FIPS'] = df_predict['FIPS'].str.zfill(5)
    df_predict = df_predict.reset_index(drop=True)
    df_census['FIPS'] = df_census['FIPS'].astype('str')
    df_census['FIPS'] = df_census['FIPS'].str.zfill(5)

    # Rename some columns
    df_predict = pd.merge(left=df_predict, right=df_census, how='left', on=['FIPS'], copy=False).sort_values(['FIPS', 'date']).reset_index(drop=True)
    df_predict = df_predict.rename(columns={'FIPS': 'location', 'date': 'forecast_date'})

    # Calculate estimated hospitalization from
    df_predict['TOT_POP'] = df_predict['TOT_POP'] / 100000
    df_predict['value'] = df_predict['model_predictions'] * df_predict['TOT_POP'] * 17

    df_predict = df_predict.drop(['TOT_POP', 'model_predictions'], 1)

    # Fix negative value bug and round number
    df_predict['value'] = df_predict['value'].mask(df_predict['value'] < 0, 0)
    df_predict['value'] = df_predict['value'].round().astype(int)

    # Calculate end date of the prediced period
    df_predict['target_end_date'] = pd.to_datetime(df_predict['forecast_date'])
    df_predict['target_end_date'] = df_predict['target_end_date'].apply(pd.DateOffset(14))
    df_predict['target_end_date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    # Add required columns for convention
    df_predict['target'] = '2 wk ahead inc case'
    df_predict['type'] = 'point'
    df_predict['quantile'] = 'NA'

    # Export data
    filename = df_predict['forecast_date'][0]

    if not os.path.exists('predictions/covid19-forecast-hub'):
        os.mkdir('predictions/covid19-forecast-hub')

    filepath = 'predictions/covid19-forecast-hub/' + filename + '-PandemicCentral-USCounty.csv'

    df_predict = df_predict[df_predict['forecast_date'] != '2020-07-20']
    df_predict['target_end_date'] = '2020-08-22'
    df_predict.to_csv(filepath, index=False)

    print(df_predict.head())

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
