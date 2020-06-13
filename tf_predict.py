"""
This module loads processed and merged data into Pandas dataframe, and does all
the machine learning fancy stuffs. Wish myself luck.
"""

import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import csv
import os, sys
from preprocess import get_latest_file
from datetime import datetime, date

PATH = get_latest_file('merged')
FEATURES = ['rt_mean_MIT',\
    'google_mobility_7d', 'apple_mobility_7d', 'fb_movement_change']

mpl.rcParams['figure.figsize'] = (8, 6)
mpl.rcParams['axes.grid'] = False

def load_dataframe():
    df = pd.read_csv(PATH)
    # drop the rows with NaN value
    df = df.dropna(subset=['google_mobility_7d', 'apple_mobility_7d'])
    # list of unique FIPS codes and dates
    fips_list = df['FIPS'].unique()
    dates = df['date'].unique()
    # ideally, the number of recorded dates equals to the size of batches
    batch_size = len(dates)
    new_df = df[FEATURES] # load dataframe from list of features
    new_df.index = df['date'] # indexing by dates
    # Load dataframe into Tensorflow dataset
    dataset = tf.data.Dataset.from_tensor_slices((new_df.values, new_df.index))
    dataset = dataset.batch(batch_size, drop_remainder=True)
    for feat, targ in dataset.take(5):
        print ('Features: {}, Target: {}'.format(feat, targ))
    return dataset, batch_size

if __name__ == '__main__':
    df, batch_size = load_dataframe()
    print(df)
    #df.to_csv('demo.csv', index=False)
