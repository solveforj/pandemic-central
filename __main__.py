"""
Run this command to use our project:

    $python3 pandemic-central

or:
    $cd pandemic-central
    $python3 __main__.py
"""

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'developing'
__url__ = 'https://github.com/solveforj/pandemic-central'

import os
import preprocess
import tf_predict
#import train_scikit
#import generate_data

def main():
    path = os.getcwd() + ('/pandemic-central')
    os.chdir(path)
    preprocess.main()
    tf_predict.main()
    #generate_data.merge_data()

if __name__ == '__main__':
    main()
