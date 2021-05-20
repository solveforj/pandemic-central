import pandas as pd
import os
from datetime import date

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

fips_to_state = {
   "01": "Alabama",
   "02": "Alaska",
   "04": "Arizona",
   "05": "Arkansas",
   "06": "California",
   "08": "Colorado",
   "09": "Connecticut",
   "10": "Delaware",
   "11": "District of Columbia",
   "12": "Florida",
   "13": "Georgia",
   "15": "Hawaii",
   "16": "Idaho",
   "17": "Illinois",
   "18": "Indiana",
   "19": "Iowa",
   "20": "Kansas",
   "21": "Kentucky",
   "22": "Louisiana",
   "23": "Maine",
   "24": "Maryland",
   "25": "Massachusetts",
   "26": "Michigan",
   "27": "Minnesota",
   "28": "Mississippi",
   "29": "Missouri",
   "30": "Montana",
   "31": "Nebraska",
   "32": "Nevada",
   "33": "New Hampshire",
   "34": "New Jersey",
   "35": "New Mexico",
   "36": "New York",
   "37": "North Carolina",
   "38": "North Dakota",
   "39": "Ohio",
   "40": "Oklahoma",
   "41": "Oregon",
   "42": "Pennsylvania",
   "44": "Rhode Island",
   "45": "South Carolina",
   "46": "South Dakota",
   "47": "Tennessee",
   "48": "Texas",
   "49": "Utah",
   "50": "Vermont",
   "51": "Virginia",
   "53": "Washington",
   "54": "West Virginia",
   "55": "Wisconsin",
   "56": "Wyoming"
}

pd.set_option('display.max_columns', 500)

def predict(date_today):
    print("MAKING PREDICTIONS\n")

    mobility_data = pd.read_csv(os.path.split(os.getcwd())[0] + "/" + "mobility_full_predictions.csv.gz", dtype={"label":float})
    no_mobility_data = pd.read_csv(os.path.split(os.getcwd())[0] + "/" + "no_mobility_full_predictions.csv.gz",dtype={"label":float})

    latest_dates = list(range(((9*-7)-1), 6, 7))
    latest_mobility = mobility_data.groupby("FIPS", as_index=False).nth(latest_dates)
    latest_no_mobility = no_mobility_data.groupby("FIPS", as_index=False).nth(latest_dates)

    combined_predictions = latest_mobility.append(latest_no_mobility, ignore_index=True)
    combined_predictions = combined_predictions.sort_values(['FIPS', 'date', 'fb_movement_change'], na_position='first').groupby(['FIPS', 'date']).tail(1)
    combined_predictions = combined_predictions.groupby("FIPS").tail(10)

    combined_predictions['fb_movement_change'] = combined_predictions['fb_movement_change'].astype(float)
    combined_predictions['fb_stationary'] = combined_predictions['fb_stationary'].astype(float)
    combined_predictions = combined_predictions.round(3)

    state = combined_predictions['FIPS'].astype(str).str.zfill(5).apply(lambda x: x[0:2]).map(fips_to_state)
    id = combined_predictions['Location'] + ", " + combined_predictions['FIPS'].astype(str) + ", " + state
    combined_predictions.insert(0, 'ID', id)

    combined_predictions.iloc[:, 65:-1] = combined_predictions.iloc[:, 65:-1].astype(float)
    combined_predictions.iloc[:, 65:-1] = combined_predictions.iloc[:, 65:-1].clip(lower=0)

    #print("Here are the latest dates for predictions of all counties:")
    #print(combined_predictions.groupby("FIPS").tail(1)['date'].unique())

    combined_predictions.to_csv("output/raw_predictions/raw_predictions_" + date_today + ".csv", index=False)
    print("  • Finished\n")
