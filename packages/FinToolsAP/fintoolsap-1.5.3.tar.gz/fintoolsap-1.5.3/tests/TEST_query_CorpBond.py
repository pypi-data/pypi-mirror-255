import os
import sys
import time
import shutil
import pathlib
import datetime
import functools
import knockknock
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# add source directory to path
sys.path.insert(0, '../src/FinToolsAP/')

import QueryWRDS
import FamaFrench

# set printing options
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', shutil.get_terminal_size()[0])
pd.set_option('display.float_format', lambda x: '%.5f' % x)

# directory for loacl wrds database
LOCAL_WRDS_DB = pathlib.Path('/home/andrewperry/Documents')

SLACK_NOTIFY = True

def main():
    
    DB = QueryWRDS.QueryWRDS(WRDS_username = 'andrewperry', 
                             save_directory = LOCAL_WRDS_DB, 
                             database_name = 'WRDS'
                            )

    start_date = datetime.datetime(1900, 1, 1)
    end_date = datetime.datetime.now()
    
    s = time.time()
    df = DB.query_DB(DB.DBP.WRDS.CorpBond, start_date, end_date)
    e = time.time()
    print(f'loaded = {e - s}')
    print(df.head())
    print(df.info())
    mem = df.memory_usage(index = True, deep = True)
    print(f'total memory = {mem.sum()}')
    print(f'GiB = {round(mem.sum() / 10 ** 9, 2)}')


WEBHOOK_URL = 'https://hooks.slack.com/services/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'
@knockknock.slack_sender(webhook_url = WEBHOOK_URL,
                         channel = 'test',
                         user_mentions = ['U01DNFEHKEV'])
def filename(): # change to name of file
    main()

if __name__ == '__main__':
    if(os.getlogin() == 'andrewperry' and SLACK_NOTIFY):
        filename() # change to name of file
    else:
        main()