import logging
import pandas as pd
from pandas import DataFrame
import numpy as np
from collections import namedtuple
from types import NoneType

PnLDetails = namedtuple(
    'PnLDetails',
    ['symbol', 'entry_time', 'exit_time', 'direction', 'entry_price', 'exit_price', 'quantity', 'commission', 'pnl_tick',
     'time_to_live', 'pnl_amount', 'pnl_with_commission', 'mfe', 'mfe_time', 'mae', 'mae_time'])


class GenerateFeatures:

    def __init__(self, pnl_data, features_data: (DataFrame, None), columns: (set, list) = set(),
                 feature_lookback_period=pd.offsets.Second(0), feature_lookforward_period=pd.offsets.Second(0)):

        logging.info('Generating features against supplied timeseries')
        self._feature_lookback = feature_lookback_period
        self._feature_lookforward = feature_lookforward_period

        self._feature_cols, self._features_data = self._restricted_features(columns, features_data)

        self.pnl_data = pnl_data
        self.pnl_data['features'] = self._explode_features()
        self.pnl_data = self.pnl_data.drop(['leading_entry_time', 'trailing_exit_time'], axis=1)

        self._feature_detail = self._generate_feature_dict()

    @staticmethod
    def _restricted_features(cols, features):
        if isinstance(features, NoneType) or features.empty:
            dtypes = np.dtype([('datetime', 'datetime64[ns]')])
            return None, pd.DataFrame(np.empty(0, dtype=dtypes))

        # close_p will allow for MTM calculation for improved profit factor calculation
        cols = set(cols)
        cols.add('datetime')
        cols.add('close_p')
        cols = list(cols)

        features = features[cols]
        return cols, features

    def _explode_features(self):
        df = self.pnl_data
        df['leading_entry_time'] = df.entry_time - self._feature_lookback
        df['trailing_exit_time'] = df.exit_time + self._feature_lookforward
        df = df.apply(lambda x: self._calc_feature(x), axis=1)
        return df

    def _calc_feature(self, x):
        df = self._features_data.query('datetime >= @x.leading_entry_time and datetime <= @x.trailing_exit_time')
        return df.to_numpy(), df.columns

    def _generate_feature_dict(self):
        # TODO: This only implies the label can be added if the features datetime is the same as timeframe used
        #  to generate entries, mfe, mae. Therefore I need to revisit this with varying timeframes and models
        #  maybe the closes ceil time acts as the marker

        # TODO: Looping this through this and exploding may not be the optimal case, to to parallelize
        pnl_entry_features = dict()
        for x in self.pnl_data[['entry_time', 'exit_time', 'mfe_time', 'mae_time', 'features']].itertuples():
            df = pd.DataFrame(x.features[0], columns=x.features[1])

            # TODO: The issue here is that an entry, exit, mfe, mae can all be on the same record
            df['label'] = np.where(df.datetime == x.entry_time, 'ENTRY', np.nan)
            df.label = np.where(df.datetime == x.exit_time, 'EXIT', df.label)
            df.label = np.where(df.datetime == x.mfe_time, 'MFE', df.label)
            df.label = np.where(df.datetime == x.mae_time, 'MAE', df.label)

            df = df.set_index('datetime')
            pnl_entry_features[x.Index] = df

        return pnl_entry_features

    def get_pnl(self, index: int) -> PnLDetails:
        pnl_data = self.pnl_data.drop('features', axis=1)
        pnl_data = pnl_data.iloc[index] if index in pnl_data.index.values else pd.Series(index=pnl_data.columns)
        return PnLDetails(*pnl_data)

    def get_feature(self, index: int) -> DataFrame:
        return self._feature_detail.get(index, pd.DataFrame(columns=self._feature_cols))
