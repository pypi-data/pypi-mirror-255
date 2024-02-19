from collections import namedtuple
import pandas as pd
# import numpy as np
from extended_algo.market import load_symbol_lookup
from extended_algo.report.calculate.MaeMfe import MaxFavorableAdverseExcursion

# TODO: I may want to deprecate _split_to_buy_sell_stack and _run_pnl_cal and opt for vector calc of pnl
TradeDetail = namedtuple('TradeDetail', 'datetime symbol action price quantity commission')
PnLDetail = namedtuple('PnLDetail', 'symbol entry_time exit_time direction entry_price exit_price quantity commission')


class CalculatePnL:

    def __init__(self, trade_data: pd.DataFrame = None, pnl_data: pd.DataFrame = None):
        self.trade_data = trade_data
        self.pnl_data = pnl_data
        self.symbol_lookup = load_symbol_lookup()

        # if self.trade_data and not pnl_data:
        #     self._buy_stack = []
        #     self._sell_stack = []
        #     self._split_to_buy_sell_stack()
        #     self.pnl_data = self._run_pnl_calc()

        self.pnl_data = self._run_mae_mfe_calc()


    # def _split_to_buy_sell_stack(self):
    #     self.trade_data = self.trade_data.sort_values('datetime', ascending=False)
    #
    #     buy_stack = self.trade_data.query('action.str.upper() == "BUY"')
    #     sell_stack = self.trade_data.query('action.str.upper() == "SELL"')
    #
    #     cols = ['datetime', 'symbol', 'action', 'price', 'quantity', 'commission']
    #     self._buy_stack = list(buy_stack[cols].itertuples(name="TradeDetail", index=False))
    #     self._sell_stack = list(sell_stack[cols].itertuples(name="TradeDetail", index=False))
    #
    # def _run_pnl_calc(self):
    #
    #     pnl_stack = []
    #     while len(self._buy_stack) > 0 and len(self._sell_stack) > 0:
    #         _buy_trade = self._buy_stack.pop()
    #         _sell_trade = self._sell_stack.pop()
    #
    #         entry_symbol = _buy_trade.symbol
    #         if _buy_trade.datetime <= _sell_trade.datetime:
    #             entry_direction = 'LONG'
    #             entry_time = _buy_trade.datetime
    #             entry_price = _buy_trade.price
    #             exit_time = _sell_trade.datetime
    #             exit_price = _sell_trade.price
    #         else:
    #             entry_direction = 'SHORT'
    #             entry_time = _sell_trade.datetime
    #             entry_price = _sell_trade.price
    #             exit_time = _buy_trade.datetime
    #             exit_price = _buy_trade.price
    #
    #         if _buy_trade.quantity == _sell_trade.quantity:
    #             closed_quantity = _buy_trade.quantity
    #             total_commission = _buy_trade.commission + _sell_trade.commission
    #         else:
    #             closed_quantity = min(_sell_trade.quantity, _buy_trade.quantity)
    #             remaining_quantity = int(max(_buy_trade.quantity, _sell_trade.quantity) - closed_quantity)
    #             total_commission = min(_buy_trade.commission, _sell_trade.commission) * 2
    #             remaining_commission = round(_buy_trade.commission + _sell_trade.commission - total_commission, 2)
    #             remaining_trade = TradeDetail(
    #                 symbol=entry_symbol,
    #                 datetime=_buy_trade.datetime if _buy_trade.quantity > _sell_trade.quantity else _sell_trade.datetime,
    #                 action=_buy_trade.action if _buy_trade.quantity > _sell_trade.quantity else _sell_trade.action,
    #                 price=_buy_trade.price if _buy_trade.quantity > _sell_trade.quantity else _sell_trade.price,
    #                 quantity=remaining_quantity, commission=remaining_commission)
    #
    #             if _buy_trade.quantity > _sell_trade.quantity:
    #                 self._buy_stack.append(remaining_trade)
    #             else:
    #                 self._sell_stack.append(remaining_trade)
    #
    #         pnl_stack.append(
    #             PnLDetail(symbol=entry_symbol, entry_time=entry_time, exit_time=exit_time, entry_price=entry_price,
    #                       exit_price=exit_price, direction=entry_direction, quantity=closed_quantity,
    #                       commission=total_commission))
    #
    #     pnl = pd.DataFrame(pnl_stack)
    #     pnl['pnl_tick'] = pnl.exit_price - pnl.entry_price
    #     pnl['pnl_tick'] = np.where(pnl.direction == 'SHORT', pnl.pnl_tick * -1, pnl.pnl_tick)
    #     pnl['time_to_live'] = pnl.exit_time - pnl.entry_time
    #     pnl['pnl_amount'] = pnl.pnl_tick * pnl.symbol.apply(lambda x: self.symbol_lookup.get(x).multiplier) * pnl.quantity
    #     pnl['pnl_with_commission'] = pnl.pnl_amount - pnl.commission
    #
    #     return pnl

    def _run_mae_mfe_calc(self):
        data = MaxFavorableAdverseExcursion(self.pnl_data)

        return data.pnl_data
