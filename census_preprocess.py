"""
Run this module (in Python 2) to keep only the census data of 2018
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
