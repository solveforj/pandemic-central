import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import pickle
from sklearn.metrics import r2_score


def align_rt(update=True, train=True):

    county_rt = pd.read_csv("data/Rt/rt_data.csv", dtype={"FIPS":str})

    case_data = pd.read_csv("data/JHU/jhu_data.csv", dtype={"FIPS":str})
    final = pd.merge(left=county_rt, right=case_data,how="left", on=['FIPS', 'date'], copy=False)

    testing_data = pd.read_csv("data/COVIDTracking/testing_data.csv", dtype={"FIPS":str})
    final = pd.merge(left=final, right=testing_data, how="left", on=['FIPS','date'], copy=False)

    final[['confirmed_cases_norm','confirmed_cases']] = final[['confirmed_cases_norm','confirmed_cases']].mask(final[['confirmed_cases_norm','confirmed_cases']] < 0, 0)

    final['normalized_cases_norm'] = (final['confirmed_cases_norm']/final['totalTestResultsIncrease_norm'])
    final['normalized_cases'] = (final['confirmed_cases']/final['totalTestResultsIncrease'])

    #print(final['normalized_cases_norm'].corr(final['normalized_cases']))
    county_counts = final.groupby("state", as_index=False).apply(lambda x : [len(x['FIPS'].unique())]*len(x))
    county_counts = county_counts.explode().reset_index(drop=True)
    final['county_counts'] = county_counts

    #final = final[(final['FIPS'].str.startswith("04")) | (final['FIPS'].str.startswith("05"))]
    print("Not null")
    print(final[~final['RtIndicator'].isnull()]['FIPS'].unique())
    print("Null")
    print(final[final['RtIndicator'].isnull()]['FIPS'].unique())
    #print(final[['FIPS', 'RtIndicator']])

    def get_optimal_lag(realtime, backlag, predict_shift):
        corrs = []
        for i in range(0,50):
            corrs.append(realtime.corr(backlag.shift(periods=i)))
        max_index = corrs.index(max(corrs))
        print(corrs[max_index], max_index)
        col1 = backlag.shift(periods=max_index - predict_shift).reset_index(drop=True)
        col2 = pd.Series([max_index] * len(col1))
        result = pd.concat([col1, col2], axis=1).reset_index(drop=True)
        return result

    def get_prediction(y, x, x_var, shift):
        X = np.array(x).reshape(-1,x_var)#[:-10,:]
        #print(X.shape)
        y = np.array(y).reshape(-1,1) #.shift(periods=-10).dropna()
        #print(y.shape)
        #print(y)
        poly = PolynomialFeatures(1)
        X = poly.fit_transform(X)
        regr = LinearRegression().fit(X, y)
        print(regr.score(X, y))
        #print(regr.predict(X))
        coefficients = regr.coef_
        intercept = regr.intercept_
        #print(np.dot(X[0], coefficients.reshape(-1, 1)) + intercept)
        #print("\n")
        return coefficients, intercept, shift.values.flatten()

    #def shift_rt(column, dictionary, item, fips, predict_shift):
    #    new_col = column.shift(periods=without_county_rt_dict[fips][2][item] - predict_shift)
    #    return new_col


    def shift_fraction(name, column, predict_shift):
        #print(column.tail(12))
        new_col = column.shift(periods = -1 * predict_shift).replace(0,0.0001)
        #print(new_col.tail(12))
        new_col = pd.concat([new_col.iloc[0:-21], new_col.iloc[-21:].interpolate(method='spline', order=1)], axis=0)
        #new_col = new_col.interpolate(method='spline', order=1)
        #print(new_col.tail(12))
        return new_col

    def make_prediction(fips, dictionary, x, x_var):
        #print(fips)
        index = x.index
        X = np.array(x).reshape(-1,x_var)
        poly = PolynomialFeatures(1)
        X = poly.fit_transform(X)
        coefficients = dictionary[fips][0]

        intercept = dictionary[fips][1]
        #print(coefficients, intercept)
        predictions = np.dot(X, coefficients.reshape(-1, 1)) + intercept
        output = pd.Series(predictions.flatten().tolist())
        #print(output)
        output.index = index.tolist()
        return output

    if update:
        print("Aligning and estimating county-level Rt")
        final_estimate = final[(final['date'] > "2020-03-18")]
        final_estimate = final_estimate[~final_estimate['normalized_cases_norm'].isnull()]
        new_col = final_estimate['test_positivity']/final_estimate['county_counts']
        final_estimate['county_fraction'] = final_estimate['normalized_cases_norm']/new_col.replace(0, 1)

        final_estimate = final_estimate.reset_index(drop=True)
        new_col = final_estimate.groupby("FIPS", as_index=False).apply(lambda x : get_optimal_lag(x['test_positivity'], x['rt_mean_MIT'], 0)).reset_index(drop=True)
        final_estimate[["aligned_state_rt","ECR_shift"]] = new_col

        final_estimate['estimated_county_rt'] = final_estimate['aligned_state_rt'] * final_estimate['county_fraction']
        final_estimate['estimated_county_rt'] = final_estimate['estimated_county_rt'] / (final_estimate['estimated_county_rt'].mean()/final_estimate['aligned_state_rt'])

        print("Aligning COVID Act Now county-level Rt")
        with_county_rt = final_estimate[~final_estimate['RtIndicator'].isnull()].dropna().reset_index(drop=True)
        final_estimate = final_estimate[final_estimate['RtIndicator'].isnull()]

        new_col = with_county_rt.groupby("FIPS", as_index=False).apply(lambda x : get_optimal_lag(x['normalized_cases'], x['RtIndicator'], 0)).reset_index(drop=True)
        with_county_rt[['CAN_county_rt','CAN_shift']] = new_col

        final_estimate = final_estimate[['FIPS', 'date', 'estimated_county_rt', 'normalized_cases_norm', 'ECR_shift']].dropna()
        with_county_rt_ = with_county_rt[['FIPS', 'date', 'estimated_county_rt', 'normalized_cases', 'normalized_cases_norm','ECR_shift', 'RtIndicator', 'CAN_county_rt', 'CAN_shift']].dropna()

        #print(with_county_rt_[with_county_rt_['FIPS'].isin(["04023", "04025", "04027"])])
        without_county_rt_ = final_estimate.groupby("FIPS").apply(lambda x : get_prediction(x['normalized_cases_norm'], x['estimated_county_rt'], 1, x['ECR_shift'].head(1))).to_dict()
        with_county_rt_ = with_county_rt_.groupby("FIPS").apply(lambda x : get_prediction(x['normalized_cases_norm'], x[['estimated_county_rt', 'CAN_county_rt']], 2, x[['ECR_shift','CAN_shift']].head(1))).to_dict()
        #with_county_rt_ = with_county_rt_.groupby("FIPS").apply(lambda x : get_prediction(x['normalized_cases_norm'], x['CAN_county_rt'], 1, x['CAN_shift'].head(1))).to_dict()

        print(with_county_rt_.keys())
        print(without_county_rt_.keys())
        pickle.dump(without_county_rt_, open("data/Rt/without_county_rt.p", "wb"))
        pickle.dump(with_county_rt_, open("data/Rt/with_county_rt.p", "wb"))

    if train:
        predict = 14
        print("Aligning and estimating county-level Rt")
        final_estimate = final[(final['date'] > "2020-03-18")]


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
        #print(final_estimate['FIPS'].unique())

        print("Aligning COVID Act Now county-level Rt")
        with_county_rt = final_estimate[~final_estimate['RtIndicator'].isnull()].dropna().reset_index()
        final_estimate = final_estimate[final_estimate['RtIndicator'].isnull()]

        #print(with_county_rt)

        new_col = with_county_rt.groupby("FIPS", as_index=False).apply(lambda x : get_optimal_lag(x['normalized_cases'], x['RtIndicator'], 0)).reset_index(drop=True)
        with_county_rt[['CAN_county_rt','CAN_shift']] = new_col

        final_estimate = final_estimate.reset_index(drop=True)

        without_county_rt_dict = pickle.load(open("data/Rt/without_county_rt.p", "rb"))
        with_county_rt_dict = pickle.load(open("data/Rt/with_county_rt.p", "rb"))

        #without_county_rt_dict = with_county_rt_
        #with_county_rt_dict = without_county_rt_

        final_estimate = final_estimate[['FIPS', 'date', 'estimated_county_rt', 'normalized_cases_norm', 'ECR_shift']].dropna()
        with_county_rt = with_county_rt[['FIPS', 'date', 'estimated_county_rt', 'normalized_cases_norm', 'RtIndicator','ECR_shift', 'CAN_county_rt', 'CAN_shift']].dropna()
        final_estimate = final_estimate[final_estimate['FIPS'].isin(without_county_rt_dict.keys())].reset_index(drop=True)
        with_county_rt = with_county_rt[with_county_rt['FIPS'].isin(with_county_rt_dict.keys())].reset_index(drop=True)
        new_col = final_estimate.groupby("FIPS", as_index=False).apply(lambda x : make_prediction(x.name, without_county_rt_dict, x['estimated_county_rt'], 1))
        #print(new_col.reset_index(drop=True))
        #print(final_estimate.shape)
        #print(final_estimate.index)
        final_estimate['prediction'] = new_col.reset_index(drop=True)
        #print(final_estimate)
        new_col = with_county_rt.groupby("FIPS", as_index=False).apply(lambda x : make_prediction(x.name, with_county_rt_dict, x[['estimated_county_rt', 'CAN_county_rt']], 2))
        with_county_rt['prediction'] = new_col.reset_index(drop=True)
        print(with_county_rt)

        #print(with_county_rt)
        #print(with_county_rt)
        #print(with_county_rt[['normalized_cases_norm', 'prediction']])
        #print(with_county_rt[with_county_rt['prediction'].isna()])
        print(with_county_rt['prediction'].corr(with_county_rt['normalized_cases_norm']))
        print(r2_score(with_county_rt['normalized_cases_norm'],with_county_rt['prediction']))

        #print(final_estimate)
        #print(final_estimate['FIPS'].unique())
        #print(final_estimate[['normalized_cases_norm', 'prediction']])
        #print(final_estimate)
        print(final_estimate['prediction'].corr(final_estimate['normalized_cases_norm']))
        print(r2_score(final_estimate['normalized_cases_norm'],final_estimate['prediction']))

        col_keep = ['FIPS', 'date', 'normalized_cases_norm', 'estimated_county_rt', 'prediction']
        combined = pd.concat([with_county_rt[col_keep], final_estimate[col_keep]])
        print(combined)
        final = final[['FIPS','date','state','region']]
        combined = pd.merge(left=combined, right=final, how='left', on=['FIPS', 'date'], copy=False)
        combined = combined[['FIPS','date','state','region','normalized_cases_norm','estimated_county_rt','prediction']]

        combined.to_csv("data/Rt/aligned_rt.csv", index=False)

if __name__ == "__main__":
    align_rt(update=False)
