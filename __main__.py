from model.merge import merge
from model.train import train
from model.predict import predict

#predict()
import argparse

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'beta'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.0.0'


def main(args):
    if args.preprocess:
        merge()
    if args.train:
        train()
    if args.predict:
        predict()
    if args.default:
        merge()
        train()
        predict()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='COVID-19 County Prediction\n',\
                                    usage='use "-h" or "--help" for more instructions')
    parser.add_argument('-d', '--default', action='store_true', help='Download and preprocess latest data, train, and predict')
    parser.add_argument('-p', '--preprocess', action='store_true', help='Download and preprocess data only')
    parser.add_argument('-t', '--train', action='store_true', help='Train model using Scikit-learn only')
    parser.add_argument('-o', '--predict', action='store_true', help='Predict and export predictions only')
    parser.add_argument('--map', action='store_true', help='Render map for existing predictions')
    parser.add_argument('--tf', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    main(args)
