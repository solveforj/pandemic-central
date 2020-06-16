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
import seaborn as sns
import tensorflow_docs as tfdocs
import tensorflow_docs.plots
import tensorflow_docs.modeling

PATH = get_latest_file('merged')
FEATURES = ['rt_mean_MIT',\
    'google_mobility_7d', 'apple_mobility_7d', 'fb_movement_change']

mpl.rcParams['figure.figsize'] = (8, 6)
mpl.rcParams['axes.grid'] = False

def load_dataframe():
    df = pd.read_csv(PATH)
    # drop the rows with NaN value
    df = df.dropna(subset=['google_mobility_7d', 'apple_mobility_7d'])
    # Drop the counties with population density less than 100 people / sq mi
    df = df.loc[df['POP_DENSITY']>=100]
    # Filter out the necessary columns only
    df = df[['rt_mean_MIT',  'google_mobility_7d', 'apple_mobility_7d',\
        'fb_movement_change1']]

    # df.to_csv('demo.csv', index=False)

    train_dataset = df.sample(frac=0.8,random_state=0)
    test_dataset = df.drop(train_dataset.index)

    train_labels = train_dataset.pop('rt_mean_MIT')
    test_labels = test_dataset.pop('rt_mean_MIT')
    """
    # list of unique FIPS codes and dates
    fips_list = df['FIPS'].unique()
    dates = df['date'].unique()
    # ideally, the number of recorded dates equals to the size of batches
    batch_size = len(dates)
    new_df = df[FEATURES] # load dataframe from list of features
    new_df.index = df['date'] # indexing by dates
    # Load dataframe into Tensorflow dataset
    dataset = tf.data.Dataset.from_tensor_slices((new_df.values, new_df.index))
    dataset = dataset.batch(batch_size, drop_remainder=True) # simple batching
    return dataset, batch_size, test
    """
    return train_dataset, test_dataset, train_labels, test_labels

def build_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=[len(train_dataset.keys())]),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1)
      ])

    optimizer = tf.keras.optimizers.RMSprop(0.001)

    model.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mae', 'mse'])

    return model

def train_model(model, train_data, train_labels):
    EPOCHS = 1000
    history = model.fit(
      train_dataset, train_labels,
      epochs=EPOCHS, validation_split = 0.2, verbose=0,
      )

if __name__ == '__main__':
    train_dataset, test_dataset, train_labels, test_labels  = load_dataframe()
    model = build_model()
    print(model.summary())
    train_model(model, train_dataset, train_labels)

    """
    ds, _, test = load_dataframe()
    for feat, date in ds.take(5):
        print ('Features: {}, Date: {}'.format(feat, date))
    sns.pairplot(test.take[FEATURES], diag_kind="kde")
    """
    #df.to_csv('demo.csv', index=False)
