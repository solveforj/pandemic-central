import pandas as pd
from os import listdir
from utils import calculate_mae

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'

def web():
    #date_today = date.today().strftime('%Y-%m-%d')
    date_today = "2020-08-22"

    projections = pd.read_csv("predictions/projections/predictions_" + date_today + ".csv")
    projections = projections.fillna("NULL")
    projections['date'] = pd.to_datetime(projections['date'])
    projections['date'] = projections['date'].apply(pd.DateOffset(7))
    #projections = projections.rename({"model_predictions":"model_predictions_norm"}, axis=1)
    projections['model_predictions'] = projections['model_predictions_norm'] / 100000 * projections['TOT_POP']
    projections['risk'] = projections['model_predictions'] * 7 / projections['TOT_POP'] * 100

    mae, _ = calculate_mae(cumulative=True)
    projections['mae'] = [mae] * len(projections)

    projections.to_csv("predictions/web/predictions_" + date_today + ".csv", index=False)
    projections.to_csv("predictions/web/predictions_latest.csv", index=False)

if __name__ == "__main__":
    web()
