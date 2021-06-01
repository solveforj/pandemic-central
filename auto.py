import pandas as pd
from datetime import date, datetime, timedelta
from model import merge, train, predict, reichlab, web, map
from publication import performance_comparison, performance_graph, feature_importance, rt_alignment, misc_stats
import argparse

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

def get_sunday(d):
    start = date.fromisoformat(d)

    while start.weekday()!=6:
        start -= timedelta(days=1)

    return start.isoformat()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run Pandemic Central model to generate U.S. county-level COVID-19 projections')
    parser.add_argument("-d", "--date", help=f'Start date in isoformat (for example, today is {date.today().isoformat()})', type=str)
    parser.add_argument("-r", "--can_api_key", help='COVIDActNow.org API Key (Register here: https://apidocs.covidactnow.org/#register)', type=str)
    parser.add_argument('--sunday', default=False, action='store_true', help='(Optional) If addressed, the forecast day will be the previous Sunday (i.e. week start)')
    parser.add_argument('--figures', default=False, action='store_true', help='(Optional) To plot figures and relevant data that we used in our research journal')
    parser.add_argument('--publication_method', default=False, action='store_true', help='(Optional) To replicate reported results in our research journal. See README.md for more details.')
    args = parser.parse_args()

    if args.figures:
        performance_comparison.performance_comparison()
        performance_graph.performance_graph()
        feature_importance.feature_importance()
        rt_alignment.rt_alignment()
        misc_stats.misc_stats()

    else:
        if args.sunday:
            print('Reference date for which forecasts will be generated: ', end='')
            date_today = get_sunday(args.date)
            print(date_today)
        else:
            print('Reference date for which forecasts will be generated: ', end='')
            date_today = args.date
            print(date_today)

        input('Press \'Enter\' to proceed \n')

        if args.publication_method:
            if date_today > "2021-01-15":
                print("Please restart and use a date between 2020-03-30 and 2021-01-15.")
            else:
                merge.merge(date_today, args.can_api_key, update_data=False)
                train.train(date_today, importance=True)
        else:
            merge.merge(date_today, args.can_api_key, update_data=True)
            train.train(date_today, importance=False)

        predict.predict(date_today)
        reichlab.reichlab(date_today)
        web.web(date_today)
        map.render(date_today)


        print("The pipeline is finished.  See results in output folder.")
