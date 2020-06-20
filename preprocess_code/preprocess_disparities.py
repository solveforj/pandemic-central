import pandas as pd

disparities = pd.read_csv("raw_data/disparities/CCVI.csv", dtype={"FIPS":str})
disparities = disparities[disparities.columns[3:-2]].sort_values('FIPS').reset_index(drop=True)

disparities.to_csv("raw_data/disparities/disparities.csv", sep=",", index=False)
