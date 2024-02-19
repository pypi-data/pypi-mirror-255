import pandas as pd
from sqlalchemy import create_engine
import logging
import re
import os
from dotenv import load_dotenv

load_dotenv()

pd.set_option('display.width', 1000, 'display.max_columns', 1000)

re_cols = re.compile('select\s(.*?)\sfrom', re.IGNORECASE)


def SecurityMaster(query):
    try:
        logging.info(f'Connecting to {os.getenv("DB_SECURITY_MASTER_READ").split("@")[1]}')
        db_engine = create_engine(os.getenv("DB_SECURITY_MASTER_READ"))
        db_conn = db_engine.connect()

        df = pd.read_sql(query, con=db_conn)
        df.columns = [x.lower() for x in df.columns]

        cols = re_cols.findall(query)[0].split(',')
        cols = [x.lower().strip() for x in cols]

        if len(cols) == 1 and 'count(*)' in cols:
            df = df.iloc[0]['count(*)']

    except Exception as err:
        logging.error(f'Something went wrong!\n{err}')
        df = pd.DataFrame()
    finally:
        db_conn.close()

    return df
