import pandas as pd
import numpy as np

agg_resample_bars = dict(open_p='first', high_p='max', low_p='min', close_p='last', is_live='last', prd_vlm='sum')
agg_resample_ticks = dict(last='ohlc', last_sz='sum', tick_count='sum', datetime='last', dollar_traded="sum")
rename_iqfeed_tick_cols = dict(open='open_p', high='high_p', low='low_p', close='close_p', last_sz='prd_vlm')


def round_tick_bar_count(xs, y):
    return np.int64(xs / y) * y


def resample_market_data(df, freq):
    _col_resample = {k: v for k, v in agg_resample_bars.items() if k in set(df.columns)}

    try:
        df = df.groupby(pd.Grouper(freq=freq, key='datetime')).agg(_col_resample)
    except KeyError:
        df = df.groupby(pd.Grouper(freq=freq)).agg(_col_resample)

    df = df.reset_index()
    df = df.dropna()
    return df
