from extended_algo.market import MarketData
import datetime as dt
import pandas as pd
from extended_algo.market.style import Ticks, TickBars, TickRangeBars, TickVolumeBars, TickDollarBars, TimeBars
from extended_algo.market import MarketSource, MarketDataType
import numpy as np


# Note: Please reference the MarketData module for details on args, and kwargs
class LogReturnMarketData():

    def __init__(self, symbol: str, start: dt.datetime, end: dt.datetime, market_data_type: MarketDataType, freq: int | str,
                 lookback_period: pd.offsets = pd.offsets.Day(0), lookforward_period=pd.offsets.Day(0), use_cache=True,
                 agg_consecutive_last_px=True, **kwargs):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.market_data_type = market_data_type
        self.freq = freq
        self.use_cache = use_cache

        self.agg_consecutive_last_px = agg_consecutive_last_px

        self.lookback_period = lookback_period
        self.lookforward_period = lookforward_period

        self.source = kwargs.pop('source', None)
        self.common_kwargs = {'symbol': self.symbol, 'start': self.start, 'end': self.end, 'freq': self.freq,
                              'lookback_period': self.lookback_period, 'lookforward_period': self.lookforward_period,
                              'market_data_type': self.market_data_type,
                              'use_cache': self.use_cache, 'agg_consecutive_last_px': self.agg_consecutive_last_px}

        self.delog_data = self._get_historical_market_data()
        self.data = self._calc_log_return()

    def _get_historical_market_data(self):
        market = MarketData(**self.common_kwargs)
        return market.data

    def _log_return_series(self, label):
        df = self.delog_data[[label]]
        series = np.log(df[label] / df[label].shift(1)).dropna()
        return pd.Series(series, name=label)

    def _calc_log_return(self):
        # TODO: for all of these cases but tick, we need to ohlc, but for tick we need last only

        series = []
        for x in ['open_p', 'high_p', 'low_p', 'close_p']:
            series.append(self._log_return_series(x))

        df = pd.concat(series, axis=1)
        datetime_series = self.delog_data['datetime']
        is_live_series = self.delog_data['is_live']
        prd_vlm_series = self.delog_data['prd_vlm']

        df = pd.concat([datetime_series, df, is_live_series, prd_vlm_series], axis=1).dropna()

        print('\n', df)
        return df
