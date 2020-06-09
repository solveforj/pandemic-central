import pandas as pd
from preprocess import get_latest_file
import os
from datetime import date

MOBILITY_PATH = get_latest_file('7-days-mobility')
TIME = date.today().isoformat()
PATH = 'processed_data/merged/'

dst = PATH + TIME + '.csv'

testing_data = pd.read_csv("raw_data/testing_data/testing_data.csv", dtype={'FIPS':int}, usecols=['FIPS', 'date','positiveIncrease', 'totalTestResultsIncrease'])
rt_data = pd.read_csv("raw_data/rt_data/rt_data.csv", dtype={'FIPS':int}, usecols=['FIPS', 'date','r_values_mean', 'rt_mean_MIT'])
jhu_data = pd.read_csv("raw_data/jhu/jhu_data.csv", dtype={'FIPS':int})
health_data = pd.read_csv("raw_data/health_data/health_data.csv", dtype={'FIPS':int})
disparities_data = pd.read_csv("raw_data/disparities/disparities.csv", dtype={'FIPS':int})
census_data = pd.read_csv("raw_data/census/census-2018.csv", dtype={'FIPS':int})
mobility_data = pd.read_csv(MOBILITY_PATH, dtype={'fips':int}, usecols=['fips', 'date', 'google_mobility_7d','apple_mobility_7d'])
facebook_data = pd.read_csv("raw_data/facebook/facebook.csv", dtype={'FIPS':int})


merged_DF = pd.merge(left=rt_data, right=testing_data, how='left', on=['FIPS', 'date'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=jhu_data, how='left', on=['FIPS', 'date'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=mobility_data, how='left', left_on=['FIPS', 'date'], right_on=['fips', 'date'], copy=False)
merged_DF = merged_DF.drop(['fips'], 1)
merged_DF = pd.merge(left=merged_DF, right=facebook_data, how='left', left_on=['FIPS', 'date'], right_on=['FIPS', 'date'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=health_data, how='left', on=['FIPS'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=disparities_data, how='left', on=['FIPS'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=census_data, how='left', on=['FIPS'], copy=False).sort_values(['FIPS', 'date'])

print(MOBILITY_PATH)
print(merged_DF)
print(merged_DF.columns)

if os.path.exists(dst):
    os.remove(dst)

merged_DF.to_csv(dst, sep=',', index=False)
