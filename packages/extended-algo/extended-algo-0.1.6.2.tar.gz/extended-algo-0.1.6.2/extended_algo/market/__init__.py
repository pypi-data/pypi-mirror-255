from .utils.symbol_lookup import load_symbol_lookup
from .utils.common import MarketDataType, MarketSource
from .utils.resample_market_data import resample_market_data

# TODO: Currently I am only supporting IQFEED FEATHER DATA
#  there is a utility in market.utils.move_remote_to_local that takes data from aws_backup folder
#  and moves it to the local staging folder as a feather format

# TODO: I think I need to revisit the rounding logic I have for bar completion as freq should be exceeded before bar closes

# TODO: I may want to change the lookback period to be in number of days instead of  pd.offset.X option

from extended_algo.market.MarketData import MarketData
from extended_algo.market.LogReturnMarketData import LogReturnMarketData

