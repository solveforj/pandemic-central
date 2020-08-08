import pandas as pd

from apple.preprocess import preprocess_apple
from CCVI.preprocess import preprocess_disparities
from census.preprocess import preprocess_census
from COVIDTracking.preprocess import preprocess_testing
from facebook.preprocess import preprocess_facebook
from google.preprocess import preprocess_google
from IHME.preprocess import preprocess_IHME
from JHU.preprocess import preprocess_JHU
from Rt.preprocess import preprocess_Rt
from align_Rt import align_rt

# Update dynamic data
#preprocess_apple()
#preprocess_google()
#preprocess_facebook()
#preprocess_JHU()
#preprocess_Rt()
#preprocess_testing()


# Read datasets into memory
ccvi = pd.read_csv("data/CCVI/CCVI.csv")
census = pd.read_csv("data/census/census.csv")
testing = pd.read_csv("data/COVIDTracking/testing_data.csv")
fb_mobility = pd.read_csv("data/facebook/mobility.csv.gz")
g_mobility = pd.read_csv("data/google/mobility.csv.gz")
a_mobility = pd.read_csv("data/apple/mobility.csv.gz")
ihme = pd.read_csv("data/IHME/IHME.csv")
cases = pd.read_csv("data/JHU/jhu_data.csv")
rt = pd.read_csv("data/Rt/aligned_rt.csv")

merged_DF = pd.merge(left=rt, right=testing, how='left', on=['FIPS', 'date'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=cases, how='left', on=['FIPS', 'date'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=fb_mobility, how='left', on=['FIPS', 'date'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=ihme, how='left', on=['FIPS'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=ccvi, how='left', on=['FIPS'], copy=False)
merged_DF = pd.merge(left=merged_DF, right = smoking, how='left', on=['region', 'Location'], copy=False)
merged_DF = pd.merge(left=merged_DF, right=census, how='left', on=['FIPS'], copy=False).sort_values(['FIPS', 'date']).reset_index(drop=True)
