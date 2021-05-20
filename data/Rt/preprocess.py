import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import pickle
from sklearn.metrics import r2_score
import warnings
from scipy.interpolate import interp1d
import numpy as np

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

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

def align_rt(county_rt):
    print("  • Loading input Rt, testing, and cases datasets")
    #county_rt = pd.read_csv("data/Rt/rt_data.csv", dtype={"FIPS":str})
    #county_rt = county_rt[~county_rt['RtIndicator'].isnull()]
    #county_rt['state_rt'] = county_rt['state_rt'].fillna(method='ffill')
    #print(county_rt)

    #print(len(county_rt[county_rt['FIPS'] == "01001"]))

    #print(county_rt.groupby("FIPS").tail(1)['date'].unique())

    case_data = pd.read_csv("data/JHU/jhu_data.csv", dtype={"FIPS":str})

    #print(case_data.groupby("FIPS").tail(1)['date'].unique())

    final = pd.merge(left=county_rt, right=case_data, how="left", on=['FIPS', 'date'], copy=False)

    #print(len(final[final['FIPS'] == "01001"]))
    #print(final.groupby("FIPS").tail(1)['date'].unique())

    testing_data = pd.read_csv("data/COVIDTracking/testing_data.csv.gz", dtype={"FIPS":str})

    #print(testing_data.groupby("FIPS").tail(1)['date'].unique())

    final = pd.merge(left=final, right=testing_data, how="left", on=['FIPS','date'], copy=False)
    #print(len(final[final['FIPS'] == "01001"]))
    #print(final.groupby("FIPS").tail(1)['date'].unique())

    final[['confirmed_cases_norm','confirmed_cases']] = final[['confirmed_cases_norm','confirmed_cases']].mask(final[['confirmed_cases_norm','confirmed_cases']] < 0, 0)

    final['normalized_cases_norm'] = (final['confirmed_cases_norm']/final['totalTestResultsIncrease_norm'])
    final['normalized_cases'] = (final['confirmed_cases']/final['totalTestResultsIncrease'])

    final = final.sort_values(["state", "FIPS"])
    county_counts = final.groupby("state", as_index=False).apply(lambda x: len(x['FIPS'].unique()))
    county_counts.columns = ["state", "unique_counties"]
    county_counts = county_counts['unique_counties'].to_list()

    state_counts = final.groupby("state", as_index=False).apply(lambda x: len(x['FIPS']))
    state_counts.columns = ['state','total_counties']
    state_counts = state_counts['total_counties'].to_list()

    ccounts = []
    for i in range(len(state_counts)):
        lst = [county_counts[i]]*state_counts[i]
        ccounts += lst

    final['county_counts'] = ccounts

    track_higher_corrs = {'FIPS':[], 'region':[], 'shift':[], 'correlation': []}

    #print(final.columns)
    #final = final[(final['FIPS'].str.startswith("04")) | (final['FIPS'].str.startswith("01"))]
    #print(len(final[final['FIPS'] == "01001"]))
    #print(final)

    #print("Latest Date")
    #print(final.sort_values('date').groupby("FIPS").tail(1)['date'].unique())

    def get_optimal_lag(realtime, backlag, predict_shift):
        corrs = []
        for i in range(0,75):
            corrs.append(realtime.corr(backlag.shift(periods=i)))
        max_index = corrs.index(max(corrs))
        col1 = backlag.shift(periods=max_index - predict_shift).reset_index(drop=True)
        col2 = pd.Series([max_index] * len(col1))
        col3 = pd.Series([max(corrs)] * len(col1))
        result = pd.concat([col1, col2, col3], axis=1).reset_index(drop=True)
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
        if predict_shift <= 14:
            new_col = pd.concat([new_col.iloc[0:-22], new_col.iloc[-22:].interpolate(method='spline', order=1)], axis=0)
        if predict_shift > 14:
            new_col = pd.concat([new_col.iloc[0:-20], new_col.iloc[-20:].interpolate(method='spline', order=1)], axis=0)
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

    def dual_shifter(col1, shift1, col2, shift2):
        if shift1 > shift2:
            print([shift2]*len(col2))
            return pd.concat([col1.shift(shift1-shift2).reset_index(drop=True), col2.reset_index(drop=True), pd.Series([shift2]*len(col2))], axis=1)
        else:
            print([shift1]*len(col2))
            return pd.concat([col1.reset_index(drop=True), col2.shift(shift2-shift1).reset_index(drop=True), pd.Series([shift1]*len(col1))], axis=1)

    def interpolator(col, col_name):
        if len(col.dropna()) == 0:
            return col

        num = -1*predict - 14
        interpolate_portion = col.iloc[num:]

        interpolate_portion = pd.concat([pd.Series(range(len(interpolate_portion))), interpolate_portion.reset_index(drop=True)], axis=1)

        train_col = interpolate_portion.dropna()
        f = np.poly1d(np.polyfit(train_col[0],train_col[col_name], 1))
        interpolate_portion[col_name] = interpolate_portion[col_name].fillna(interpolate_portion[0].apply(f))
        #interpolate_portion[col_name] = interpolate_portion[col_name].fillna(method='ffill')

        col_out = pd.concat([col.iloc[0:num], interpolate_portion[col_name]], axis=0)

        col_out.index = col.index
        return col_out

    def optimizer(name, col_a, shift_a, corr_a, col_b, shift_b, corr_b):
        corr_a = max(corr_a.fillna(0).tolist())
        corr_b = max(corr_b.fillna(0).tolist())
        shift_a = max(shift_a.fillna(0).tolist())
        shift_b = max(shift_b.fillna(0).tolist())

        track_higher_corrs['FIPS'].append(name)

        if corr_a >= corr_b:
            new_col = pd.concat([col_a.reset_index(drop=True), pd.Series([shift_a]*col_a.shape[0])], axis=1)
            new_col.columns = ['rt_final_unaligned', 'rt_final_shift']
            track_higher_corrs['region'].append('county')
            track_higher_corrs['shift'].append(new_col['rt_final_shift'].iloc[0])
            track_higher_corrs['correlation'].append(corr_a)
            return new_col
        else:
            new_col = pd.concat([col_b.reset_index(drop=True), pd.Series([shift_b]*col_b.shape[0])], axis=1)
            new_col.columns = ['rt_final_unaligned', 'rt_final_shift']
            track_higher_corrs['region'].append('state')
            track_higher_corrs['shift'].append(new_col['rt_final_shift'].iloc[0])
            track_higher_corrs['correlation'].append(corr_b)
            return new_col


    # Align the Rt.live Rt
    print("  • Calculating optimal Rt shifts")
    final_estimate = final[(final['date'] > "2020-03-30")]

    final_estimate = final_estimate[~final_estimate['normalized_cases_norm'].isnull()]
    final_estimate = final_estimate.reset_index(drop=True)

    #print(len(final_estimate[final_estimate['FIPS'] == "01001"]))

    # Align the Rt.live (state) Rt so that it is maximally correlated with test positivity by shifting it forward
    new_col = final_estimate.groupby("FIPS", as_index=False).apply(lambda x : get_optimal_lag(x['normalized_cases'], x['state_rt'], 0)).reset_index(drop=True)
    final_estimate[["aligned_state_rt","ECR_shift", "ECR_correlation"]] = new_col

    # Use the aligned state Rt to calculate an estimated county Rt that is also aligned
    #print("  Aligning COVID Act Now county-level Rt")

    # Find rows with a calculated and estimated county Rt
    with_county_rt = final_estimate[~final_estimate['RtIndicator'].isnull()].dropna().reset_index(drop=True)

    # Find rows with a estimated county Rt only
    without_county_rt = final_estimate[final_estimate['RtIndicator'].isnull()]

    # Align the COVID act now Rt so that it is maximally correlated with cases by shifting it forward
    new_col = with_county_rt.groupby("FIPS", as_index=False).apply(lambda x : get_optimal_lag(x['normalized_cases'], x['RtIndicator'], 0)).reset_index(drop=True)
    with_county_rt[['CAN_county_rt','CAN_shift', "CAN_correlation"]] = new_col

    # Drop NA values from each of the three dataframes
    without_county_rt = without_county_rt.replace([np.inf, -np.inf], np.nan)
    without_county_rt = without_county_rt[['FIPS', 'date', 'state_rt', 'normalized_cases_norm', 'confirmed_cases_norm', 'ECR_shift', 'ECR_correlation']].interpolate().dropna()

    with_county_rt = with_county_rt.replace([np.inf, -np.inf], np.nan)
    with_county_rt = with_county_rt[['FIPS', 'date', 'state_rt', 'aligned_state_rt', 'normalized_cases_norm','confirmed_cases_norm','ECR_shift', 'ECR_correlation', 'RtIndicator', 'CAN_county_rt', 'CAN_shift', 'CAN_correlation']].interpolate().dropna()

    final_estimate = final_estimate.replace([np.inf, -np.inf], np.nan)

    final_estimate = final_estimate[['FIPS', 'date', 'state_rt', 'aligned_state_rt', 'normalized_cases_norm', 'confirmed_cases_norm', 'ECR_shift', 'ECR_correlation']].interpolate().dropna()

    with_county_rt_merge = with_county_rt[['FIPS', 'date',  'CAN_county_rt', 'RtIndicator', 'CAN_shift', 'CAN_correlation']]

    merged = pd.merge(left=final_estimate, right=with_county_rt_merge, how='left', on=['FIPS', 'date'], copy=False)

    #print(len(merged[merged['FIPS'] == "01001"]))

    print("  • Computing case predictions from aligned Rt")

    merged = merged.reset_index(drop=True)
    new_col = merged.groupby("FIPS", as_index=False).apply(lambda x : optimizer(x.name, x['RtIndicator'], x['CAN_shift'], x['CAN_correlation'], x['state_rt'], x['ECR_shift'], x['ECR_correlation']))
    merged[['rt_final_unaligned', 'rt_final_shift']] = new_col.reset_index(drop=True)

    pd.DataFrame.from_dict(track_higher_corrs, orient='index').transpose().to_csv('data/Rt/higher_corrs.csv', index=False, sep=',')

    new_col = merged.groupby("FIPS", as_index=False).apply(lambda x : (x["rt_final_unaligned"].shift(int(x['rt_final_shift'].iloc[0]))))
    merged["rt_final_aligned"] = new_col.reset_index(drop=True)

    #print(len(merged))
    #print(merged[merged['FIPS'] == "01001"])
    merged_training = merged[(~merged['rt_final_aligned'].isnull())]
    #print(len(merged_training))

    prediction_dict = merged_training.groupby("FIPS").apply(lambda x : get_prediction(x['normalized_cases_norm'], x['rt_final_aligned'], 1, x['rt_final_shift'].head(1))).to_dict()

    merged_training = merged_training[~merged_training['rt_final_unaligned'].isnull()].reset_index(drop=True)

    new_col = merged_training.groupby("FIPS", as_index=False).apply(lambda x : make_prediction(x.name, prediction_dict, x['rt_final_unaligned'], 1))
    merged_training["prediction_unaligned"] = new_col.reset_index(drop=True)
    #print("Merged Training")
    #print(merged_training)

    #print(len(merged_training[merged_training['FIPS'] == "01001"]))

    shift_dates = [7, 14, 21, 28]

    for predict in shift_dates:
        print("  • Shifting case predictions and Rt for " + str(predict) + "-day forecasts")

        dat = merged_training.copy(deep=True)
        # Shift
        new_col = dat.groupby("FIPS", as_index=False).apply(lambda x : (x["prediction_unaligned"].shift(int(x['rt_final_shift'].unique()[0] - predict))))
        dat["prediction_aligned_" + str(predict)] = new_col.reset_index(drop=True)

        new_col = dat.groupby("FIPS", as_index=False).apply(lambda x : (x["rt_final_unaligned"].shift(int(x['rt_final_shift'].unique()[0] - predict))))
        dat["rt_aligned_" + str(predict)] = new_col.reset_index(drop=True)

        # Interpolate
        new_col = dat.groupby("FIPS", as_index=False).apply(lambda x : interpolator(x["prediction_aligned_" + str(predict)], "prediction_aligned_" + str(predict)))
        dat["prediction_aligned_int_" + str(predict)] = new_col.reset_index(drop=True).clip(lower=0)

        new_col = dat.groupby("FIPS", as_index=False).apply(lambda x : interpolator(x["rt_aligned_" + str(predict)], "rt_aligned_" + str(predict)))
        dat["rt_aligned_int_" + str(predict)] = new_col.reset_index(drop=True).clip(lower=0)

        # Correlate
        #print()
        #print(dat['normalized_cases_norm'].shift(-1*predict).corr(dat['prediction_aligned_int_'+str(predict)]))
        #print(dat['normalized_cases_norm'].shift(-1*predict).corr(dat['rt_aligned_int_'+str(predict)]))
        #print(dat.groupby("FIPS").tail(1)['date'].unique())
        #print()

        dat = dat[['FIPS', 'date','normalized_cases_norm', 'prediction_aligned_int_' + str(predict), 'rt_aligned_int_'+str(predict)]]
        #print(len(dat[dat['FIPS'] == "01001"]))
        dat.to_csv("data/Rt/aligned_rt_"+str(predict)+".csv", index=False, sep=',')

