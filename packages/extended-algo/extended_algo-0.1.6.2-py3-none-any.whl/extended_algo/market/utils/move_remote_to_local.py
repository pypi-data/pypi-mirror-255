from extended_algo.market import MarketSource
import pandas as pd
import numpy as np
import os, pathlib
from tqdm import tqdm
from extended_algo.market.utils.common import get_market_data_source_dir
import logging

logger = logging.getLogger(__name__)


def move_remote_market_data_to_local(symbol, source: MarketSource):
    remote_dir_path = pathlib.Path(os.getenv('MARKET_DATA_REMOTE_DIR'))

    cols = ['datetime', 'open_p', 'high_p', 'low_p', 'close_p', 'prd_vlm']
    if source in (MarketSource.IQFEED_MINUTE_FEATHER, MarketSource.IQFEED_MINUTE):
        remote_dir = remote_dir_path / "minute_data" / symbol
    elif source in (MarketSource.IQFEED_SECOND_FEATHER, MarketSource.IQFEED_SECOND):
        remote_dir = remote_dir_path / "iq_seconds_data" / symbol
    elif source in (MarketSource.IQFEED_TICK_FEATHER, MarketSource.IQFEED_TICK):
        remote_dir = remote_dir_path / "tick_data" / symbol
        cols = ['datetime', 'bid', 'ask', 'last', 'last_sz']
    else:
        raise FileNotFoundError(f'"{source}" does not have remote market_data directory defined!')

    assert remote_dir.exists(), f'Required {symbol=} does not exits in location:\n{remote_dir}'

    local_dir = get_market_data_source_dir(source) / symbol
    local_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(os.listdir(remote_dir), columns=['filename'])
    df = df[df.filename.str.strip().str.endswith('.zip')]
    df = df.sort_values('filename', ascending=True)
    df['datetime_yyyy_mm_dd'] = pd.to_datetime(df.filename, format='%Y_%m_%d.zip', errors='coerce')
    df['datetime_yyyy_mm'] = pd.to_datetime(df.filename, format='%Y_%m.zip', errors='coerce')
    df['datetime'] = np.where(df.datetime_yyyy_mm_dd.isnull(), df.datetime_yyyy_mm, df.datetime_yyyy_mm_dd)

    if source in (MarketSource.IQFEED_TICK, MarketSource.IQFEED_TICK_FEATHER):
        df['save_as_date'] = df.datetime.apply(lambda x: dt.datetime(x.year, x.month, 1))
        df = df.groupby(['save_as_date']).agg(filenames=('filename', list))
        df['local_path'] = df.index.to_series().apply(lambda x: local_dir / f"{x:%Y_%m}.f")
    else:
        df['save_as_date'] = df.datetime.apply(lambda x: dt.datetime(x.year, 1, 1))
        df = df.groupby(['save_as_date']).agg(filenames=('filename', list))
        df['local_path'] = df.index.to_series().apply(lambda x: local_dir / f"{x:%Y}.f")

    processed_files_df = check_completed_on_local_dir(symbol=symbol, source=source)
    df = pd.concat([df, processed_files_df], axis=1)

    df = df[df.is_processed.isnull()]

    logger.info(f'Converting {symbol} {source.name}:')
    for x in df.itertuples():
        consolidate_df = []
        for file in tqdm(x.filenames, desc=f".  {x.Index:%b %Y}"):
            _df = pd.read_pickle(remote_dir / file, compression='zip')
            consolidate_df.append(_df)

        # logger.info(f'    Saving {x.local_path}')
        consolidate_df = pd.concat(consolidate_df, ignore_index=True)
        consolidate_df[cols].to_feather(x.local_path)


def check_completed_on_local_dir(symbol, source: MarketSource):
    try:
        local_dir = get_market_data_source_dir(source) / symbol
        df = pd.DataFrame(os.listdir(local_dir), columns=['is_processed'])
        df = df[df.is_processed.str.strip().str.endswith('.f')]
        df.is_processed = df.is_processed.str.replace('.f', '')
        df['datetime_yyyy_mm'] = pd.to_datetime(df.is_processed, format='%Y_%m', errors='coerce')
        df['datetime_yyyy'] = pd.to_datetime(df.is_processed, format='%Y', errors='coerce')
        df['save_as_date'] = np.where(df.datetime_yyyy_mm.isnull(), df.datetime_yyyy, df.datetime_yyyy_mm)
        df = df[['save_as_date', 'is_processed']]
        df = df.sort_values('save_as_date', ascending=True)
        df = df.iloc[0:-1]
        df = df.set_index('save_as_date')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['is_processed', 'save_as_date'])
        df = df.set_index('save_as_date')
    return df


if __name__ == '__main__':
    import datetime as dt
    from itertools import product

    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    ts = dt.datetime.now()

    refresh_symbols = {"XRT", 'SPY', 'BST'}
    market_type_sources = {MarketSource.IQFEED_MINUTE_FEATHER}

    # refresh_symbols = {"@ES#", 'QCL#', '@EU#', '@TY#', 'QGC#'}
    # market_type_sources = {MarketSource.IQFEED_MINUTE_FEATHER, MarketSource.IQFEED_SECOND_FEATHER,
    #                        MarketSource.IQFEED_TICK_FEATHER}

    # refresh_symbols = {"@ES#", 'QCL#', '@EU#', '@TY#', 'QGC#'}
    # market_type_sources = {MarketDataType.IQFEED_TICK_FEATHER}

    for symbol, source in sorted(product(refresh_symbols, market_type_sources), key=lambda x: x[0]):
        move_remote_market_data_to_local(symbol=symbol, source=source)
        logging.info(f'.  Elapsed time {dt.datetime.now() - ts}\n')
