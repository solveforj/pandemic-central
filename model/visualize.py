"""
Visualize quantile and point projections
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, date, timedelta

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
DATES = ['Week 1', 'Week 2', 'Week 3', 'Week 4']

def visualize():
    # Complete the list of important column headers
    for week in WEEKS:
        for quantile in QUANTILES:
            PREDICTION_COLUMNS.append(f'quantile_{quantile}_{week}_weeks')
        PREDICTION_COLUMNS.append(f'point_{week}_weeks')

    # Calculate date
    dates = [date.today().isoformat()]
    for i in range(3):
        dates.append((date.fromisoformat(dates[i])+timedelta(weeks=1)).isoformat())
    print(dates)

    # Read projections
    df_predict = pd.read_csv(PREDICTION_FILE, usecols=PREDICTION_COLUMNS)
    df_predict = df_predict.groupby('FIPS').tail(1).reset_index(drop=True)

    # Denormalize data
    for var in PREDICTION_COLUMNS[3:]:
        df_predict[var] = df_predict[var]*df_predict['TOT_POP']/100000

    points = []
    quantiles_0025 = []
    quantiles_0975 = []
    quantiles_01 = []
    quantiles_09 = []
    quantiles_025 = []
    quantiles_075 = []
    quantiles_05 = []

    for i in list(range(1,5)):
        points.append(df_predict[f'point_{str(i)}_weeks'].sum())
        quantiles_0025.append(df_predict[f'quantile_0.025_{str(i)}_weeks'].sum())
        quantiles_0975.append(df_predict[f'quantile_0.975_{str(i)}_weeks'].sum())
        quantiles_01.append(df_predict[f'quantile_0.1_{str(i)}_weeks'].sum())
        quantiles_09.append(df_predict[f'quantile_0.9_{str(i)}_weeks'].sum())
        quantiles_025.append(df_predict[f'quantile_0.25_{str(i)}_weeks'].sum())
        quantiles_075.append(df_predict[f'quantile_0.75_{str(i)}_weeks'].sum())
        quantiles_05.append(df_predict[f'quantile_0.5_{str(i)}_weeks'].sum())


    plt.plot(dates, points, label='point')
    plt.fill_between(dates, quantiles_0025, quantiles_0975, label='0.025-0.975', alpha=0.5)
    plt.fill_between(dates, quantiles_01, quantiles_09, label='0.1-0.9', alpha=0.5)
    plt.fill_between(dates, quantiles_025, quantiles_075, label='0.25-0.75', alpha=0.5)
    plt.legend()
    plt.suptitle('Pandemic Central - USCounty')
    plt.ylabel('Total incident cases in the US')
    plt.tight_layout()
    plt.show()

    # Export data
    df = pd.DataFrame({'date':dates,\
                        'quantile_0.025':quantiles_0025,\
                        'quantile_0.1':quantiles_01,\
                        'quantile_0.25':quantiles_025,\
                        'quantile_0.5':quantiles_05,\
                        'quantile_0.75':quantiles_075,\
                        'quantile_0.9':quantiles_09,\
                        'quantile_0.975':quantiles_0975,\
                        'point':points,\
                        })
    df.to_csv('predictions/web/quantiles_'+date.today().isoformat()+'.csv',\
                index=False)
    df.to_csv('predictions/web/quantiles_latest.csv',\
                index=False)


if __name__ == '__main__':
    visualize()
