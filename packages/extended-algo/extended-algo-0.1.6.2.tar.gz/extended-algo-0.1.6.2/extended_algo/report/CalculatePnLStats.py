import pandas as pd
from extended_algo.report.calculate.Stats import CalculateStats
from extended_algo.report.calculate.Features import GenerateFeatures, PnLDetails


class CalculatePnLStats:

    def __init__(self, trade_data: pd.DataFrame() = None, pnl_data: pd.DataFrame() = None,
                 features_data: (pd.DataFrame(), None) = None,
                 restrict_feature_cols: (set, list) = {},
                 feature_lookback_period=pd.offsets.Second(0),
                 feature_lookforward_period=pd.offsets.Second(0),
                 stats_chunk: (int, str, None) = None,
                 **kwargs):
        '''
        Report api that converts trade data with "BUY" and "SELL" entries to pnl data with "LONG" and "SHORT" positions
        Additional functionality allow for pnl position to be converted to chucked stats to allow for drift analysis
        And allows for supplementing a continuous-timeseries features data for entry and exit optimization

        :param trade_data: For backward compatability, will be deprecated in feature release
        :param pnl_data with headers [symbol, entry_time, exit_time, direction, entry_price, exit_price, quantity, commission, pnl_amount, pnl_with_commission]
        :param features_data:
        :param restrict_feature_cols: reduce the features to a subset of columns
        :param stats_chunk: int=chunk by trade count, str=chunk by time-freq, (ALL | 0)=consolidated, None=skip,
        :param kwargs: leading_seconds and trailing_seconds adds a buffer to the features data
        '''

        self.trade_data = trade_data
        self.pnl_data = pnl_data
        self._features_data = features_data
        self._restrict_features_cols = restrict_feature_cols
        self._stats_chunk = stats_chunk
        self._feature_lookback = feature_lookback_period
        self._feature_lookforward = feature_lookforward_period
        self.pnl_data, self.stats_data = self._calculate_pnl_and_stats()

        self._features = self._calculate_features()

    def get_feature(self, index: int) -> pd.DataFrame():
        return self._features.get_feature(index=index)

    def get_pnl(self, index: int) -> PnLDetails:
        return self._features.get_pnl(index=index)

    def _calculate_pnl_and_stats(self):
        stats = CalculateStats(trade_data=self.trade_data, pnl_data=self.pnl_data, chunk=self._stats_chunk)
        return stats.pnl_data, stats.stat_data

    def _calculate_features(self):
        features = GenerateFeatures(pnl_data=self.pnl_data, features_data=self._features_data,
                                    columns=self._restrict_features_cols, feature_lookback_period=self._feature_lookback,
                                    feature_lookforward_period=self._feature_lookforward)

        self.pnl_data = features.pnl_data
        return features
