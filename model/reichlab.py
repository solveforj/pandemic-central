import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
import os
from epiweeks import Week as epiweek

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

PREDICTION_COLUMNS = ['FIPS', 'date', 'TOT_POP']
WEEKS = ['1', '2', '3', '4']
QUANTILES = ['0.025', '0.1', '0.25', '0.5', '0.75', '0.9', '0.975']

meta_description = """
This model utilizes population mobility, demographics, and health data in combination with COVID-19 SEIR-generated projections and testing data \
as input into a random forest regression model to forecast COVID-19 cases for 1, 2, 3, and 4 weeks into the future for over 3000 U.S. counties \
and county equivalents.
"""

def get_saturday(d):
    # EPIWEEK ENDS ON SATURDAY...
    # If the forecast date is Sunday or Monday, the first week will end on the
    # next Saturday. Otherwise, first week should end on the Saturday of the second
    # week.

    if d.weekday() >= 1 and d.weekday() <=  5:
        d += timedelta(weeks=1)

    end_date = epiweek.fromdate(d).enddate().isoformat()

    return end_date

def reichlab(date_today):

    print("GENERATING COVID-19 FORECAST HUB DATA\n")

    PREDICTION_FILE = 'output/raw_predictions/raw_predictions_' + date_today + '.csv'
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
        df_predict[var] = df_predict[var]*df_predict['TOT_POP']/100000

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
        ends = ends + [get_saturday(date.fromisoformat(date_today) + timedelta(weeks=wk))]*8
    df_predict['target_end_date'] = [ends] * len(df_predict)

    # Drop all unnecessary columns
    df_predict = df_predict.drop(PREDICTION_COLUMNS[2:], 1)

    # EXPLODE
    df_predict = df_predict.set_index(['location']).apply(pd.Series.explode).reset_index()

    # Correct negative values
    df_predict['value'] = df_predict['value'].clip(lower=0)

    # Set 'forecast_date' to be the date today
    #df_predict['forecast_date'] = date.today().isoformat()
    df_predict['forecast_date'] = date_today

    # Reorder columns
    df_predict = df_predict[['location', 'forecast_date', 'value', \
                            'target_end_date', 'target', 'type', 'quantile']]
    # Preview
    #print(df_predict.head(5))

    # EXPORT DATA
    #filename = date.today().isoformat()
    filename = date_today
    df_predict.to_csv('output/ReichLabFormat/' + filename + '-PandemicCentral-COVIDForest.csv', index=False)

    print("  • Finished\n")
