"""
This module processes output data into right format.
Processed data can be found @ cdc.gov & Reichlab's GitHub repository
"""

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
import os
from isoweek import Week

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.1.0'

PREDICTION_FILE = 'predictions/projections/predictions_latest.csv'
PREDICTION_COLUMNS = ['FIPS', 'date', 'TOT_POP']
WEEKS = ['1', '2', '3', '4']
QUANTILES = ['0.025', '0.1', '0.25', '0.5', '0.75', '0.9', '0.975']

# Require package 'isoweek'
# try command 'pip install isoweek' or 'pip3 install isoweek'

def get_saturday(d):
    # EPIWEEK ENDS ON SATURDAY...
    # If the forecast date is Sunday or Monday, the first week will end on the
    # next Saturday. Otherwise, first week should end on the Saturday of the second
    # week.
    date = d.isocalendar()
    if date[2] <= 1:
        final = str(date[0]) + 'W' + str((date[1]))
        next_sat = Week.fromstring(final).saturday()
    else:
        final = str(date[0]) + 'W' + str((date[1] + 1))
        next_sat = Week.fromstring(final).saturday()
    return next_sat.isoformat()

def read_prediction():
    # Complete the list of important column headers
    for week in WEEKS:
        for quantile in QUANTILES:
            PREDICTION_COLUMNS.append(f'quantile_{quantile}_{week}_weeks')
        PREDICTION_COLUMNS.append(f'point_{week}_weeks')

    # Read projections
    df_predict = pd.read_csv(PREDICTION_FILE, usecols=PREDICTION_COLUMNS)
    df_predict = df_predict.groupby('FIPS').tail(1).reset_index(drop=True)

    # Set date of forecast
    df_predict = df_predict.drop(['date'], 1)

    # Write FIPS in 5-digit string format
    df_predict['FIPS'] = df_predict['FIPS'].astype('str')
    df_predict['FIPS'] = df_predict['FIPS'].str.zfill(5)
    df_predict = df_predict.rename(columns={'FIPS': 'location'})

    # Denormalize data
    df_population = pd.read_csv('data/census/Reichlab_Population.csv',\
                                usecols=['location', 'population'])

    df_population['location'] = df_population['location'].astype('str')
    df_population['location'] = df_population['location'].str.zfill(5)

    df_predict = df_predict.merge(df_population, how='left', on='location')
    df_predict['TOT_POP'] = df_predict['population']
    df_predict = df_predict.drop(['population'], 1)

    for var in PREDICTION_COLUMNS[3:]:
        df_predict[var] = df_predict[var]*df_predict['TOT_POP']*7/100000

    # List of values to be exploded
    df_predict['value'] = df_predict[PREDICTION_COLUMNS[3:]].values.tolist()

    # List of targets to be exploded
    targets = []
    for wk in WEEKS:
        targets = targets + [f'{wk} wk ahead inc case']*8
    df_predict['target'] = [targets] * len(df_predict)

    # List of types to be exploded
    types = ['quantile']*7+['point']
    types = types * len(WEEKS)
    df_predict['type'] = [types] * len(df_predict)

    # List of quantiles to be exploded
    quantiles_2 = ['0.025', '0.100', '0.250', '0.500', '0.750', '0.900', '0.975']
    df_predict['quantile'] = [(quantiles_2 + ['NA'])*len(WEEKS)] * len(df_predict)

    # List of end dates to be exploded
    ends = []
    for wk in range(0,4):
        ends = ends + [get_saturday(date.today() + timedelta(weeks=wk))]*8
    df_predict['target_end_date'] = [ends] * len(df_predict)

    # Drop all unnecessary columns
    df_predict = df_predict.drop(PREDICTION_COLUMNS[2:], 1)

    # EXPLODE
    df_predict = df_predict.set_index(['location']).apply(pd.Series.explode).reset_index()

    # Correct negative values
    df_predict['value'] = df_predict['value'].clip(lower=0)

    # Set 'forecast_date' to be the date today
    df_predict['forecast_date'] = date.today().isoformat()

    # Reorder columns
    df_predict = df_predict[['location', 'forecast_date', 'value', \
                            'target_end_date', 'target', 'type', 'quantile']]
    # Preview
    print(df_predict.head(20))

    # EXPORT DATA
    filename = date.today().isoformat()
    if not os.path.exists('predictions/covid19-forecast-hub'):
        os.mkdir('predictions/covid19-forecast-hub')
    filepath = 'predictions/covid19-forecast-hub/' + filename + '-PandemicCentral-USCounty.csv'
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
