from abc import ABC, abstractmethod
import logging
import datetime as dt
import pandas as pd
import numpy as np
from pathlib import Path
from extended_algo.market.utils.common import MarketDataType
from extended_algo.market import MarketData
from extended_algo.market import load_symbol_lookup
from extended_algo.engine.create_audit_file import create_audit_file
from extended_algo.engine.create_consolidated_stats import create_consolidated_stats
from extended_algo.engine.create_stop_entries import create_stop_entries
from extended_algo.engine.create_limit_entries import create_limit_entries
import inspect
from tqdm import tqdm
from extended_algo import OrderType
from pandas.tseries import offsets
import dataclasses
from uuid import uuid1


class VectorStrategy(ABC):

    # TODO: I need to rename the breakeven_tigger

    def __init__(self, symbol: str, start: dt.datetime, end: dt.datetime, profit_target=100., stop_loss=100.,
                 breakeven_trigger: float = None, breakeven_stop_loss=0.,
                 closeout_ttl: (offsets.DateOffset | dt.time) = pd.offsets.Hour(1),
                 signal_ttl: offsets.DateOffset = pd.offsets.Hour(1),

                 market_data_type=MarketDataType.TIME,
                 market_freq='5Min',
                 market_lookback_period=pd.offsets.Day(0),
                 market_lookforward_period=pd.offsets.Day(0),
                 market_use_cache=True,
                 market_agg_consecutive_last_px=True,

                 restrict_feature_cols=[],
                 feature_lookback_period=pd.offsets.Second(0),
                 feature_lookforward_period=pd.offsets.Second(0),

                 save_dir_root: Path = None, override_strategy_name: str = None, chunk_stats: int = None, **kwargs):
        '''

        :param symbol: References the traded symbol (iqfeed symbol name)
        :param start: Datetime of when to start strategy run
        :param end: Datetime of when to end strategy run

        :param profit_target: Force profit target exit
        :param stop_loss: Force stop loss exit
        :param breakeven_tigger(o): Adjust stop loss when price moves in favor and exceeds breakeven price
        :param breakeven_stop_loss: Requires price to exceed breakeven trigger for stop loss to be adjusted to breakeven price
        :param closeout_ttl: pd.offsets(..) generates closeout offsetting signal time; However time forces a hard closeout at time

        :param market_data_type: Market data type [TIME, TICKS, TICK_COUNT, TICK_VOLUME, TICK_DOLLAR, TICK_RANGE]
        :param market_freq: Bar close frequency
        :param market_use_cache: Speed up strategy discovery process by caching market data for strategy window
        :param market_agg_consecutive_last_px: Forced True, aggregate tick data on consecutive last px
        :param market_lookback_period: provide inactive lookback market data to prime strategy window
        :param market_lookforward_period: provide inactive lookforward market data to close open position

        :param restrict_feature_cols: Restrict the columns that are tracked in the pnl data
        :param feature_lookback_period: Provides leading features data for entry analysis
        :param feature_lookforward_period: Provides trailing features data for exit analysis
        :param save_dir_root: Override default location where strategy metadata are saved
        :param override_strategy_name: Override the strategy name
        :param chunk_stats: Generate stats in fixed chunks for decay analysis
        '''

        self.strategy_name = self.__class__.__name__ if not override_strategy_name else override_strategy_name
        self.symbol = symbol

        assert (sym_detail := load_symbol_lookup().get(self.symbol)), f'Symbol details not defined for: {self.symbol}'
        self.sym_detail = sym_detail

        if not save_dir_root:
            self.save_dir = Path(inspect.getfile(self.__class__)).parent / self.strategy_name / self.symbol
        else:
            save_dir_root = save_dir_root if isinstance(save_dir_root, Path) else Path(save_dir_root)
            self.save_dir = save_dir_root / self.strategy_name / self.symbol

        self.save_dir.mkdir(exist_ok=True, parents=True)

        self.start = start
        self.end = end
        self.stats_chunk = chunk_stats

        self.market_data_type = market_data_type
        self.market_freq = market_freq
        self.market_use_cache = market_use_cache
        self.market_lookback_period = market_lookback_period
        self.market_lookforward_period = market_lookforward_period
        self.market_agg_consecutive_last_px = market_agg_consecutive_last_px

        self.profit_target = profit_target
        self.breakeven_trigger = breakeven_trigger
        self.breakeven_stop_loss = breakeven_stop_loss
        self.stop_loss = stop_loss
        self.closeout_ttl = closeout_ttl
        self.signal_timeout = signal_ttl

        self.restrict_feature_cols = set(restrict_feature_cols)
        self.feature_lookback_period = feature_lookback_period
        self.feature_lookforward_period = feature_lookforward_period
        self.kwargs = kwargs

        logging.info(f'Running {self.strategy_name} | {self.symbol} from {self.start} - {self.end}')

        self.market_data = self._get_tradeable_market_data()
        self.features_data = pd.DataFrame()
        self.signal_data = self.market_data.copy()

    def _get_tradeable_market_data(self):
        market = MarketData(market_data_type=self.market_data_type, symbol=self.symbol, start=self.start, end=self.end,
                            freq=self.market_freq, use_cache=self.market_use_cache,
                            agg_consecutive_last_px=self.market_agg_consecutive_last_px,
                            lookback_period=self.market_lookback_period, lookforward_period=self.market_lookforward_period)

        market = market.data
        market = market.set_index('datetime')
        return market

    @abstractmethod
    def signal(self) -> pd.DataFrame(columns=['signal']):
        # TODO: This helper statement needs to be updated to reflect MKT, STP, LMT as well ad dynamic PT SL and BT offsets
        raise NotImplementedError('''
            Must return dataframe with datetime index and signal column

            Provide logic for generating trading signal by leveraging df = self.signal_data
            The signal dataframe must contain the following as a minimum
            signal (-1 = NEW SHORT TRADE | 1 = NEW LONG TRADE | 0 = NO ACTION ) as the inception of the trade
            quantity is always defaulted to 1/lot sizes based on commission.
            to implement a scalp and swing strategy, implement separately and consolidate using ConstructPortfolioOfStrategies

            ''')

    def _explode_oco_entries(self):
        df = self.signal_data
        assert 'signal' in df.columns, 'Signal column missing, please set [-1=SHORT, 1=LONG] for abstract method signal()\n' \
                                       'Advanced entry pattern are available by "providing" entries column with ' \
                                       'Entries(Order, Order....Order, oco=False)'

        # TODO: I need to change the assert statement and make a function that applies entries_oco columns or equivalent
        #  I also need to verify clean-up this backward compatibility issue

        # TODO: There should be an assert statement that indicated which columns should not be used by the end-user
        #  as it is required fields for the Entries Object
        try:
            df.set_index('datetime', inplace=True)
        except:
            pass

        df = df[df.is_live == 1]
        df = df[df.signal != 0]
        df = df[~df.signal.isnull()]

        try:
            df['entries'] = df.entries.apply(lambda x: x.orders)
            df = df.explode('entries')
            df['oco_id'] = df.entries.apply(lambda x: x.get('oco_id'))
            df['entries'] = df.entries.apply(lambda x: x.get('entries'))

            df = pd.concat([df, df.entries.apply(dataclasses.asdict).apply(pd.Series)], axis=1)

            df['signal'] = df['action'].apply(lambda x: {'BUY': 1, 'SELL': -1}.get(x.value))

            df['pt_offset'] = df.profit_target_px
            df['sl_offset'] = df.stoploss_px
            df['bt_offset'] = df.breakeven_trigger_px

            df['entry_type'] = df.order_type
            df['entry_price'] = df.signal_px
            df['signal_timeout'] = df.signal_ttl

            df['empty_oco_id'] = df.oco_id.apply(lambda x: uuid1())
            df['oco_id'] = np.where(df.oco_id.isnull(), df.empty_oco_id, df.oco_id)
            df = df.drop(['empty_oco_id'], axis=1)
        except:
            df['oco_id'] = np.nan
            df['signal_time'] = df.index

        return df

    def _calculate_sl_pt_bt_bsl(self, df):
        # TODO: This part of the code is getting really messy, and I think I need to extract it out once done
        if 'pt_offset' not in df.columns:
            df['pt_offset'] = self.profit_target
        df['pt_offset'] = df['pt_offset'].fillna(self.profit_target)
        df['pt_offset'] = df['pt_offset'].apply(lambda x: ((x // self.sym_detail.tick_size) * self.sym_detail.tick_size))
        df['pt_offset'] = np.where(df.pt_offset <= 0, 0, df.pt_offset)

        df['pt'] = np.where((df.signal == -1), df.entry_price - df.pt_offset, np.nan)
        df['pt'] = np.where((df.signal == 1), df.entry_price + df.pt_offset, df.pt)

        if 'sl_offset' not in df.columns:
            df['sl_offset'] = self.stop_loss
        df['sl_offset'] = df['sl_offset'].fillna(self.stop_loss)
        df['sl_offset'] = df['sl_offset'].apply(lambda x: ((x // self.sym_detail.tick_size) * self.sym_detail.tick_size))
        df['sl_offset'] = np.where(df.sl_offset <= 0, 0, df.sl_offset)

        df['sl'] = np.where((df.signal == -1), df.entry_price + df.sl_offset, np.nan)
        df['sl'] = np.where((df.signal == 1), df.entry_price - df.sl_offset, df.sl)

        for x in ['bt_offset', 'bsl_offset', 'bt', 'bsl']:
            if x not in df.columns:
                df[x] = np.nan

        if self.breakeven_trigger:
            # If breakeven stoploss price is greater than breakeven trigger, set it to breakeven trigger price
            #  As this case is not a valid condition. I was debating between setting bt_offset to 0

            df['bt_offset'] = np.where(df['bt_offset'].isin([True, False]), self.breakeven_trigger, df['bt_offset'])
            df['bsl_offset'] = df['bsl_offset'].fillna(self.breakeven_stop_loss)

            df['bt_offset'] = np.where(df.bt_offset <= 0, 0, df.bt_offset)
            df['bsl_offset'] = np.where(df.bsl_offset <= 0, 0, df.bsl_offset)
            df['bsl_offset'] = np.where(df.bsl_offset >= df.bt_offset, df.bt_offset, df.bsl_offset)

            df['bt'] = np.where(df.signal == -1, df.entry_price - df.bt_offset, np.nan)
            df['bt'] = np.where(df.signal == 1, df.entry_price + df.bt_offset, df.bt)

            df['bsl'] = np.where(df.signal == -1, df.entry_price - df.bsl_offset, np.nan)
            df['bsl'] = np.where(df.signal == 1, df.entry_price + df.bsl_offset, df.bsl)

        if isinstance(self.closeout_ttl, (offsets.DateOffset | dt.timedelta)):
            df['forced_closeout'] = df.entry_time + self.closeout_ttl
        elif isinstance(self.closeout_ttl, dt.time):
            df['forced_closeout'] = df.entry_time.apply(lambda x: dt.datetime.combine(x, self.closeout_ttl))

        tqdm.pandas(desc='Calculating exit condition')
        try:
            df['exit'] = df.progress_apply(self._generate_mfe_mae_stats, axis=1)
            df[['exit_price', 'exit_time', 'exit_type', 'bt_trigger_time']] = pd.DataFrame(df.exit.tolist(), index=df.index)
            df = df.drop('exit', axis=1, errors='ignore')
        except:
            df['exit_price'] = np.nan
            df['exit_time'] = pd.NaT
            df['exit_type'] = ""
            df['bt_trigger_time'] = pd.NaT

        return df

    def _generate_mfe_mae_stats(self, x):
        # TODO: Need a way of dynamically exiting the position in profit or in loss based on a threshold m['4_threshold']

        try:
            m = self.market_data[x.entry_time:][['high_p', 'low_p', 'close_p']]
            m = m.loc[m.index <= x.forced_closeout]
            m = m.iloc[1:]

            m['1_sl_exit'] = np.where(((x.signal == -1) & (m.high_p >= x.sl)) |
                                      ((x.signal == 1) & (m.low_p <= x.sl)), x.sl, np.nan)
            m['2_pt_exit'] = np.where(((x.signal == -1) & (m.low_p <= x.pt)) |
                                      ((x.signal == 1) & (m.high_p >= x.pt)), x.pt, np.nan)
            m['3_cl_exit'] = np.nan
            m.loc[m.index[-1],'3_cl_exit'] = m.iloc[-1]['close_p']

            if self.breakeven_trigger:
                m['4_bsl_exit'] = np.where(((x.signal == -1) & (m.high_p >= x.bsl)) |
                                           ((x.signal == 1) & (m.low_p <= x.bsl)), x.bsl, np.nan)
                m['5_bt_exit'] = np.where(((x.signal == -1) & (m.low_p <= x.bt)) |
                                          ((x.signal == 1) & (m.high_p >= x.bt)), x.bt, np.nan)
                m['5_bt_exit'] = m['5_bt_exit'].fillna(method='ffill')
                m['4_bsl_exit'] = np.where(m['5_bt_exit'].isnull(), np.nan, m['4_bsl_exit'])

                try:
                    bt_tigger_time = m[m['5_bt_exit'].notna()].index[0]
                except KeyError:
                    bt_tigger_time = pd.NaT
            else:
                bt_tigger_time = pd.NaT

            exit_cols = ['1_sl_exit', '2_pt_exit', '3_cl_exit']
            if self.breakeven_trigger:
                exit_cols.append('4_bsl_exit')

            m.drop_duplicates(exit_cols, inplace=True)
            m = m.drop('5_bt_exit', axis=1, errors='ignore')
            m.dropna(thresh=4, inplace=True)

            exit = m.iloc[0][exit_cols].sort_index().dropna().reset_index()
            exit['index'] = exit['index'].map(
                {'1_sl_exit': 'stop_loss', '3_cl_exit': 'close_out', '2_pt_exit': 'profit_target', '4_bsl_exit': 'breakeven'})

            exit_type = exit.iloc[0][0]
            exit_price = exit.iloc[0][1]
            exit_time = exit.columns[1]

            if exit_time < bt_tigger_time:
                bt_tigger_time = pd.NaT

            return [exit_price, exit_time, exit_type, bt_tigger_time]

        except (IndexError, ValueError):
            logging.info(f'   - Could not compute exit stats for the following timestamp {x.name}')
            return [np.nan, np.nan, np.nan]

    def _apply_stoploss_and_profit_targets(self):
        # TODO: Clean up all the if-else statement once that I used to rush the implementation of MTK, LMT, STP orders

        df = self.signal_data
        assert 'signal' in df.columns, 'signal column missing, please set [-1=SHORT, 1=LONG] for abstract method signal() '

        try:
            df.set_index('datetime', inplace=True)
        except:
            pass
        df = df[df.is_live == 1]
        df = df[df.signal != 0]
        df = df[~df.signal.isnull()]

        if 'signal_timeout' not in df.columns:
            df['signal_timeout'] = self.signal_timeout
        df['signal_timeout'] = df['signal_timeout'].fillna(self.signal_timeout)
        df['signal_timeout'] = df.signal_time + df.signal_timeout

        if 'entry_type' in df.columns:
            df_stop_entries = df[df.entry_type == OrderType.STP].copy()
            df_limit_entries = df[df.entry_type == OrderType.LMT].copy()

            df = df[~df.index.isin(df_stop_entries.index)]
            df = df[~df.index.isin(df_limit_entries.index)]

            df['entry_price'] = df.close_p

            df_stop_entries = create_stop_entries(self, df_stop_entries)
            df_limit_entries = create_limit_entries(self, df_limit_entries)

            df = pd.concat([df, df_stop_entries, df_limit_entries])
            if 'entry_time' not in df.columns:
                df['entry_time'] = pd.NaT
            df['entry_time'] = np.where(df.entry_time.isnull(), df.index, df.entry_time)
            df['entry_type'] = df.entry_type.apply(lambda x: x.value)

        else:
            print('\n\nI HAVE HIT THE ENTRY_PRICE EXCEPTION\n')
            df['entry_price'] = df.close_p
            df['entry_time'] = df.index
            df['entry_type'] = 'MKT'
            df['signal_timeout'] = pd.NaT



        df = self._calculate_sl_pt_bt_bsl(df)

        logging.info(df)
        return df

    def _calc_trades(self):
        df = self.signal_data

        df['symbol'] = self.symbol
        df['quantity'] = self.kwargs.get('quantity', 1)
        df['tick_multiplier'] = self.sym_detail.multiplier
        df['commission'] = df.quantity * self.sym_detail.commission
        df['direction'] = df.signal.map({-1: 'SHORT', 1: 'LONG'})
        df['commission'] = df.quantity * self.sym_detail.commission * 2
        df['pnl_tick'] = df.exit_price - df.entry_price
        df['pnl_tick'] = np.where(df.direction == 'SHORT', df.pnl_tick * -1, df.pnl_tick)
        df['time_to_live'] = df.exit_time - df.entry_time
        df['pnl_amount'] = (df.exit_price - df.entry_price) * self.sym_detail.multiplier
        df['pnl_amount'] = np.where(df.direction == 'SHORT', df.pnl_amount * -1, df.pnl_amount)
        df['pnl_with_commission'] = df.pnl_amount - df.commission

        # Drop duplicated OCO orders, keep the first entry,
        # if there are two entries on the same price, penalize by taking the works trade
        df = df.sort_values(['entry_time', 'pnl_tick'], ascending=[True, True])
        try:
            df = df.drop_duplicates('oco_id', keep='first')
        except KeyError:
            ...

        df = df[
            ['symbol', 'entry_type', 'signal_time', 'signal_timeout', 'entry_time', 'exit_time', 'direction', 'entry_price',
             'exit_price', 'quantity', 'commission', 'pnl_tick', 'time_to_live', 'pnl_amount', 'pnl_with_commission',
             'exit_type', 'pt', 'sl', 'bt', 'bsl', 'forced_closeout', 'bt_trigger_time']]
        df = df.reset_index(drop=True)


        return df

    def run(self):
        s = dt.datetime.now()
        self.signal_data = self.signal()
        self.features_data = self.signal_data.reset_index().copy()

        self.market_data.to_pickle(self.save_dir / 'market_data.p')
        self.features_data.to_pickle(self.save_dir / 'features_data.p')

        assert 'signal' in self.signal_data.columns, '"signal" column not defined in signal()!'
        logging.info(f'Signals generated from Strategy\n{self.signal_data[self.signal_data.signal.abs() >= 1]}')

        self.signal_data = self._explode_oco_entries()
        self.signal_data = self._apply_stoploss_and_profit_targets()
        self.pnl_data = self._calc_trades()
        self.stats_data = create_consolidated_stats(self)  # Note stats will update self.pnl_data

        # print('\n', self.pnl_data[
        #     ['entry_type', 'signal_time', 'direction', 'entry_time', 'entry_price', 'pt', 'sl', 'bt', 'bt_trigger_time', 'bsl',
        #      'exit_time', 'exit_price', 'exit_type', 'forced_closeout', 'signal_timeout', 'mfe', 'mfe_time', 'mae',
        #      'mae_time']].T)

        self.signal_data.to_pickle(self.save_dir / 'signal_data.p')
        self.pnl_data.to_pickle(self.save_dir / 'pnl_data.p')
        self.stats_data.to_pickle(self.save_dir / 'stats_data.p')

        create_audit_file(self)

        e = dt.datetime.now()
        logging.info(f'Saving {self.__class__.__name__} strategy details...\n{self.save_dir}')
        logging.info(f'Elapsed time: {e - s}')
