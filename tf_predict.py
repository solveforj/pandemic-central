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
FEATURES = ['confirmed_cases', 'google_mobility_7d', \
    'apple_mobility_7d', 'fb_movement_change1']
FEATURE_COLS = FEATURES[1:]
LABEL = 'confirmed_cases'
MIN_POP = 500
N_BATCH = 1
EPOCHS = 180

mpl.rcParams['figure.figsize'] = (8, 6)
mpl.rcParams['axes.grid'] = False

df = pd.read_csv(PATH)
# drop the rows with NaN value
df = df.dropna()
# Drop the counties with population density less than MIN_POP people / sq mi
df = df.loc[df['POP_DENSITY']>=MIN_POP]
# Filter out the necessary columns only
df = df[FEATURES]
# Split the dataset into train and test
train_dataset = df.sample(frac=0.8,random_state=0)
test_dataset = df.drop(train_dataset.index)
# Visualize correlation by graphing
#pair_plot = sns.pairplot((train_dataset), diag_kind="kde")
#plt.show()
#heatmap = sns.heatmap(train_dataset.corr(),annot=True)
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

def build_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=[len(train_dataset.keys())]),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1)
      ])
    optimizer = tf.keras.optimizers.RMSprop(0.001)
    model.compile(loss='mse', optimizer=optimizer, metrics=['mae', 'mse'])
    return model

model = build_model()
print(model.summary())

history = model.fit(
  normed_train_data, train_labels,
  epochs=EPOCHS, validation_split = 0.2, verbose=0,
  callbacks=[tfdocs.modeling.EpochDots()])

plotter = tfdocs.plots.HistoryPlotter(smoothing_std=2)
plotter.plot({'Basic': history}, metric = "mae")
plt.ylabel('Cases')
plt.show()

test_predictions = model.predict(normed_test_data).flatten()
print(test_predictions)
print(test_labels)

### GRAVEYARD OF CODES BELOW THIS LINE ###
"""



early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)

early_history = model.fit(train_dataset, train_labels,
                    epochs=EPOCHS, validation_split = 0.2, verbose=0,
                    callbacks=[early_stop, tfdocs.modeling.EpochDots()])

plotter = tfdocs.plots.HistoryPlotter(smoothing_std=2)
plotter.plot({'Early Stopping': early_history}, metric = "mae")
plt.ylabel('Cases')
plt.show()

loss, mae, mse = model.evaluate(test_dataset, test_labels, verbose=2)

print("Testing set Mean Abs Error: {:5.2f} cases".format(mae))


feature_columns = []

for feature_name in FEATURE_COLS:
    feature_columns.append(tf.feature_column.numeric_column(feature_name))

# Use entire batch since this is such a small dataset.

def make_input_fn(X, y, n_epochs=None, shuffle=False):
  def input_fn():
    dataset = tf.data.Dataset.from_tensor_slices((dict(X), y))
    if shuffle:
      dataset = dataset.shuffle(len(y))
    # For training, cycle thru dataset as many times as need (n_epochs=None).
    dataset = dataset.repeat(n_epochs)
    # In memory training doesn't use batching
    dataset = dataset.batch(len(y))
    return dataset
  return input_fn

# Training and evaluation input functions
train_input_fn = make_input_fn(train_df, train_labels)
eval_input_fn = make_input_fn(test_df, test_labels)

model = tf.estimator.BoostedTreesRegressor(feature_columns, n_batches_per_layer=1)

model.train(input_fn=train_input_fn, max_steps=1000)

# Eval
result = model.evaluate(test_dataset)
"""
