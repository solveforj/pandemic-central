import pandas as pd
import os
import sys
sys.path.append(os.getcwd() + "/")
from data.apple.preprocess import preprocess_apple
from data.CCVI.preprocess import preprocess_disparities
from data.census.preprocess import preprocess_census
from data.COVIDTracking.preprocess import preprocess_testing
from data.facebook.preprocess import preprocess_facebook
from data.google.preprocess import preprocess_google
from data.IHME.preprocess import preprocess_IHME
from data.JHU.preprocess import preprocess_JHU
from data.Rt.preprocess import preprocess_Rt

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'

# Update dynamic data
def update():
    print("UPDATING DATA\n")
    #preprocess_apple()
    #preprocess_google()
    preprocess_facebook()
    preprocess_JHU()
    preprocess_testing()
    preprocess_Rt()

# Read datasets into memory
def combine(apple_google_mobility = False):
    print("MERGING DATA\n")
    ccvi = pd.read_csv("data/CCVI/CCVI.csv")
    census = pd.read_csv("data/census/census.csv")
    testing = pd.read_csv("data/COVIDTracking/testing_data.csv.gz")
    fb_mobility = pd.read_csv("data/facebook/mobility.csv.gz")
    ihme = pd.read_csv("data/IHME/IHME.csv")
    #ihme_smoking = pd.read_csv("data/IHME/IHME_smoking.csv")
    cases = pd.read_csv("data/JHU/jhu_data.csv")

    # Read Rt datasets for all alignments
    rt = pd.read_csv("data/Rt/aligned_rt_7.csv")
    rt_14 = pd.read_csv("data/Rt/aligned_rt_14.csv", usecols=['FIPS', 'date', "prediction_aligned_int_14" , "rt_aligned_int_14"])
    rt_21 = pd.read_csv("data/Rt/aligned_rt_21.csv", usecols=['FIPS', 'date', "prediction_aligned_int_21" , "rt_aligned_int_21"])
    rt_28 = pd.read_csv("data/Rt/aligned_rt_28.csv", usecols=['FIPS', 'date', "prediction_aligned_int_28" , "rt_aligned_int_28"])

    # Merge all Rt datasets into one final
    rt = pd.merge(left=rt, right=rt_14, how='left', on=['FIPS', 'date'], copy=False)
    rt = pd.merge(left=rt, right=rt_21, how='left', on=['FIPS', 'date'], copy=False)
    rt = pd.merge(left=rt, right=rt_28, how='left', on=['FIPS', 'date'], copy=False)

    # Merge all datasets together
    merged_DF = pd.merge(left=rt, right=testing, how='left', on=['FIPS', 'date'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=cases, how='left', on=['FIPS', 'date'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=fb_mobility, how='left', on=['FIPS', 'date'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=ihme, how='left', on=['FIPS'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=ccvi, how='left', on=['FIPS'], copy=False)
    #merged_DF = pd.merge(left=merged_DF, right = ihme_smoking, how='left', on=['region', 'Location'], copy=False)
    merged_DF = pd.merge(left=merged_DF, right=census, how='left', on=['FIPS'], copy=False).sort_values(['FIPS', 'date']).reset_index(drop=True)

    if apple_google_mobility:
        g_mobility = pd.read_csv("data/google/mobility.csv.gz")
        a_mobility = pd.read_csv("data/apple/mobility.csv.gz")
        merged_DF = pd.merge(left=merged_DF, right=g_mobility, how='left', on=['FIPS', 'date'], copy=False)
        merged_DF = pd.merge(left=merged_DF, right=a_mobility, how='left', on=['FIPS', 'date'], copy=False)

    locations = merged_DF['Location']
    merged_DF = merged_DF.drop('Location', axis=1)

    merged_DF.insert(0, 'Location', locations)

    # Divide dataset into counties with and without mobility
    columns = merged_DF.columns.tolist()
    columns.remove('fb_stationary')
    columns.remove('fb_movement_change')

    #for i in merged_DF.columns:
    #    s = merged_DF[i]
    pd.set_option('display.max_rows', 500)

    s = merged_DF.isnull().sum(axis = 0)
    print(s)

    cleaned_DF = merged_DF.dropna(subset=columns)

    unused_DF = merged_DF[~merged_DF.index.isin(cleaned_DF.index)]

    training_mobility = cleaned_DF.dropna()
    training_mobility = training_mobility.sort_values(['FIPS', 'date'])

    print("Training Mobility")
    print(training_mobility.groupby("FIPS").tail(1)['date'])
    no_mobility = cleaned_DF[~cleaned_DF.index.isin(training_mobility.index)]
    no_mobility = no_mobility.drop(['fb_stationary', 'fb_movement_change'], axis=1)
    no_mobility = no_mobility.sort_values(['FIPS', 'date'])
    training_no_mobility = cleaned_DF.drop(['fb_stationary', 'fb_movement_change'], axis=1)

    # Save datasets
    unused_DF.to_csv(os.path.split(os.getcwd())[0] + "/unused_data.csv.gz", index=False, compression='gzip')
    training_mobility.to_csv(os.path.split(os.getcwd())[0] + "/training_mobility.csv.gz", index=False, compression='gzip')
    training_no_mobility.to_csv(os.path.split(os.getcwd())[0] + "/training_no_mobility.csv.gz", index=False, compression='gzip')
    print("  Finished!\n")

def merge(apple_google_mobility=False):
    if apple_google_mobility:
        update()
        combine(apple_google_mobility=True)
    if not apple_google_mobility:
        update()
        combine()

if __name__ == "__main__":
    merge()
