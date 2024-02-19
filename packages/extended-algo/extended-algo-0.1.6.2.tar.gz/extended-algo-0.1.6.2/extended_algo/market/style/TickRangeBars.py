import pandas as pd
from extended_algo.market.utils.use_cached_market_data import use_cached_market_data
from extended_algo.market.style import Ticks
import datetime as dt


class TickRangeBars:

    def __init__(self, symbol: str, start: dt.datetime, end: dt.datetime, freq: int, use_cache=True, **kwargs):
        '''
        :param freq: create range bars when price bin is exceed; the starting price impacts the bin low/high boundaries
        '''
        self.symbol = symbol
        self.start = start
        self.end = end
        self.kwargs = kwargs
        self.use_cache = use_cache

        self._ticks = self._get_tick_data()

        self.freq = freq
        assert self.freq >= 0.0001

        self.data = self._calc_range_bars()

    def _get_tick_data(self):
        ticks = Ticks(symbol=self.symbol, start=self.start, end=self.end, agg_consecutive_last_px=True, kwargs=self.kwargs)
        ticks = ticks.data
        return ticks

    @use_cached_market_data
    def _calc_range_bars(self):
        df = self._ticks
        range_bars = []
        current_bar = {'open_p': df.iloc[0]['last'], 'high_p': -float('inf'), 'low_p': float('inf'), 'close_p': None,
                       'prd_vlm': df.iloc[0]['last_sz']}

        for item, row in df.iterrows():
            price = row['last']
            current_bar['high_p'] = max(current_bar['high_p'], price)
            current_bar['low_p'] = min(current_bar['low_p'], price)
            current_bar['prd_vlm'] += row['last_sz']

            if abs(current_bar['high_p'] - current_bar['low_p']) >= self.freq:
                current_bar['close_p'] = price
                current_bar['datetime'] = row['datetime']
                range_bars.append(current_bar)
                current_bar = {'open_p': price, 'high_p': price, 'low_p': price, 'close_p': None, 'prd_vlm': 0}

        df = pd.DataFrame(range_bars)
        df = df["datetime open_p high_p low_p close_p prd_vlm".split()]
        return df
