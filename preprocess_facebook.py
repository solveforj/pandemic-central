import pandas as pd
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
import os

z = urlopen('https://data.humdata.org/dataset/c3429f0e-651b-4788-bb2f-4adbf222c90e/resource/92ea5ec1-c87c-4210-92ac-abeb7aace2c7/download/movement-range-data-2020-06-07.zip')
myzip = ZipFile(BytesIO(z.read()))
print(myzip.infolist())
df = pd.read_csv(myzip.open('movement-range-2020-06-07.txt'), sep='\t', dtype={'polygon_id':str})
df = df[df['country'] == 'USA']
#df.to_csv("raw_data/facebook/facebook_raw.csv", sep=',', index=False)
#df = pd.read_csv("raw_data/facebook/facebook_raw.csv", dtype={'polygon_id':str})
df = df[['ds', 'polygon_id', 'all_day_bing_tiles_visited_relative_change', 'all_day_ratio_single_tile_users']]
df = df.rename({'polygon_id':'FIPS','ds':'date','all_day_bing_tiles_visited_relative_change':'fb_movement_change', 'all_day_ratio_single_tile_users':'fb_stationary'}, axis=1)
df = df.reset_index(drop=True)

df['fb_movement_change1'] = pd.Series(df.groupby("FIPS")['fb_movement_change'].rolling(7).mean()).reset_index(drop=True)
df['fb_stationary1'] = pd.Series(df.groupby("FIPS")['fb_stationary'].rolling(7).mean()).reset_index(drop=True)

df['date'] = pd.to_datetime(df['date'])
df['date'] = df['date'].apply(pd.DateOffset(1))
df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
df = df.dropna()
df.to_csv('raw_data/facebook/facebook.csv', sep=',', index=False)
