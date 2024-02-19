import pandas as pd
import datetime as dt
from extended_algo.market import MarketSource
from extended_algo.market.utils.common import get_market_data_source_dir
from extended_algo.market.utils.use_cached_market_data import use_cached_market_data


class Ticks:

    def __init__(self, symbol: str, start: dt.datetime, end: dt.datetime, agg_consecutive_last_px=True, use_cache=True,
                 **kwargs):
        '''
        :param agg_consecutive_last_px: sequential prices where last_px is the same will be rolled into one record with last_sz and tick_count summed to drastically shrink tick dataset for iteration
        :param use_cache: leveraging ticks is an expensive operation so best to leverage cache to reduce load time
        '''

        source = kwargs.pop('source', MarketSource.IQFEED_TICK_FEATHER)
        assert end - start >= dt.timedelta(milliseconds=0), 'end date must be greater than start date'
        assert end - start <= dt.timedelta(days=32), 'reading tick data is expensive, limit to <31 days'
        assert source in (MarketSource.IQFEED_TICK, MarketSource.IQFEED_TICK_FEATHER), 'only tick source is supported'

        self.symbol = symbol
        self.start = start
        self.end = end

        self.kwargs = kwargs
        self.agg_consecutive_last_px = agg_consecutive_last_px
        self._source_dir = get_market_data_source_dir(source=source)
        self.use_cache = use_cache
        self.freq = None

        self.data = self._load_historical_data()


    @use_cached_market_data
    def _load_historical_data(self):
        _start_time = dt.datetime.combine(self.start.date().replace(day=1), dt.time(0, 0, 0, 0))

        load_dates = pd.date_range(start=_start_time, end=self.end + pd.offsets.MonthEnd(0),
                                   freq='MS', inclusive='both')

        load_dates = pd.DataFrame(load_dates, columns=['load_date'])
        load_dates['load_path'] = load_dates.load_date.apply(lambda x: self._source_dir / self.symbol / f'{x:%Y_%m.f}')

        df = []
        for file in load_dates.itertuples():
            cols = self.kwargs.pop('columns', None)
            if cols:
                _data = pd.read_feather(file.load_path, columns=cols)
            else:
                _data = pd.read_feather(file.load_path)
            df.append(_data)

        df = pd.concat(df, ignore_index=True)
        df = df.sort_values('datetime', ascending=True)
        df = df.query(f'datetime >= @self.start and datetime <= @self.end')
        df['tick_count'] = 1

        if self.agg_consecutive_last_px:
            df['group'] = (df['last'] != df['last'].shift()).cumsum()
            df = df.groupby(['group', 'last']).agg({'datetime': 'last', 'last_sz': 'sum', 'tick_count': 'sum'})
            df = df.reset_index().drop('group', axis=1)

        return df
