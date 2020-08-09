"""
This module creates an interactive HTML map and a PNG based on latest prediction

Credit: using Plotly for Choropleth Maps (under MIT License)
"""

import numpy as np
import pandas as pd
import os, sys
import plotly.express as px
import plotly.io as pio
import chart_studio.tools as tls
from urllib.request import urlopen
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw, ImageFilter

PREDICTION_COLUMNS = ['FIPS', 'date', 'model_predictions', 'ID']

def read_lastest_file():
    path = 'predictions/projections/predictions_latest.csv'
    df_predict = pd.read_csv(path, \
        low_memory=False, \
        usecols=PREDICTION_COLUMNS)
    # Get latest predicted data for each county
    df_predict = df_predict.groupby('FIPS').tail(1)
    df_predict = df_predict.drop(['date'], 1)
    df_predict['FIPS'] = df_predict['FIPS'].astype('str')
    df_predict['FIPS'] = df_predict['FIPS'].str.zfill(5)
    return df_predict

def render_map(df):
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
    pio.write_image(fig, file='predictions/projections/latest_map.png')
    pio.write_html(fig, file='predictions/projections/latest_map.html', auto_open=True)

def fix_map(path='predictions/projections/latest_map.html'):
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

def add_watermark(img_1='predictions/projections/latest_map.png',\
    img_2='data/graphics/pandemic-central-watermark.png'):

    background = Image.open(img_1)
    foreground = Image.open(img_2)

    background.paste(foreground, (0, 0), foreground)
    background.save(img_1)

def draw_map():
    df = read_lastest_file()
    render_map(df)
    fix_map()
    add_watermark()

if __name__ == '__main__':
    draw_map()
