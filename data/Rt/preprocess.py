"""
This module preprocesses and calculates for county's Rt.

Data source: see README for more details
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import pickle
from sklearn.metrics import r2_score
import warnings

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District Of Columbia': 'DC',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

def get_state_fips():

    # Source: US census
    # Link: www.census.gov/geographies/reference-files/2017/demo/popest/2017-fips.html
    # File:  2017 State, County, Minor Civil Division, and Incorporated Place FIPS Codes
    # Note: .xslx file header was removed and sheet was exported to csv
    fips_data = pd.read_csv("data/geodata/all-geocodes-v2017.csv",encoding = "ISO-8859-1", dtype={'State Code (FIPS)': str, 'County Code (FIPS)': str})

    # Map 040 level fips code to state name in dictionary
    state_data = fips_data[fips_data['Summary Level'] == 40].copy(deep=True)
    state_data['state_abbrev'] = state_data['Area Name (including legal/statistical area description)'].apply(lambda x : us_state_abbrev[x])
    state_map = pd.Series(state_data['State Code (FIPS)'].values,index=state_data['state_abbrev']).to_dict()
    state_map['AS'] = "60"
    state_map['GU'] = "66"
    state_map['MP'] = "69"
    state_map['PR'] = "72"
    state_map['VI'] = "78"

    # Get all county fips codes
    fips_data = fips_data[fips_data['Summary Level'] == 50]
    fips_data.insert(0, 'FIPS', fips_data['State Code (FIPS)'] + fips_data['County Code (FIPS)'])
    fips_data = fips_data[['FIPS', 'State Code (FIPS)']]

    return state_map, fips_data

def align_rt(update=True, train=True):

    county_rt = pd.read_csv("data/Rt/rt_data.csv", dtype={"FIPS":str})

    case_data = pd.read_csv("data/JHU/jhu_data.csv", dtype={"FIPS":str})

    final = pd.merge(left=county_rt, right=case_data,how="left", on=['FIPS', 'date'], copy=False)

    testing_data = pd.read_csv("data/COVIDTracking/testing_data.csv", dtype={"FIPS":str})

    final = pd.merge(left=final, right=testing_data, how="left", on=['FIPS','date'], copy=False)

    final[['confirmed_cases_norm','confirmed_cases']] = final[['confirmed_cases_norm','confirmed_cases']].mask(final[['confirmed_cases_norm','confirmed_cases']] < 0, 0)

    final['normalized_cases_norm'] = (final['confirmed_cases_norm']/final['totalTestResultsIncrease_norm'])
    final['normalized_cases'] = (final['confirmed_cases']/final['totalTestResultsIncrease'])

    county_counts = final.groupby("state", as_index=False).apply(lambda x : [len(x['FIPS'].unique())]*len(x))
    county_counts = county_counts.explode().reset_index(drop=True)
    final['county_counts'] = county_counts

    #print("Not null")
    #print(final[~final['RtIndicator'].isnull()]['FIPS'].unique())
    #print("Null")
    #print(final[final['RtIndicator'].isnull()]['FIPS'].unique())

    def get_optimal_lag(realtime, backlag, predict_shift):
        corrs = []
        for i in range(0,50):
            corrs.append(realtime.corr(backlag.shift(periods=i)))
        max_index = corrs.index(max(corrs))
        #print(corrs[max_index], max_index)
        col1 = backlag.shift(periods=max_index - predict_shift).reset_index(drop=True)
        col2 = pd.Series([max_index] * len(col1))
        result = pd.concat([col1, col2], axis=1).reset_index(drop=True)
        return result

    def get_prediction(y, x, x_var, shift):
        X = np.array(x).reshape(-1,x_var)
        y = np.array(y).reshape(-1,1)
        poly = PolynomialFeatures(1)
        X = poly.fit_transform(X)
        regr = LinearRegression().fit(X, y)
        coefficients = regr.coef_
        intercept = regr.intercept_
        return coefficients, intercept, shift.values.flatten()

    def shift_fraction(name, column, predict_shift):
        new_col = column.shift(periods = -1 * predict_shift).replace(0,0.0001)
        new_col = pd.concat([new_col.iloc[0:-21], new_col.iloc[-21:].interpolate(method='spline', order=1)], axis=0)
        return new_col

    def make_prediction(fips, dictionary, x, x_var):
        index = x.index
        X = np.array(x).reshape(-1,x_var)
        poly = PolynomialFeatures(1)
        X = poly.fit_transform(X)
        coefficients = dictionary[fips][0]
        intercept = dictionary[fips][1]
        predictions = np.dot(X, coefficients.reshape(-1, 1)) + intercept
        output = pd.Series(predictions.flatten().tolist())
        output.index = index.tolist()
        return output

    if update:
        print("  Aligning and estimating county-level Rt")
        final_estimate = final[(final['date'] > "2020-03-18")]
        final_estimate = final_estimate[~final_estimate['normalized_cases_norm'].isnull()]
        new_col = final_estimate['test_positivity']/final_estimate['county_counts']
        final_estimate['county_fraction'] = final_estimate['normalized_cases_norm']/new_col.replace(0, 1)

        final_estimate = final_estimate.reset_index(drop=True)
        new_col = final_estimate.groupby("FIPS", as_index=False).apply(lambda x : get_optimal_lag(x['test_positivity'], x['rt_mean_MIT'], 0)).reset_index(drop=True)
        final_estimate[["aligned_state_rt","ECR_shift"]] = new_col

        final_estimate['estimated_county_rt'] = final_estimate['aligned_state_rt'] * final_estimate['county_fraction']
        final_estimate['estimated_county_rt'] = final_estimate['estimated_county_rt'] / (final_estimate['estimated_county_rt'].mean()/final_estimate['aligned_state_rt'])

        print("  Aligning COVID Act Now county-level Rt")
        with_county_rt = final_estimate[~final_estimate['RtIndicator'].isnull()].dropna().reset_index(drop=True)
        final_estimate = final_estimate[final_estimate['RtIndicator'].isnull()]

        new_col = with_county_rt.groupby("FIPS", as_index=False).apply(lambda x : get_optimal_lag(x['normalized_cases'], x['RtIndicator'], 0)).reset_index(drop=True)
        with_county_rt[['CAN_county_rt','CAN_shift']] = new_col

        final_estimate = final_estimate[['FIPS', 'date', 'estimated_county_rt', 'normalized_cases_norm', 'ECR_shift']].dropna()
        with_county_rt_ = with_county_rt[['FIPS', 'date', 'estimated_county_rt', 'normalized_cases', 'normalized_cases_norm','ECR_shift', 'RtIndicator', 'CAN_county_rt', 'CAN_shift']].dropna()

        without_county_rt_ = final_estimate.groupby("FIPS").apply(lambda x : get_prediction(x['normalized_cases_norm'], x['estimated_county_rt'], 1, x['ECR_shift'].head(1))).to_dict()
        with_county_rt_ = with_county_rt_.groupby("FIPS").apply(lambda x : get_prediction(x['normalized_cases_norm'], x[['estimated_county_rt', 'CAN_county_rt']], 2, x[['ECR_shift','CAN_shift']].head(1))).to_dict()

        #print(with_county_rt_.keys())
        #print(without_county_rt_.keys())
        pickle.dump(without_county_rt_, open("data/Rt/without_county_rt.p", "wb"))
        pickle.dump(with_county_rt_, open("data/Rt/with_county_rt.p", "wb"))

    if train:
        predict = 14
        print("  Aligning and estimating county-level Rt")
        final_estimate = final[(final['date'] > "2020-03-25")]

        final_estimate = final_estimate[~final_estimate['normalized_cases_norm'].isnull()]
        new_col = final_estimate['test_positivity']/final_estimate['county_counts']
        final_estimate['county_fraction'] = final_estimate['normalized_cases_norm']/new_col.replace(0, 1)

        final_estimate = final_estimate.reset_index(drop=True)

        new_col = final_estimate.groupby("FIPS", as_index=False).apply(lambda x : get_optimal_lag(x['test_positivity'], x['rt_mean_MIT'], predict)).reset_index(drop=True)
        final_estimate[["aligned_state_rt","ECR_shift"]] = new_col

        new_col = final_estimate.groupby("FIPS", as_index=False).apply(lambda x : shift_fraction(x.name, x['county_fraction'], predict))
        final_estimate['county_fraction'] = new_col.reset_index(drop=True)

        new_col = final_estimate.groupby("FIPS", as_index=False).apply(lambda x : shift_fraction(x.name, x['normalized_cases_norm'], predict))
        final_estimate['normalized_cases_norm'] = new_col.reset_index(drop=True)

        final_estimate['estimated_county_rt'] = final_estimate['aligned_state_rt'] * final_estimate['county_fraction']
        final_estimate['estimated_county_rt'] = final_estimate['estimated_county_rt'] / (final_estimate['estimated_county_rt'].mean()/final_estimate['aligned_state_rt'])

        print("  Aligning COVID Act Now county-level Rt")
        with_county_rt = final_estimate[~final_estimate['RtIndicator'].isnull()].dropna().reset_index()
        final_estimate = final_estimate[final_estimate['RtIndicator'].isnull()]

        new_col = with_county_rt.groupby("FIPS", as_index=False).apply(lambda x : get_optimal_lag(x['normalized_cases'], x['RtIndicator'], 0)).reset_index(drop=True)
        with_county_rt[['CAN_county_rt','CAN_shift']] = new_col

        final_estimate = final_estimate.reset_index(drop=True)

        without_county_rt_dict = pickle.load(open("data/Rt/without_county_rt.p", "rb"))
        with_county_rt_dict = pickle.load(open("data/Rt/with_county_rt.p", "rb"))

        final_estimate = final_estimate[['FIPS', 'date', 'estimated_county_rt', 'normalized_cases_norm', 'ECR_shift']].dropna()
        with_county_rt = with_county_rt[['FIPS', 'date', 'estimated_county_rt', 'normalized_cases_norm', 'RtIndicator','ECR_shift', 'CAN_county_rt', 'CAN_shift']].dropna()
        final_estimate = final_estimate[final_estimate['FIPS'].isin(without_county_rt_dict.keys())].reset_index(drop=True)
        with_county_rt = with_county_rt[with_county_rt['FIPS'].isin(with_county_rt_dict.keys())].reset_index(drop=True)
        new_col = final_estimate.groupby("FIPS", as_index=False).apply(lambda x : make_prediction(x.name, without_county_rt_dict, x['estimated_county_rt'], 1))

        final_estimate['prediction'] = new_col.reset_index(drop=True)

        new_col = with_county_rt.groupby("FIPS", as_index=False).apply(lambda x : make_prediction(x.name, with_county_rt_dict, x[['estimated_county_rt', 'CAN_county_rt']], 2))
        with_county_rt['prediction'] = new_col.reset_index(drop=True)

        #print(with_county_rt['prediction'].corr(with_county_rt['normalized_cases_norm']))
        #print(r2_score(with_county_rt['normalized_cases_norm'],with_county_rt['prediction']))

        #print(final_estimate['prediction'].corr(final_estimate['normalized_cases_norm']))
        #print(r2_score(final_estimate['normalized_cases_norm'],final_estimate['prediction']))

        col_keep = ['FIPS', 'date', 'normalized_cases_norm', 'estimated_county_rt', 'prediction']
        combined = pd.concat([with_county_rt[col_keep], final_estimate[col_keep]])
        final = final[['FIPS','date','state','region']]
        combined = pd.merge(left=combined, right=final, how='left', on=['FIPS', 'date'], copy=False)
        combined = combined[['FIPS','date','state','region','normalized_cases_norm','estimated_county_rt','prediction']]

        combined.to_csv("data/Rt/aligned_rt.csv", index=False)

def warning_suppressor(debug_mode=True):
    if not debug_mode:
        warnings.filterwarnings("ignore")

def preprocess_Rt():
    warning_suppressor(debug_mode=False) # Change it to show errors

    print("• Processing Rt Data")

    state_map, fips_data = get_state_fips()

    # Rt calculations from rt.live
    rt_data = pd.read_csv("https://d14wlfuexuxgcm.cloudfront.net/covid/rt.csv", usecols=['date', 'region', 'mean'])
    rt_data['state'] = rt_data['region'].apply(lambda x : state_map[x])

    date_list = rt_data['date'].unique()
    fips_list = fips_data['FIPS'].unique()

    df = pd.DataFrame()
    df['FIPS'] = fips_list
    df['date'] = [date_list]*len(fips_list)
    df = df.explode('date').reset_index(drop=True)
    df['state'] = df['FIPS'].apply(lambda x : x[0:2])

    # Rt calculations from covid19-projections.com
    projections = pd.read_csv("https://raw.githubusercontent.com/youyanggu/covid19_projections/master/projections/combined/latest_us.csv", usecols=['date', 'region', 'r_values_mean'])
    projections['datetime'] = pd.to_datetime(projections['date'])
    projections = projections[(projections['region'].notnull()) & (projections['datetime'] < pd.to_datetime('today'))]
    projections.insert(0, "state", projections['region'].apply(lambda x : state_map[x]))
    projections = projections.drop(['datetime', 'region'], axis=1).reset_index(drop=True)

    # Merge Rt values from both sources together
    merged_df = pd.merge(left=df, right=rt_data, how='left', on=['state', 'date'], copy=False)
    merged_df = merged_df[merged_df['region'].notnull()]
    merged_df = merged_df.rename({'mean':'rt_mean_rt.live'},axis=1)
    merged_df = pd.merge(left=merged_df, right=projections, on=['state', 'date'], copy=False)
    merged_df = merged_df.rename({'r_values_mean':'rt_mean_MIT'},axis=1)
    merged_df = merged_df.sort_values(['FIPS', 'state'])

    # Add county-level Rt values
    county_rt = pd.read_csv("https://data.covidactnow.org/latest/us/counties.WEAK_INTERVENTION.timeseries.csv", dtype={"fips": str}, \
        usecols=['date', 'fips', 'RtIndicator'])
    county_rt = county_rt.rename({'fips':'FIPS'}, axis=1)
    final_rt = pd.merge(left=merged_df, right=county_rt, how="left", on=['FIPS', 'date'], copy=False)
    final_rt = final_rt

    final_rt.to_csv("data/Rt/rt_data.csv", index=False, sep=',')

    align_rt()

    print("  Finished\n")



if __name__ == "__main__":
    warning_suppressor()
    preprocess_Rt()
