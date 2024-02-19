from dataclasses import dataclass, asdict
from enum import Enum
from pandas.tseries import offsets
import datetime as dt
import pandas as pd
from uuid import uuid1
import numpy as np


class Action(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class OrderType(Enum):
    MKT = 'MKT'
    STP = 'STP'
    LMT = 'LMT'


class Entries:
    def __init__(self, *args, oco=False):
        self.orders = []
        self.oco_id = None
        if oco:
            self.oco_id = uuid1()

        for o in args:
            self.add(o)

    def add(self, other):
        if isinstance(other, Order):
            self.orders.append({'oco_id': self.oco_id, 'entries': other})
        else:
            raise TypeError('Not OrderDetails Object!')

    def __repr__(self):
        return f'OCOEntries({self.orders})'

    def __len__(self):
        return len(self.orders)


@dataclass(slots=True)
class Order:
    signal_time: (dt.datetime | pd.Timestamp)
    action: (Action | None)
    signal_px: (float | None) = None
    quantity: int = 1

    order_type: OrderType | None = OrderType.MKT
    signal_ttl: (offsets.DateOffset, dt.time, None) = pd.offsets.Minute(30)
    profit_target_px: float = np.nan
    stoploss_px: float = np.nan

    breakeven_trigger_px: float | bool = False
    breakeven_stoploss_px = float = np.nan

    closeout_ttl: (offsets.DateOffset, dt.time, None) = pd.NaT  # pd.offsets.Hour(1)

    def __repr__(self):
        return f'Order({self.action.value} {self.quantity} @ {self.signal_px} {self.order_type.value})'
