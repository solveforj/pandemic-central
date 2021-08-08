"""
This module preprocesses Google Mobility Data.

Data source: https://www.google.com/covid19/mobility/
"""

import os, sys
import numpy as np
import pandas as pd
from datetime import datetime, date
import csv
import ast
import shutil
import requests
import json
from zipfile import ZipFile
from bs4 import BeautifulSoup

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'

GOOGLE_MOBILITY_URL = 'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'

def get_google_data():
    url = \
        'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'
    df_google = pd.read_csv(url,
                            low_memory=False,
                            usecols=['census_fips_code', 'date', 'workplaces_percent_change_from_baseline'])
    df_google.dropna(subset=['census_fips_code'], inplace=True)
    df_google.rename(columns={'census_fips_code':'FIPS',
                            'workplaces_percent_change_from_baseline': 'workplaces_change'},
                            inplace=True)
    df_google['workplaces_change'].interpolate(inplace=True)
    df_google['workplaces_change'] /= 100
    df_google.to_csv('data/google/mobility.csv.xz', index=False)
    del df_google

if __name__ == "__main__":
    get_google_data()
