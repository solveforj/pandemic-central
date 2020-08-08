import pandas as pd

def preprocess_disparities():
    # Source: Surgo Foundation
    # Link: docs.google.com/spreadsheets/d/1bPdZz1YCYai1l35XL2CWdAS0gCjpss0FMiDGWERYPmA/edit#gid=1699059654
    # Note: Original csv was modified by simplifying header titles
    disparities = pd.read_csv("data/CCVI/CCVI_raw.csv", dtype={"FIPS":str})
    disparities = disparities[disparities.columns[3:-1]].sort_values('FIPS').reset_index(drop=True)
    disparities.to_csv("data/CCVI/CCVI.csv", index=False)

def main():
    print('• Processing CCVI Data')
    preprocess_disparities()
    print('  Finished\n')
main()
