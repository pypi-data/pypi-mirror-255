from extended_algo.market import MarketSource
from extended_algo.market.utils.resample_market_data import agg_resample_ticks, round_tick_bar_count, rename_iqfeed_tick_cols
from extended_algo.market.utils.use_cached_market_data import use_cached_market_data
from extended_algo.market.style import Ticks
import datetime as dt
import numpy as np


class TickBars:

    def __init__(self, symbol: str, start: dt.datetime, end: dt.datetime, freq: int, agg_consecutive_last_px=True,
                 use_cache=True, source=MarketSource.IQFEED_TICK_FEATHER, **kwargs):
        '''
        :param freq: create bar when number of ticks traded exceeds freq
        '''
        self.symbol = symbol
        self.start = start
        self.end = end
        self.agg_consecutive_last_px = agg_consecutive_last_px
        self.source = source
        self.kwargs = kwargs
        self.use_cache = use_cache

        self._ticks = self._get_tick_data()

        self.freq = freq
        assert self.freq >= 1
        assert source in (MarketSource.IQFEED_TICK_FEATHER, MarketSource.IQFEED_TICK), f'TickBar not supported on {source}'
        self.data = self._convert_to_bars(groupby_field="tick_count", groupby_count=self.freq)

    def _get_tick_data(self):
        ticks = Ticks(symbol=self.symbol, start=self.start, end=self.end, agg_consecutive_last_px=self.agg_consecutive_last_px,
                      kwargs=self.kwargs)
        return ticks.data

    @use_cached_market_data
    def _convert_to_bars(self, groupby_field, groupby_count):
        df = self._ticks
        filtered_agg = {key: agg_resample_ticks[key] for key in df.columns if key in agg_resample_ticks}
        df = df.groupby(round_tick_bar_count(np.cumsum(df[groupby_field]), groupby_count)).agg(filtered_agg)
        df = df.droplevel(0, axis=1)
        df = df.rename(columns=rename_iqfeed_tick_cols)
        return df["datetime open_p high_p low_p close_p prd_vlm".split()]
