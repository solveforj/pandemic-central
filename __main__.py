from data.apple.preprocess import preprocess_apple
from data.CCVI.preprocess import preprocess_disparities
from data.census.preprocess import preprocess_census
from data.COVIDTracking.preprocess import preprocess_testing
from data.facebook.preprocess import preprocess_facebook
from data.google.preprocess import preprocess_google
from data.JHU.preprocess import preprocess_JHU
from data.Rt.preprocess import preprocess_Rt
import argparse

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'beta'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'


def main(args):
    if args.preprocess:
        preprocess_apple()
        preprocess_facebook()
        preprocess_google()
    if args.train:
        print('train here')
    if args.output:
        print('output here')
    if args.default:
        preprocess_apple()
        preprocess_google()
        preprocess_facebook()
        print('train here\noutput here')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='COVID-19 County Prediction\n',\
                                    usage='use "-h" or "--help" for more instructions')
    parser.add_argument('-d', '--default', action='store_true', help='Download and preprocess latest data, train, and predict')
    parser.add_argument('-p', '--preprocess', action='store_true', help='Download and preprocess data only')
    parser.add_argument('-t', '--train', action='store_true', help='Train model using Scikit-learn only')
    parser.add_argument('-o', '--output', action='store_true', help='Predict and export predictions only')
    parser.add_argument('--map', action='store_true', help='Render map for existing predictions')
    parser.add_argument('--tf', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    main(args)
