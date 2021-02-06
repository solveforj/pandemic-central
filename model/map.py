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
from PIL import Image, ImageDraw, ImageFilter
from datetime import datetime, date
import imageio

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'

PREDICTION_FILE = 'predictions/projections/predictions_latest.csv'
PREDICTION_COLUMNS = ['ID', 'FIPS', 'date', 'TOT_POP']
WEEKS = ['1', '2', '3', '4']
QUANTILES = ['0.025', '0.1', '0.25', '0.5', '0.75', '0.9', '0.975']
DATE = date.today().isoformat()
WATERMARK = 'predictions/graphics/pandemic-central-watermark.png'
WATERMARK_2 = 'predictions/graphics/pandemic-central-watermark-2.png'
WATERMARK_3 = 'predictions/graphics/pandemic-central-watermark-3.png'
UPPER_COLOR_LIMIT = 500

def read_lastest_file(type='predictions'):
    if type=='predictions':
        # Read data
        week_1 = pd.read_csv(PREDICTION_FILE, usecols=PREDICTION_COLUMNS+['point_1_weeks'])
        week_1 = week_1.groupby('FIPS').tail(1)
        week_1 = week_1.rename(columns={'point_1_weeks': 'value'}).drop(['date'], 1)
        week_1['FIPS'] = week_1['FIPS'].astype('str').str.zfill(5)

        week_2 = pd.read_csv(PREDICTION_FILE, usecols=PREDICTION_COLUMNS+['point_2_weeks'])
        week_2 = week_2.groupby('FIPS').tail(1)
        week_2 = week_2.rename(columns={'point_2_weeks': 'value'}).drop(['date'], 1)
        week_2['FIPS'] = week_2['FIPS'].astype('str').str.zfill(5)

        week_3 = pd.read_csv(PREDICTION_FILE, usecols=PREDICTION_COLUMNS+['point_3_weeks'])
        week_3 = week_3.groupby('FIPS').tail(1)
        week_3 = week_3.rename(columns={'point_3_weeks': 'value'}).drop(['date'], 1)
        week_3['FIPS'] = week_3['FIPS'].astype('str').str.zfill(5)

        week_4 = pd.read_csv(PREDICTION_FILE, usecols=PREDICTION_COLUMNS+['point_4_weeks'])
        week_4 = week_4.groupby('FIPS').tail(1)
        week_4 = week_4.rename(columns={'point_4_weeks': 'value'}).drop(['date'], 1)
        week_4['FIPS'] = week_4['FIPS'].astype('str').str.zfill(5)

        return [week_1, week_2, week_3, week_4]

    elif type == 'vaccinations':
        df = pd.read_csv('data/vaccine/covid_vaccine_by_state.csv')

        for i in df.columns.values.tolist()[2:5]:
            df[i] = df.groupby('state')[i].cumsum()
        df = df.groupby('state').tail(1)

        df_pop = pd.read_csv('data/census/Reichlab_Population.csv',
                            usecols=['abbreviation', 'population'])
        df_pop = df_pop.dropna(subset=['abbreviation'])
        d = dict(zip(df_pop['abbreviation'], df_pop['population']))
        df['population'] = df['state'].map(d)

        for i in df.columns.values.tolist()[2:5]:
            df[i] = df[i]*100000/df['population']

        return df

def render_map(df, wk, type='predictions'):
    if type == 'predictions':
        with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
            counties = json.load(response)
        fig = px.choropleth(df, geojson=counties, locations='FIPS', color='value',
                                   color_continuous_scale="Spectral_r",
                                   range_color=(0, UPPER_COLOR_LIMIT),
                                   hover_name='ID',
                                   hover_data={'FIPS':False},
                                   scope="usa",
                                   labels={'value':'Predicted'},
                                   width=1100,
                                   height=600
                                  )
        fig.update_layout(
            title=f'Projected new cases per 100,000 people for {wk} week ahead' if wk == 1 else f'Projected new cases per 100,000 people for {wk} weeks ahead',
            title_x=0.5,
            title_font_size=16)
        pio.write_image(fig, file=f'predictions/graphics/{DATE}-{wk}.png')
        if wk == 1:
            pio.write_html(fig, file='predictions/graphics/latest_map.html')
        return f'predictions/graphics/{DATE}-{wk}.png'

    if type == 'vaccinations':
        latest_date = df['date'].unique()[0]
        latest_iso_date = date.fromisoformat(latest_date).strftime('%B %d')
        paths = []
        for manu in df.columns.values.tolist()[2:5]:
            manufacturer = manu.split('_')[0].capitalize()
            title = f'{manufacturer} allocated vaccine doses per 100,000 by {latest_iso_date}'

            fig = px.choropleth(df, locationmode="USA-states",
                                    locations='state',
                                    color=manu,
                                    color_continuous_scale='blues',
                                    scope='usa',
                                    labels={manu:'Doses'},
                                    width=1100,
                                    height=600
                                )
            fig.update_layout(
                title=title,
                title_x=0.5,
                title_font_size=16)
            if not os.path.exists('data/vaccine/maps'):
                os.mkdir('data/vaccine/maps')
            pio.write_image(fig, file=f'data/vaccine/maps/{manufacturer}-vaccine-map.png')
            paths.append(f'data/vaccine/maps/{manufacturer}-vaccine-map.png')
        return paths


def fix_map(path='predictions/graphics/latest_map.html'):
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

def add_watermark(img, type='predictions'):
    background = Image.open(img)
    if type == 'predictions':
        if len(str(UPPER_COLOR_LIMIT)) > 2:
            foreground = Image.open(WATERMARK_3)
        else:
            foreground = Image.open(WATERMARK_2)
    elif type == 'vaccinations':
        foreground = Image.open(WATERMARK)
    background.paste(foreground, (0, 0), foreground)
    background.save(img)

def render(type='predictions'):
    if type == 'predictions':
        dfs = read_lastest_file()
        weeks = list(range(1,5))
        filenames = []
        for df, wk in zip(dfs, weeks):
            print(f'Rendering Week {wk}', end='')
            path = render_map(df, wk)
            add_watermark(path)
            filenames.append(path)
            print(' - Done!')
        print('Rendering interactive map', end='')
        fix_map()
        print(' - Done!')
        images = []
        print('Rendering GIF image', end='')
        for filename in filenames:
            images.append(imageio.imread(filename))
        imageio.mimsave(f'predictions/graphics/latest_map.gif', images, fps=1)
        print(' - Done!')
    elif type == 'vaccinations':
        print('Rendering Vaccine Maps', end='')
        df = read_lastest_file(type='vaccinations')
        maps = render_map(df, 0, type='vaccinations')
        for m in maps:
            add_watermark(m, type='vaccinations')
        print(' - Done!')

if __name__ == "__main__":
    render()
