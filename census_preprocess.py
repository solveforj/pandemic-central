"""
Run this module (in Python 2) to filter out the census data for 2010-2017 and
save as a new dataset.
"""

import pandas as pd

PATH = 'raw_data/census/census-2018.csv'
# Load census population demographics data
census = pd.read_csv('raw_data/census/cc-est2018.csv')

# Filter for a particular year
year = 2018
census = census[(census['YEAR'] == year - 2007)]

# Save into new csv_file
census.to_csv(PATH, index=False)
