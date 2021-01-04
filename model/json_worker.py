import urllib3
import json
import pandas as pd

http = urllib3.PoolManager()
r = http.request('GET', "https://itsonit.com/static/geojson-counties-fips.geojson")

result = r.data.decode('UTF-8')[18:].strip()

j = json.loads(result)

df = pd.read_csv("predictions/website/web_latest.csv", dtype={"FIPS":str}).groupby("FIPS").tail(4).reset_index(drop=True)

df = df[['FIPS', 'date', 'cases']]

df['FIPS'] = df['FIPS'].apply(lambda x: "0" + x if len(x) < 5 else x)
census = pd.read_csv("data/census/census.csv", dtype={'FIPS':str})[['FIPS', 'TOT_POP']]
df = pd.merge(left=df, right=census, how='left', on=['FIPS'], copy=False)

df['cases_p'] = (df['cases'] / df['TOT_POP'] * 7).round(5)
df['cases'] = (df['cases'] * 7).round(0)
df = df[['FIPS','date','cases', 'cases_p']]

print(df['cases_p'].max())
print(df['cases_p'].min())

imploded_df = df.groupby("FIPS").agg({'FIPS': lambda x: x.iloc[0], 'date': lambda x: x.tolist(), 'cases': lambda x: x.tolist(), 'cases_p': lambda x: x.tolist()}).reset_index(drop=True)

imploded_df = imploded_df.set_index("FIPS")

imploded_dict = imploded_df.T.to_dict("list")

print(len(imploded_dict.keys()))
print(imploded_dict['49017'])

from collections import defaultdict

present = 0
tot_county = len(j['features'])
for i in range(tot_county):
    county = j['features'][i]['id']
    if county in imploded_dict.keys():
        present += 1
        dates = imploded_dict[county][0]
        cases = imploded_dict[county][1]
        cases_p = imploded_dict[county][2]
        cases_dict = dict(zip(dates, cases))
        cases_p_dict = dict(zip(dates, cases_p))
        merged_dict = defaultdict(list)
        for d in (cases_dict, cases_p_dict): # you can list as many input dicts as you want here
            for key, value in d.items():
                merged_dict[key].append(value)
        j['features'][i]['properties']['cases'] = merged_dict
    else:
        #dates = ["NULL"]*4
        #cases = [0]*4
        #cases_p = [0]*4
        merged_dict = {"NULL0":[0, 0], "NULL1":[0, 0],"NULL2":[0, 0],"NULL3":[0, 0]}
        print(merged_dict)
        j['features'][i]['properties']['cases'] = merged_dict
        print(j['features'][i]['properties']['cases'])
        print()

for i in range(tot_county):
    if j['features'][i]['id'] == '49017':
        print(j['features'][i])

output_json = r.data.decode('UTF-8')[0:18] + json.dumps(j)

with open('predictions/website/county-data.geojson', 'w') as f:
    f.write(output_json)