def warning_suppressor(debug_mode=True):
    if not debug_mode:
        warnings.filterwarnings("ignore")

def update_Rt(can_key):
    warning_suppressor(debug_mode=False) # Change it to show errors

    print("• Downloading Rt dataset")

    state_map, fips_data = get_state_fips()

    s_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
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

    # Rt calculations from rt.live
    rt_data = pd.read_csv("https://api.covidactnow.org/v2/states.timeseries.csv?apiKey=" + can_key, dtype={"fips": str}, \
        usecols=['date', 'fips', 'metrics.infectionRate'])
    rt_data = rt_data.rename({'fips':'state', 'metrics.infectionRate':'state_rt'}, axis=1)

    date_list = rt_data['date'].unique()
    fips_list = fips_data['FIPS'].unique()

    df = pd.DataFrame()
    df['FIPS'] = fips_list
    df['date'] = [date_list]*len(fips_list)
    df = df.explode('date').reset_index(drop=True)
    df['state'] = df['FIPS'].apply(lambda x : x[0:2])

    # Merge Rt values from both sources together
    merged_df = pd.merge(left=df, right=rt_data, how='left', on=['state', 'date'], copy=False)

    merged_df = merged_df[merged_df['state'].notnull()]
    merged_df = merged_df.sort_values(['FIPS', 'state'])

    # Add county-level Rt values
    county_rt = pd.read_csv("https://api.covidactnow.org/v2/counties.timeseries.csv?apiKey=" + can_key, dtype={"fips": str}, \
        usecols=['date', 'fips', 'metrics.infectionRate'])
    county_rt = county_rt.rename({'fips':'FIPS', 'metrics.infectionRate':'RtIndicator'}, axis=1)
    final_rt = pd.merge(left=merged_df, right=county_rt, how="left", on=['FIPS', 'date'], copy=False)

    # Only use counties that are non-errant
    fips_to_use = pd.read_csv("data/geodata/FIPS_used.csv", dtype={'FIPS': 'str'})['FIPS'].to_list()
    final_rt = final_rt[final_rt['FIPS'].isin(fips_to_use)]

    final_rt = final_rt.sort_values(['FIPS', 'date'])

    final_rt.to_csv("data/Rt/rt_data.csv", index=False, sep=',')

    print("  • Finished\n")

def preprocess_Rt(date, old):

    print("• Aligning Rt")

    if old:
        final_rt = pd.read_csv("data/Rt/rt_data_test.csv", dtype={"FIPS":"str"})
    else:
        final_rt = pd.read_csv("data/Rt/rt_data.csv", dtype={"FIPS":"str"})

    final_rt = final_rt[(final_rt['date'] <= date)]

    align_rt(final_rt)
    print("  • Finished\n")


if __name__ == "__main__":
    warning_suppressor()
    preprocess_Rt(date)
