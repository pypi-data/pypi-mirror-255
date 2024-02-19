"""
This is an example file that is used to create a table in
the database. Everything above the pound-line should not be modified.
Insert your code below the line to create a table. 

Best Practices:
    - Name the file the same name as the resulting table
    - Dont forget to update the DatabaseParameters file
    - Only read data that is currently in the database.
        Dont read data from external directories. This
        makes keeping track of the data present to the DB 
        much simpler. The data used to create tables should 
        be 1. present in the database and 2. in its raw form.
        This makes it easier to track down bugs that might
        exist in code.

"""

# DO NOT MODIFY

import sys
import pathlib
import sqlalchemy
import importlib.util

PATH_TO_DB = sys.argv[1]
PATH_TO_DBP = pathlib.Path(PATH_TO_DB).parent / 'DatabaseParameters.py'

spec = importlib.util.spec_from_file_location('DBP', str(PATH_TO_DBP))
DBP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(DBP)

sql_engine = sqlalchemy.create_engine(f'sqlite:///{PATH_TO_DB}')

############################################################################
# Your Code Below

#import pandas as pd
# read data from the database using sql
#df = pd.read_sql("""SQL QUERY""", con = sql_engine)
#df.to_sql(Tablename, con = sql_engine, if_exists = 'replace', index = False)