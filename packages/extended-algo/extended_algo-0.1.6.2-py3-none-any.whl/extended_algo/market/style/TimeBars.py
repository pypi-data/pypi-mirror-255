import pandas as pd
import datetime as dt
from extended_algo.market.utils.common import get_market_data_source_dir
from extended_algo.market import MarketSource, resample_market_data
from extended_algo.market.utils.use_cached_market_data import use_cached_market_data
from extended_algo.market.utils.common import MarketSource
import logging

class TimeBars:

    def __init__(self, source: MarketSource, symbol, start: dt.datetime, end: dt.datetime, freq=None,
                 use_cache=False, **kwargs):
        '''
        :param freq: Returning historical data will be Seconds or Minutes based on source. Resample data into a different time-freq (5Min, 1H, 1W ...)
        '''

        assert end - start >= dt.timedelta(milliseconds=0), 'end date must be greater than start date'
        assert source in (MarketSource.IQFEED_SECOND_FEATHER, MarketSource.IQFEED_SECOND,
                          MarketSource.IQFEED_MINUTE_FEATHER, MarketSource.IQFEED_MINUTE), \
            'ohlc only available vi seconds, minute data'
        self.symbol = symbol
        self.start = start
        self.end = end
        self.freq = freq
        if not self.freq:
            self.freq = '1S' if source in (MarketSource.IQFEED_SECOND_FEATHER, MarketSource.IQFEED_SECOND) else "1Min"

        self.use_cache = use_cache
        self.kwargs = kwargs

        self.source_type = source
        self.source_dir = get_market_data_source_dir(source)

        self.data = self._load_historical_data()

    @use_cached_market_data
    def _load_historical_data(self):
        load_file_years = list(range(self.start.year, self.end.year + 1))
        path_symbol_dir = self.source_dir / self.symbol

        df = []
        for year in load_file_years:
            try:
                cols = self.kwargs.pop('columns', None)
                if cols:
                    _data = pd.read_feather(path_symbol_dir / f'{year}.f', columns=cols)
                else:
                    _data = pd.read_feather(path_symbol_dir / f'{year}.f')
                df.append(_data)
            except FileNotFoundError:
                logging.error(f'File not found: {self.symbol} - {year}')

        df = pd.concat(df, ignore_index=True)
        df = df.query(f'datetime >= @self.start and datetime <= @self.end')

        if self.source_type in (MarketSource.IQFEED_SECOND_FEATHER, MarketSource.IQFEED_SECOND) and self.freq.upper() == "1S":
            return df
        if self.source_type in (
                MarketSource.IQFEED_MINUTE_FEATHER, MarketSource.IQFEED_MINUTE) and self.freq.upper() == '1MIN':
            return df

        df = resample_market_data(df, freq=self.freq)
        return df
