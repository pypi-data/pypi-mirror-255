import pandas as pd
from extended_algo.report.calculate.Pnl import CalculatePnL
import numpy as np
from types import NoneType
from tqdm import tqdm
import re
import logging

re_offset_time = re.compile('(\d+)([A-Za-z]+)')


class CalculateStats:

    def __init__(self, trade_data: pd.DataFrame = None, pnl_data: pd.DataFrame = None, chunk: (int | str, None) = None):
        self.trade_data = trade_data
        self.pnl_data = pnl_data
        self.chuck_size = chunk

        self._stats_chunk = self._create_pnl_trade_data_chunks()
        self.stat_data = self._calc_stats()

    def _create_pnl_trade_data_chunks(self):
        pnl = CalculatePnL(trade_data=self.trade_data, pnl_data=self.pnl_data)
        pnl_data = pnl.pnl_data
        self.pnl_data = pnl_data
        logging.info(pnl_data)

        both_pnl_data = pnl_data.copy()
        both_pnl_data.direction = both_pnl_data.direction = 'BOTH'
        pnl_data = pd.concat([pnl_data, both_pnl_data], ignore_index=True)

        stats = []
        for direction in ['BOTH', 'LONG', 'SHORT']:
            df = pnl_data.query('direction == @direction')
            df = df.reset_index(drop=True)

            if isinstance(self.chuck_size, int):
                df['chuck_group'] = (df.index / self.chuck_size).astype(int) if self.chuck_size > 0 else 'ALL'

            elif isinstance(self.chuck_size, str):
                freq_int, freq_str = re_offset_time.findall(self.chuck_size)[0]
                freq_int = int(freq_int)

                offset_lookup = {'S': pd.offsets.Second(freq_int), 'Min': pd.offsets.Minute(freq_int),
                                 'H': pd.offsets.Hour(freq_int), 'D': pd.offsets.Day(freq_int),
                                 'W': pd.offsets.Week(freq_int, weekday=6), 'M': pd.offsets.MonthEnd(freq_int),
                                 'Y': pd.offsets.YearEnd(freq_int)}

                rounding_lookup = {'S': 'S', 'Min': 'T', 'H': 'H'}

                offset_func = offset_lookup.get(freq_str, pd.offsets.Week(0))
                rounding_func = rounding_lookup.get(freq_str, None)

                df['chuck_group'] = df.exit_time + offset_func
                if rounding_func:
                    df['chuck_group'] = df["chuck_group"].dt.round(rounding_func)
                else:
                    df['chuck_group'] = df["chuck_group"].dt.date

            elif isinstance(self.chuck_size, NoneType):
                df['chuck_group'] = 0

            stats.extend([d for _, d in df.groupby(['chuck_group'])])

        if not stats:
            pnl_data['chuck_group'] = 0
            stats.append(pnl_data)

        return stats

    @staticmethod
    def _map_reduce_stats(df):
        df['cumulative_return'] = df.pnl_with_commission.cumsum()

        try:
            chunk_size = df.chuck_group.unique()[0]
            direction = df.direction.unique()[0]

            winning = df[df.pnl_with_commission >= 0]
            losing = df[df.pnl_with_commission < 0]
            winning_count = len(winning)
            losing_count = len(losing)

        except IndexError:
            chunk_size = 0
            direction = 'BOTH'

            winning = df
            losing = df
            winning_count = 0
            losing_count = 0

        '''
            average_trade_time=pd.to_timedelta(df.time_to_live.dt.total_seconds().mean(), errors='coerce'),
            average_winning_time=pd.to_timedelta(winning.time_to_live.dt.total_seconds().mean(), errors='coerce'),
            average_losing_time=pd.to_timedelta(losing.time_to_live.dt.total_seconds().mean(), errors='coerce'),
            average_time_between_trades=pd.to_timedelta(
                (df['entry_time'].shift(-1) - df['exit_time']).dt.total_seconds().mean(), errors='coerce'),
            max_flat_time=pd.to_timedelta((df['entry_time'].shift(-1) - df['exit_time']).dt.total_seconds().max(),
                                          errors='coerce'), )
        '''

        try:
            sharpe_r = df[['exit_time', 'pnl_with_commission']].set_index('exit_time').groupby(
                pd.Grouper(freq='D')).sum().pnl_with_commission.cumsum().diff()
            sharpe_r = np.divide(sharpe_r.mean(), sharpe_r.std() * np.sqrt(252))
        except AttributeError:
            sharpe_r = np.nan

        stats = dict(
            net_profit=df.pnl_with_commission.sum(), gross_profit=winning.pnl_with_commission.sum(),
            gross_loss=losing.pnl_with_commission.sum(), total_commission=df.commission.sum(),
            max_drawdown=np.min(df.cumulative_return - np.maximum.accumulate(df.cumulative_return)),
            number_of_winning_trades=winning_count, number_of_losing_trades=losing_count,
            total_trade_count=winning_count + losing_count, largest_winning_trade=winning.pnl_with_commission.max(),
            largest_losing_trade=losing.pnl_with_commission.min(),
            average_winning_trade=winning.pnl_with_commission.mean(),
            average_losing_trade=losing.pnl_with_commission.mean(),
            average_mfe=df.mfe.mean(), average_mae=df.mae.mean(),
            average_winning_percentage=np.divide(winning_count, (winning_count + losing_count)),
            average_losing_percentage=np.divide(losing_count, (winning_count + losing_count)),
            profit_factor=np.divide(winning.pnl_with_commission.sum(), losing.pnl_with_commission.sum()) * -1,
            sharpe_ratio=sharpe_r,
            consecutive_winners=((df.pnl_with_commission >= 0) * ((df.pnl_with_commission >= 0).groupby(
                ((df.pnl_with_commission >= 0) != (df.pnl_with_commission >= 0).shift()).cumsum()).cumcount() + 1)).max(),
            consecutive_losers=((df.pnl_with_commission < 0) * ((df.pnl_with_commission < 0).groupby(
                ((df.pnl_with_commission < 0) != (df.pnl_with_commission < 0).shift()).cumsum()).cumcount() + 1)).max(),
            average_trade_time=df.time_to_live.mean(),
            average_winning_time=winning.time_to_live.mean(),
            average_losing_time=losing.time_to_live.mean(),
            average_time_between_trades=(df['entry_time'].shift(-1) - df['exit_time']).mean(),
            max_flat_time=(df['entry_time'].shift(-1) - df['exit_time']).max())

        num_cols = ['net_profit', 'gross_profit', 'gross_loss', 'total_commission', 'max_drawdown', 'largest_winning_trade',
                    'largest_losing_trade', 'average_winning_trade', 'average_losing_trade', 'average_mfe', 'average_mae']
        pct_cols = ['average_winning_percentage', 'average_losing_percentage', 'profit_factor', 'sharpe_ratio']

        stats = pd.DataFrame(stats, index=[(direction, chunk_size)])
        stats[num_cols] = stats[num_cols].round(2)
        stats[pct_cols] = stats[pct_cols].round(4)
        return stats

    def _calc_stats(self):

        dtypes = np.dtype(
            [('direction', 'object'), ('chunk', 'object'),
             ('net_profit', 'float64'), ('gross_profit', 'float64'), ('gross_loss', 'float64'),
             ('total_commission', 'float64'), ('max_drawdown', 'float64'),
             ('number_of_winning_trades', 'int64'), ('number_of_losing_trades', 'int64'),
             ('total_trade_count', 'int64'), ('largest_winning_trade', 'float64'),
             ('largest_losing_trade', 'float64'), ('average_winning_trade', 'float64'),
             ('average_losing_trade', 'float64'), ('average_mfe', 'float64'), ('average_mae', 'float64'),
             ('average_winning_percentage', 'float64'), ('average_losing_percentage', 'float64'),
             ('profit_factor', 'float64'), ('sharpe_ratio', 'float64'), ('consecutive_winners', 'int64'),
             ('consecutive_losers', 'int64'), ('average_trade_time', 'timedelta64[ns]'),
             ('average_winning_time', 'timedelta64[ns]'), ('average_losing_time', 'timedelta64[ns]'),
             ('average_time_between_trades', 'timedelta64[ns]'), ('max_flat_time', 'timedelta64[ns]')])

        df = pd.concat([self._map_reduce_stats(x) for x in
                        tqdm(self._stats_chunk, desc=f'Running stats calculation for chunk_size={self.chuck_size}')])
        df.index = pd.MultiIndex.from_tuples(df.index, names=['direction', 'chunk'])

        df = df.unstack('chunk')
        for direction in {'LONG', 'SHORT', 'BOTH'} - set(df.index):
            df.loc[direction] = np.nan

        df.total_trade_count = df.total_trade_count.fillna(0)
        df = df.stack('chunk')
        logging.info(df)
        return df
