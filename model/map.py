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
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

PREDICTION_COLUMNS = ['ID', 'FIPS', 'date', 'TOT_POP']
WEEKS = ['1', '2', '3', '4']
DATE = date.today().isoformat()
WATERMARK_2 = 'data/geodata/pandemic-central-watermark-2.png'
WATERMARK_3 = 'data/geodata/pandemic-central-watermark-3.png'

UPPER_COLOR_LIMIT = 500

def read_lastest_file(date_today):
    PREDICTION_FILE = f'output/raw_predictions/raw_predictions_{date_today}.csv'
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

def render_map(df, wk):
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
    pio.write_image(fig, file=f'output/website/week-{wk}.png')
    if wk == 1:
        pio.write_html(fig, file='output/website/latest_map.html')
    if not os.path.exists('output/website'):
        os.mkdir('output/website')
    return f'output/website/week-{wk}.png'


def fix_map(path='output/website/latest_map.html'):
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

def add_watermark(img):
    background = Image.open(img)
    if len(str(UPPER_COLOR_LIMIT)) > 2:
        foreground = Image.open(WATERMARK_3)
    else:
        foreground = Image.open(WATERMARK_2)
    background.paste(foreground, (0, 0), foreground)
    background.save(img)

def render(date_today):
    print("GENERATING GRAPHICS\n")
    dfs = read_lastest_file(date_today)
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
    print('Rendering GIF image\n')
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(f'output/website/latest_map.gif', images, fps=1)
    print('finished\n')
