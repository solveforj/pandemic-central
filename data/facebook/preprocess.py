"""
This module preprocesses Facebook Mobility Data.

Data source: https://data.humdata.org/dataset/movement-range-maps
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
__version__ = '2.0.0'
__status__ = 'beta'
__url__ = 'https://github.com/solveforj/pandemic-central'

# DOWNLOAD
def get_facebook_data():
    url = 'https://data.humdata.org/dataset/movement-range-maps'
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')
    download_url = soup.find_all('a',\
        {"class": "btn btn-empty btn-empty-blue hdx-btn resource-url-analytics ga-download"},\
         href=True)[0]['href']
    download_url = 'https://data.humdata.org' + download_url

    zip = requests.get(download_url)
    os.mkdir('temp')
    temp_path = ('temp/data.zip')
    with open(temp_path, 'wb') as temp:
        temp.write(zip.content)
    with ZipFile(temp_path, 'r') as unzip:
        unzip.extractall('temp/')
    files = os.listdir('temp')

    return files


# PROCESS
def facebook_mobility_to_pd(files):
    for filename in files:
        if filename.startswith('movement-range'):
            path = 'temp/' + filename
    # Read and compress data file
    df_load = pd.read_csv(path, sep='\t', dtype={'polygon_id':str})
    df_load = df_load[df_load['country'] == 'USA']
    final = 'data/facebook/mobility.csv.gz'
    df_load.to_csv(final, compression='gzip', index=False)

    for filename in files:
        os.remove('temp/' + filename)
    os.rmdir('temp/')

def main():
    print('[ ] Process Facebook Mobility Data', end='\r')
    files = get_facebook_data()
    facebook_mobility_to_pd(files)
    print('[' + '+' + ']\n')
