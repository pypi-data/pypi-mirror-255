import os
import sys
import pathlib
import shutil
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, '../src/FinToolsAP/')

import LocalDatabase
import Decorators
import LaTeXBuilder

# set printing options
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', shutil.get_terminal_size()[0])
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# directory for loacl wrds database 

# linux
LOCAL_WRDS_DB = pathlib.Path('/home/andrewperry/Documents')

@Decorators.Performance
def query_CRSP_performance(DB):
    return(DB.queryDB(DB.DBP.CHAR, ticker = 'JPM', all_vars = True))

def main():

    """
    df = pd.read_stata('/home/andrewperry/Documents/ValueFunds/FILEStoDB/MF_SCORES.dta')
    print(df.head(10))
    raise ValueError
    """

    DB = LocalDatabase.LocalDatabase(save_directory = LOCAL_WRDS_DB, 
                                     database_name = 'LCLDB'
                                    )
    print(DB)

    #df = DB.queryDB(DB.DBP.MutualFundCharacteristics, all_vars = True)
    
    

if __name__ == "__main__":
    main()
