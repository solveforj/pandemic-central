"""
This module renames datasets of Johns Hopkins into isoformat (if possible).

Remember to remove any other file but csv in raw_data/jhu/county to avoid errors
"""

import os
from datetime import date, datetime
import shutil

def rename_em(src='raw_data/jhu/county', dst='raw_data/jhu/county_renamed'):
    files = os.listdir(src)
    if not os.path.exists(dst):
        os.mkdir(dst)
    for file in files:
        m = file[:2]
        d = file[3:5]
        y = file[6:10]
        date_ = date(int(y), int(m), int(d)).isoformat()
        if not os.path.exists(dst + '/' + date_ + '.csv'):
            shutil.copy(src + '/' + file, dst + '/' + date_ + '.csv')

#if __name__ == '__main__':
#    rename_em()
