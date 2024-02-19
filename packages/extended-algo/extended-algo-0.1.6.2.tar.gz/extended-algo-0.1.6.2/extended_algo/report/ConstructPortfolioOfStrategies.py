import logging, time, os
import pandas as pd
import numpy as np
import datetime as dt
from pathlib import Path
from extended_algo.report.calculate.Stats import CalculateStats
from extended_chart import ExtendedChart, add_overlay
from extended_chart.add_table import add_stats_table
from extended_chart.style import black_background

pd.set_option('display.width', 1000, 'display.max_columns', 1000)

# THere is some issue with
class ConstructPortfolioOfStrategies:

    def __init__(self, *paths, stats_chunk: (int, str, None) = None, **kwargs):
        self.paths = paths
        self.stats_chunk = stats_chunk

        self.equity_curves, self.pnl_data = self._consolidate_trades()
        self.stats_data = self._consolidate_stats()

    def _consolidate_trades(self):
        # TODO: There looks to be a bug with cumsum for pandas that needs to be resolved
        trade_data = []
        equities_data = []
        for p in self.paths:
            strategy_name = p.parts[-2]
            p = p if isinstance(p, Path) else Path(p)
            _df = pd.read_pickle(p / 'pnl_data.p')
            trade_data.append(_df)

            _df[strategy_name] = _df.pnl_with_commission
            _df = _df.groupby(pd.Grouper(freq='D', key='exit_time')).agg({strategy_name: 'sum'})
            equities_data.append(_df)

        pnl_data = pd.concat(trade_data)
        equities_data = pd.concat(equities_data, axis=1)
        equities_data = equities_data.cumsum()
        equities_data['Consolidated'] = equities_data.sum(axis=1)


        return equities_data, pnl_data

    def _consolidate_stats(self):
        stats = CalculateStats(pnl_data=self.pnl_data, chunk=100_000_000_000_000)
        stats = stats.stat_data
        return stats


class RenderPortfolioStrategiesChart:

    def __init__(self, obj:ConstructPortfolioOfStrategies):

        self.equity_overlays = obj.equity_curves
        self.stats_data = obj.stats_data

    def show(self):
        chart = ExtendedChart(title='Consolidated Portfolio View', inner_width=0.72, width=1200, height=600)
        chart = black_background(chart)

        equity = self.equity_overlays.fillna(method='ffill')
        equity = equity.fillna(0)
        equity = equity.reset_index()
        equity = equity.rename(columns={'exit_time':'datetime'}).set_index('datetime')

        equity_consolidated = equity[['Consolidated']]
        equity_consolidated['color'] = '#e1fe01'

        add_overlay(chart, data=equity.drop('Consolidated', axis=1), style='dashed')
        add_overlay(chart, data=equity_consolidated, width=1)
        chart.set_visible_range(start_time=equity.index.min(), end_time=equity.index.max())

        table = add_stats_table(chart,data=self.stats_data, width=0.28)
        table.header(1)
        table.header[0] = 'Consolidated'

        # TODO: I need a way to switch between stats. Leave on Consolidated for now
        table.footer(2)
        table.footer[0] = '<<'
        table.footer[1] = '>>'

        chart.show(True)
