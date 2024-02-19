import logging
from extended_algo.market.style import TimeBars
from extended_algo.market import MarketData
from extended_algo.market.utils.common import MarketSource
import numpy as np
import pandas as pd

map_direction = {'SHORT': -1, 'LONG': 1}


class MaxFavorableAdverseExcursion:

    def __init__(self, pnl_data):
        logging.info('Calculating MAE MFE for pnl data')
        self.pnl_data = pnl_data
        self.market_data = self._get_market_data()

        try:
            self.pnl_data[['mfe', 'mfe_time', 'mae', 'mae_time']] = self.pnl_data.apply(lambda x: self._calc_mae_mfe(x),
                                                                                        axis=1, result_type='expand')
        except ValueError:
            self.pnl_data['mfe'], self.pnl_data['mae'] = np.nan, np.nan
            self.pnl_data['mfe_time'], self.pnl_data['mae_time'] = pd.NaT,  pd.NaT

    def _get_market_data(self):
        try:
            market = TimeBars(MarketSource.IQFEED_MINUTE_FEATHER, symbol=self.pnl_data.symbol.iloc[0],
                              start=self.pnl_data.entry_time.min(), end=self.pnl_data.exit_time.max(),
                              columns=['datetime', 'low_p', 'high_p'])
            return market.data
        except IndexError:
            market_data = pd.DataFrame({'datetime': pd.Series(dtype='datetime64[ns]'), 'high_p': pd.Series(dtype='float'),
                                        'low_p': pd.Series(dtype='float'), })
            return market_data

    def _calc_mae_mfe(self, x):
        # TODO: I cant use exit - entry to calculate mfe or mae; you actually need the stop-loss and profit abs value
        market_data = self.market_data.query('datetime > @x.entry_time and datetime <= @x.exit_time')
        direction_value = map_direction[x.direction]

        market_data = market_data.set_index('datetime')

        if not market_data.empty:
            idx_max = market_data.high_p.idxmax()
            idx_min = market_data.low_p.idxmin()

            high_mark = (market_data.loc[idx_max].high_p - x.entry_price) * direction_value
            low_mark = (market_data.loc[idx_min].low_p - x.entry_price) * direction_value

            if high_mark >= low_mark:
                mfe_px = high_mark
                mfe_time = idx_max
                mae_px = low_mark
                mae_time = idx_min

            else:
                mfe_px = low_mark
                mfe_time = idx_min
                mae_px = high_mark
                mae_time = idx_max

            abs_pt = abs(x.pt - x.entry_price)
            abs_sl = abs(x.sl - x.entry_price)

            if abs(mfe_px) > abs_pt:
                return abs_pt, mfe_time, mae_px, mae_time

            if abs(mae_px) > abs(abs_sl):
                return mfe_px, mfe_time, -1 * abs_sl, mae_time

            return mfe_px, mfe_time, mae_px, mae_time

        return (np.nan, pd.Timestamp('NaT').to_pydatetime(), np.nan, pd.Timestamp('NaT').to_pydatetime())
