"""
This module creates HTML for an interactive U.S. maps with predicted case
number for county

Credit: using Plotly for Choropleth Maps (MIT License)
"""

import numpy as np
import pandas as pd
import os, sys
import plotly.express as px
import plotly.io as pio
import chart_studio.tools as tls
from preprocess import get_latest_file
from urllib.request import urlopen
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw, ImageFilter

PREDICTION_COLUMNS = ['FIPS', 'date', 'model_predictions', 'ID']

def _read_lastest_file():
    path = get_latest_file('predictions')
    df_predict = pd.read_csv(path, \
        low_memory=False, \
        usecols=PREDICTION_COLUMNS)
    # Get latest predicted data for each county
    df_predict = df_predict.groupby('FIPS').tail(1)
    df_predict = df_predict.drop(['date'], 1)
    df_predict['FIPS'] = df_predict['FIPS'].astype('str')
    df_predict['FIPS'] = df_predict['FIPS'].str.zfill(5)
    return df_predict

def _draw_map(df):
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    fig = px.choropleth(df, geojson=counties, locations='FIPS', color='model_predictions',
                               color_continuous_scale="Spectral_r",
                               range_color=(0, 40),
                               hover_name='ID',
                               hover_data={'FIPS':False},
                               scope="usa",
                               labels={'model_predictions':'Predicted'},
                               width=1100,
                               height=600
                              )
    fig.update_layout(
        title='Average projected new cases per 100,000 people per day for the next two weeks',
        title_x=0.5,
        title_font_size=16)
    pio.write_image(fig, file='processed_data/maps/map.png')
    pio.write_html(fig, file='processed_data/maps/index.html', auto_open=True)

def _fix_maps(path='processed_data/maps/index.html'):
    with open(path) as map_:
        content = map_.read()
    # Remove the "Tool Bar"
    content = content.replace(
        'displayModeBar:{valType:"enumerated",values:["hover",!0,!1],dflt:"hover"}',\
        'displayModeBar:{valType:"enumerated",values:["hover",!0,!1],dflt:!1}')
    # Deactivate the zoom and drag
    content = content.replace(
        'dragmode:{valType:"enumerated",values:["zoom","pan","select","lasso","drawclosedpath","drawopenpath","drawline","drawrect","drawcircle","orbit","turntable",!1],dflt:"zoom"',\
        'dragmode:{valType:"enumerated",values:["zoom","pan","select","lasso","drawclosedpath","drawopenpath","drawline","drawrect","drawcircle","orbit","turntable",!1],dflt:!1')
    with open(path, 'w') as new_map:
        new_map.write(content)

def _corr_graph(cols):
    path = get_latest_file('merged')
    df_merged = pd.read_csv(path, usecols=cols)
    corrs = df_merged.corr()
    #pair_plot = sns.pairplot(df_merged, diag_kind="kde")
    heatmap = sns.heatmap(df_merged.corr(), annot=True)
    plt.show()

def _add_watermark(img_1='processed_data/maps/map.png',\
    img_2='processed_data/maps/pandemic-central-watermark.png'):

    background = Image.open(img_1)
    foreground = Image.open(img_2)

    background.paste(foreground, (0, 0), foreground)
    background.save(img_1)

def main():
    df = _read_lastest_file()
    _draw_map(df)
    _fix_maps()

if __name__ == '__main__':
    main()
    _add_watermark()
    #_corr_graph(['confirmed_cases', 'fb_movement_change', 'google_mobility_14d', \
    #    'apple_mobility_14d'])
