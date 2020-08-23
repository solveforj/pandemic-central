import pandas as pd
import numpy as np
from scipy.stats.stats import pearsonr
from datetime import datetime
from os import listdir

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def calculate_mae(cumulative = True):

    dir_list = listdir("predictions/projections")

    start_date = datetime.strptime("2020-07-11", '%Y-%m-%d')
    use_dates = []

    for i in dir_list:
        date_string = i.split("_")[1].split(".")[0]
        if len(date_string) > 6:
            date_end = datetime.strptime(date_string, '%Y-%m-%d')
            delta = date_end - start_date
            if delta.days % 14 == 0:
                use_dates.append(i)

    use_dates.sort()

    case_data = pd.read_csv("data/JHU/jhu_data.csv")
    case_data = case_data[['FIPS','date','confirmed_cases_norm']]
    case_data['confirmed_cases_norm'] = case_data.groupby('FIPS')['confirmed_cases_norm'].shift(periods=-14)
    case_data = case_data.dropna().reset_index(drop=True)

    merged_cases = pd.DataFrame()

    if cumulative:
        use_dates = use_dates[:-1]
    else:
        use_dates = use_dates[-3:-1]

    for i in use_dates:
        tot_dir = "predictions/projections/" + i
        predictions = pd.read_csv(tot_dir)
        latest_predictions = predictions.groupby("FIPS").tail(2)[['ID','Location','FIPS','date','model_predictions']]
        latest_predictions = latest_predictions.reset_index(drop=True)
        merged_cases = pd.concat([merged_cases,latest_predictions], axis=0)

    merged_cases = merged_cases.sort_values(['FIPS', 'date'])
    merged_data = pd.merge(left=merged_cases, right=case_data, how='left', on=['FIPS', 'date'], copy=False)
    merged_data = merged_data.sort_values(['FIPS','date'])
    mae = np.abs(merged_data['model_predictions'] - merged_data['confirmed_cases_norm']).mean()
    corr = merged_data.groupby("FIPS").apply(lambda x : pearsonr(x['model_predictions'], x['confirmed_cases_norm'])[0])
    return mae, corr
