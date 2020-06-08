import pandas as pd

testing_data = pd.read_csv("raw_data/testing_data/testing_data.csv", dtype={'FIPS':int}, usecols=['FIPS', 'date','positiveIncrease', 'totalTestResultsIncrease'])
rt_data = pd.read_csv("raw_data/rt_data/rt_data.csv", dtype={'FIPS':int}, usecols=['FIPS', 'date','r_values_mean', 'rt_mean_MIT'])
jhu_data = pd.read_csv("raw_data/jhu/jhu_data.csv", dtype={'FIPS':int})
health_data = pd.read_csv("raw_data/health_data/health_data.csv", dtype={'FIPS':int})
disparities_data = pd.read_csv("raw_data/disparities/disparities.csv", dtype={'FIPS':int})
census_data = pd.read_csv("raw_data/census/census-2018.csv", dtype={'FIPS':int})
mobility_data = pd.read_csv("processed_data/7d-mobility-2020-06-07.csv", dtype={'FIPS':int}, usecols=['FIPS', 'date', 'google_mobility_7d','apple_mobility_7d'])

merged_DF = pd.merge(left=rt_data, right=testing_data, how='left', on=['FIPS', 'date'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=jhu_data, how='left', on=['FIPS', 'date'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=mobility_data, how='left', on=['FIPS', 'date'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=health_data, how='left', on=['FIPS'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=disparities_data, how='left', on=['FIPS'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=census_data, how='left', on=['FIPS'], copy=False).sort_values(['FIPS', 'date'])


print(merged_DF)
print(merged_DF.columns)

merged_DF.to_csv("merged_data/merged_data.csv", sep=',', index=False)
