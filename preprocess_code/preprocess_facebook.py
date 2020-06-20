import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
import os

link = "https://data.humdata.org/dataset/movement-range-maps"
page = requests.get(link).content
soup = BeautifulSoup(page, 'html.parser')
dataLink = soup.find_all('a', {"class": "btn btn-empty btn-empty-blue hdx-btn resource-url-analytics ga-download"}, href=True)[0]['href']
dataLink = "https://data.humdata.org" + dataLink

dataFile = dataLink.split("/")[-1].split(".")[0].replace("-data", "") + ".txt"
print(dataLink)
print(dataFile)

z = urlopen(dataLink)
myzip = ZipFile(BytesIO(z.read()))
print(myzip.infolist())
df = pd.read_csv(myzip.open(dataFile), sep='\t', dtype={'polygon_id':str})
df = df[df['country'] == 'USA']
#df.to_csv("raw_data/facebook/facebook_raw.csv", sep=',', index=False)
#df = pd.read_csv("raw_data/facebook/facebook_raw.csv", dtype={'polygon_id':str})
df = df[['ds', 'polygon_id', 'all_day_bing_tiles_visited_relative_change', 'all_day_ratio_single_tile_users']]
df = df.rename({'polygon_id':'FIPS','ds':'date','all_day_bing_tiles_visited_relative_change':'fb_movement_change', 'all_day_ratio_single_tile_users':'fb_stationary'}, axis=1)
df = df.reset_index(drop=True)

df['fb_movement_change'] = pd.Series(df.groupby("FIPS")['fb_movement_change'].rolling(7).mean()).reset_index(drop=True)
df['fb_stationary'] = pd.Series(df.groupby("FIPS")['fb_stationary'].rolling(7).mean()).reset_index(drop=True)

df['date'] = pd.to_datetime(df['date'])
df['date'] = df['date'].apply(pd.DateOffset(1))
df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
df = df.dropna()
df.to_csv('raw_data/facebook/facebook.csv', sep=',', index=False)
