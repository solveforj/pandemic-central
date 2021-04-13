import pandas as pd
from datetime import date, datetime, timedelta
from model import merge, train, predict, reichlab, web, map

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

def get_sunday(d):
    start = date.fromisoformat(d)

    while start.weekday()!=6:
        start += timedelta(days=1)

    return start.isoformat()

if __name__ == '__main__':
    start = input(f'Enter start date in isoformat (for example, today is {date.today().isoformat()}) ')


    print('Working on this Sunday...')
    date_today = get_sunday(start)
    print(date_today)

    input('Press \'Enter\' to proceed \n')

    #merge.merge(date_today)
    #train.train(date_today)
    #predict.predict(date_today)
    reichlab.reichlab(date_today)
    #web.web(date_today)
    #map.render(date_today)
