import numpy as np
import pandas as pd


def _check_trigger(strategy_obj, x):
    m = strategy_obj.market_data[['high_p', 'low_p', 'close_p']]

    m = m.loc[x.signal_time:x.signal_timeout]
    m['entry_price'] = x.entry_price
    m['direction'] = x.signal

    m['use_price'] = np.nan
    m['is_triggered'] = False

    # LONG PROPER CASE
    long_travel_through_condition = (m.direction == 1) & (m.entry_price >= m.low_p) & (m.entry_price <= m.high_p)
    m['is_triggered'] = np.where(long_travel_through_condition, True, m.is_triggered)
    m['use_price'] = np.where(long_travel_through_condition, 'entry_price', m.use_price)

    # LONG AUTO-FILL
    long_auto_fill_condition = (m.direction == 1) & (m.entry_price <= m.high_p)
    m['is_triggered'] = np.where(long_auto_fill_condition, True, m.is_triggered)

    # ---------------------------------------------------------------------------------------------------------------------
    # SHORT PROPER CASE
    short_travel_through_condition = (m.direction == -1) & (m.entry_price >= m.low_p) & (m.entry_price <= m.high_p)
    m['is_triggered'] = np.where(short_travel_through_condition, True, m.is_triggered)
    m['use_price'] = np.where(short_travel_through_condition, 'entry_price', m.use_price)

    # SHORT AUTO-FILL
    short_auto_fill_condition = (m.direction == -1) & (m.entry_price >= m.low_p)
    m['is_triggered'] = np.where(short_auto_fill_condition, True, m.is_triggered)

    try:
        entry = m[m.is_triggered].iloc[0]
        entry_time = entry.name

        if entry.direction == 1:
            if entry.use_price == 'entry_price':
                entry_price = entry.entry_price
            else:
                entry_price = entry.close_p
        else:
            if entry.use_price == 'entry_price':
                entry_price = entry.entry_price
            else:
                entry_price = entry.close_p

        return entry_time, entry_price

    except:
        return pd.NaT, np.nan


def create_stop_entries(strategy_obj, df):
    if df.empty:
        return df

    df[['entry_time', 'entry_price']] = df.apply(lambda x: _check_trigger(strategy_obj, x), axis=1, result_type="expand")
    df = df[~df['entry_time'].isnull()]

    return df
