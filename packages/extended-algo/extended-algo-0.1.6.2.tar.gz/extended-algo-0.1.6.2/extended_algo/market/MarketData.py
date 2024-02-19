import datetime as dt
import pandas as pd
from extended_algo.market.style import Ticks, TickBars, TickRangeBars, TickVolumeBars, TickDollarBars, TimeBars
from extended_algo.market import MarketSource, MarketDataType
import numpy as np

# TODO: MAE and MFE currently uses TimeBar; which allows for columns to be limited
#  will migrate to MarketData once STP, LMT, MKT code is finalized

class MarketData:

    def __init__(self, symbol: str, start: dt.datetime, end: dt.datetime, market_data_type: MarketDataType, freq: int | str,
                 lookback_period: pd.offsets = pd.offsets.Day(0), lookforward_period=pd.offsets.Day(0), use_cache=True,
                 agg_consecutive_last_px=True, **kwargs):
        '''
        Get Historical Market data to feed strategy discovery:
           - TIME - 1S, 1Min, 30Min, 1W...
           - TICKS - aggregates consecutive last_px in transaction history
           - TICK_COUNT - tick count
           - TICK_RANGE - price bins
           - TICK_VOLUME - volume traded
           - TICK_DOLLAR - volume * price traded

        :param symbol: iqfeed symbol
        :param start: start of market data feed
        :param end: end of market data feed
        :param market_data_type: references chart pattern to employ
        :param freq: reflects how the bar close
        :param use_cache: leverage existing market data cache if it exists, if not generate fresh cache on initial run
        :param agg_consecutive_last_px: reduce tick data by consolidating consecutive last px as one record
        :param lookback_period: market data will be supplied as inactive for datetime prior to start time.
        (A closed offset-period should be used when resampling timeframe)
        :param lookforward_period: market data will be supplied as inactive for datetime exceeding end time
        '''
        self.symbol = symbol
        self.start = start
        self.end = end
        self.market_data_type = market_data_type
        self.freq = freq
        self.use_cache = use_cache

        # Note: agg_consecutive_last_px has been set to True to reduce render time
        self.agg_consecutive_last_px = agg_consecutive_last_px

        #  May look to parametrize this field after more discovery on rounding errors
        self.lookback_start = self.start - lookback_period
        self.lookforward_end = self.end + lookforward_period

        # Since only FEATHER IQFEED data is supported, source is defaulted for the time being
        self.source = kwargs.pop('source', None)
        self.common_kwargs = dict(symbol=symbol, start=self.lookback_start, end=self.lookforward_end, freq=freq,
                                  use_cache=use_cache)

        self._market_object = self._get_market_data_obj()
        self.data = self._load_historical_data()

    def _get_market_data_obj(self):
        if self.market_data_type == MarketDataType.TIME:
            if "S" in self.freq.strip().upper():
                return TimeBars(**self.common_kwargs, source=MarketSource.IQFEED_SECOND_FEATHER)
            else:
                return TimeBars(**self.common_kwargs, source=MarketSource.IQFEED_MINUTE_FEATHER)

        elif self.market_data_type == MarketDataType.TICK_COUNT:
            return TickBars(**self.common_kwargs, source=MarketSource.IQFEED_TICK_FEATHER, agg_consecutive_last_px=True)

        elif self.market_data_type == MarketDataType.TICK:
            return Ticks(**self.common_kwargs, source=MarketSource.IQFEED_TICK_FEATHER, agg_consecutive_last_px=True)

        elif self.market_data_type == MarketDataType.TICK_RANGE:
            return TickRangeBars(**self.common_kwargs, source=MarketSource.IQFEED_TICK_FEATHER, agg_consecutive_last_px=True)

        elif self.market_data_type == MarketDataType.TICK_DOLLAR:
            return TickDollarBars(**self.common_kwargs, source=MarketSource.IQFEED_TICK_FEATHER, agg_consecutive_last_px=True)

        elif self.market_data_type == MarketDataType.TICK_VOLUME:
            return TickVolumeBars(**self.common_kwargs, source=MarketSource.IQFEED_TICK_FEATHER, agg_consecutive_last_px=True)

        raise NotImplemented(f'MarketData has not been been implemented for {self.market_data_type}!')

    def _load_historical_data(self):
        df = self._market_object.data
        df['is_live'] = 1
        df['is_live'] = np.where(df.datetime.between(self.lookback_start, self.start, inclusive='left'), 0, df.is_live)
        df['is_live'] = np.where(df.datetime.between(self.end, self.lookforward_end, inclusive='right'), 0, df.is_live)
        df['is_live'] = np.where(df.datetime <= self.lookback_start, 0, df.is_live)
        df['is_live'] = np.where(df.datetime >= self.lookforward_end, 0, df.is_live)
        return df
