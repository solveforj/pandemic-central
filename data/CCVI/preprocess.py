"""
This module preprocesses CCVI Index.

Data source: https://docs.google.com/spreadsheets/d/1qEPuziEpxj-VG11IAZoa5RWEr4GhNoxMn7aBdU76O5k/edit#gid=549685106
"""

import pandas as pd

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'

def preprocess_disparities():
    print('• Processing CCVI Data')

    # Source: Surgo Foundation
    # Link: docs.google.com/spreadsheets/d/1bPdZz1YCYai1l35XL2CWdAS0gCjpss0FMiDGWERYPmA/edit#gid=1699059654
    # Note: Original csv was modified by simplifying header titles
    disparities = pd.read_csv("data/CCVI/CCVI_raw.csv", dtype={"FIPS":str})
    disparities = disparities[disparities.columns[3:-1]].sort_values('FIPS').reset_index(drop=True)
    disparities.to_csv("data/CCVI/CCVI.csv", index=False)

    print('  Finished\n')

if __name__ == "__main__":
    preprocess_disparities()
