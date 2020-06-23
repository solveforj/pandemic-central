"""
Please read README.md before using
"""

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'released'
__url__ = 'https://github.com/solveforj/pandemic-central'

import os
import preprocess
import tf_predict
from colorama import init, Fore, Back, Style
import generate_data
import train

path = os.getcwd() + ('/pandemic-central')
os.chdir(path)
init()

def main(state='on'):
    print(Fore.BLUE + Back.WHITE + Style.BRIGHT + '''
  __             __   ___          __      __   ___      ___  __
 |__)  /\  |\ | |  \ |__   |\/| | /  `    /  ` |__  |\ |  |  |__)  /\  |
 |    /~~\ | \| |__/ |___  |  | | \__,    \__, |___ | \|  |  |  \ /~~\ |___
        ''')
    print()
    print(Style.DIM + 'An application of Machine Learning in predicting COVID-19\n')
    while state == 'on':
        menu = ['1. Preprocess data only',\
            '2. Preprocess, train and predict with Scikit-learn',\
            '3. Train and predict data using TensorFlow (EXPERIMENTAL)',\
            '4. Exit']
        print(Fore.BLACK + Back.WHITE + Style.NORMAL)
        print('\nOPTIONS:\n')
        for opt in menu:
            print(Fore.BLACK + opt)
        print(Style.RESET_ALL)
        print('\n')
        user_input = input('Enter option as its equivalent number: ')
        if user_input == '1':
            preprocess.main()
            generate_data.merge_data(save_files=True, ag=True)
        elif user_input == '2':
            train.main()
        elif user_input == '3':
            tf_predict.main()
        elif user_input == '4':
            state = 'off'
        elif not user_input in ['1', '2', '3', '4']:
            print(Fore.RED + '\nInvalid option! Please try again.')
            print(Style.RESET_ALL)

if __name__ == '__main__':
    main()
