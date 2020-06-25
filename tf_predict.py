"""
This module loads processed and merged data into Pandas dataframe, and does
predictions in TensorFlow. THIS IS AN EXPERIMENT MODULE.
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

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__version__ = '1.0.1'
__status__ = 'developing'
__url__ = 'https://github.com/solveforj/pandemic-central'

FEATURES = ['confirmed_cases', 'apple_mobility_7d', 'google_mobility_7d',\
    'fb_movement_change', 'asbestosis_mortality', 'pneumoconiosis_mortality',\
    'diarrheal_mortality', 'other_pneumoconiosis_mortality',\
    'silicosis_mortality', 'COPD_mortality', 'chronic_respiratory_mortality',\
    'interstitial_lung_mortality', 'other_resp_mortality', 'POP_DENSITY']
FEATURE_COLS = FEATURES[1:]
LABEL = 'confirmed_cases'
MIN_POP = 500
N_BATCH = 1
EPOCHS = 1000

mpl.rcParams['figure.figsize'] = (8, 6)
mpl.rcParams['axes.grid'] = False

def main():
    path = get_latest_file('merged')
    df = pd.read_csv(path, compression='gzip')
    df['confirmed_cases'] = df.groupby('FIPS')['confirmed_cases'].shift(periods=-7)
    # drop the rows with NaN value
    df = df.dropna()
    # Drop the counties with population density less than MIN_POP people / sq mi
    df = df.loc[df['POP_DENSITY']>=MIN_POP]
    # Filter out the necessary columns only
    df = df[FEATURES]
    # Split the dataset into train and test
    train_dataset = df.sample(frac=0.8,random_state=0)
    test_dataset = df.drop(train_dataset.index)
    #train_dataset, test_dataset = np.split(df, [int(.9*len(df))])
    # Visualize correlation by graphing
    #pair_plot = sns.pairplot((train_dataset), diag_kind="kde")
    #heatmap = sns.heatmap(train_dataset.corr(), annot=True)
    #plt.show()
    # For data normalization
    train_stats = train_dataset.describe()
    train_stats.pop(LABEL)
    train_stats = train_stats.transpose()
    test_stats = test_dataset.describe()
    test_stats.pop(LABEL)
    test_stats = test_stats.transpose()

    # Pop out train and eval labels
    train_labels = train_dataset.pop(LABEL)
    test_labels = test_dataset.pop(LABEL)

    # Normalize data
    normed_train_data = (train_dataset - train_stats['mean']) / train_stats['std']
    normed_test_data = (test_dataset - test_stats['mean']) / test_stats['std']

    # Model
    def build_model():
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=[len(train_dataset.keys())]),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1)
          ])
        optimizer = tf.keras.optimizers.RMSprop(learning_rate=0.001)
        model.compile(loss='mae', optimizer=optimizer, metrics=['mae', 'mse', 'mape'])
        return model

    model = build_model()
    print(model.summary())

    # Train
    early_stop_callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', \
        patience=70, mode='min')

    if not os.path.exists('models'):
        os.mkdir('models')
    if not os.path.exists('models/tensorflow'):
        os.mkdir('models/tensorflow')
    checkpoint_path = 'models/tensorflow/' + datetime.now().strftime('%Y%m%d%H%S')
    if not os.path.exists(checkpoint_path):
        os.mkdir(checkpoint_path)
    checkpoint_path = checkpoint_path + '/checkpoint'

    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,\
        save_weights_only=True, verbose=0)

    history = model.fit(
      normed_train_data, train_labels,
      epochs=EPOCHS, validation_split = 0.1, verbose=1, shuffle=True,
      callbacks=[early_stop_callback, checkpoint_callback])

    # Evaluate
    plotter = tfdocs.plots.HistoryPlotter(smoothing_std=2)
    plotter.plot({'Basic': history}, metric = 'mae')
    plt.ylabel('Cases')
    plt.show()

    test_predictions = model.predict(normed_test_data).flatten()
    print(test_predictions)
    test_dataset['predicted'] = test_predictions
    test_dataset.to_csv('models/tensorflow/demo.csv', index=False)

    loss, mae, mse, mape = model.evaluate(normed_test_data, test_labels, verbose=2)
    print("Testing set Mean Abs Error: {:5.2f} cases".format(mae))

if __name__ == '__main__':
    main()
