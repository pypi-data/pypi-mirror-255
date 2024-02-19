from extended_algo.report.CalculatePnLStats import CalculatePnLStats
import pandas as pd


def create_consolidated_stats(strategy_obj):
    s_consolidated = CalculatePnLStats(pnl_data=strategy_obj.pnl_data, features_data=strategy_obj.features_data,
                                       stats_chunk=None, restrict_feature_cols=strategy_obj.restrict_feature_cols,
                                       feature_lookback_period=strategy_obj.feature_lookback_period,
                                       feature_lookforward_period=strategy_obj.feature_lookforward_period)

    s_chunk = CalculatePnLStats(pnl_data=strategy_obj.pnl_data, features_data=strategy_obj.features_data,
                                stats_chunk=strategy_obj.stats_chunk,
                                restrict_feature_cols=strategy_obj.restrict_feature_cols,
                                feature_lookback_period=strategy_obj.feature_lookback_period,
                                feature_lookforward_period=strategy_obj.feature_lookforward_period)

    s_consolidated = s_consolidated.stats_data

    s_chunk = s_chunk.stats_data
    s_chunk.index = s_chunk.index.set_levels(s_chunk.index.levels[1] + 1, level=1)

    stats = pd.concat([s_consolidated, s_chunk])

    return stats
