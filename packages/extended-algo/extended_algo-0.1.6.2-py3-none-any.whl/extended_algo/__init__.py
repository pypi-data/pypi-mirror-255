from dotenv import load_dotenv
import pandas as pd
import warnings

pd.set_option('display.width', 1000, 'display.max_columns', 1000)

load_dotenv()
warnings.filterwarnings('ignore')

from extended_algo.report.CalculatePnLStats import CalculatePnLStats
from extended_algo.market.MarketData import MarketData, MarketDataType

from extended_algo.report.ConstructPortfolioOfStrategies import ConstructPortfolioOfStrategies, RenderPortfolioStrategiesChart

# TODO: Currently symbol lookup details are hardcoded, needs to be configurable in an external file
#  does not impact vector strategy generation

from extended_algo.market import load_symbol_lookup
from extended_algo.market import resample_market_data

# TODO: Implement LIMIT and STOP order entries on x bars in the past with entry offset
#  Currently VectorStrategy enters on MARKET order on bar-close

# TODO; Implement dynamic stop-loss, profit-target and breakeven-triggers based on secondary trade-management signal data

# TODO: market_data.p and feature_data.p has duplicate data, removing the duplication requires extended_chart to be fixed also

# TODO: Implemented multi-process package that allows you to fork and parallelize both vector and event based signal generation
#  My implementing a leading and trailing market data period where trades can't be entered bu only closed
#  You would be able to split, compute, and stitch the feature_data, pnl_table and stats_table together

# TODO: leading and trailing feature parameters are not exposed to vector strategy; needs to be kwargs

# TODO: Refine metadata.json with practice, might want to implement feature that allows you to add methods for tracking
#  Keep track of feature_data.p and pnl_data.p as an version object, with path referenced in metadata.json
#  expose key metric like markdown, sharpie on record level, and not nested in stats_data for global strategy compare

# TODO: There is an issue with self.__variable__ defined in child class of VectorStategy being exported in metadata.json file
#  Change the logic to be explict on what gets tracked:
#  (1) *args and **kwargs defined in child class __init__, signal
#  (2) explicity declared params and functions


# TODO: I would like to implement MTM feature for Features.py module, currently whey restrict_feature_col is not supplied
#  the default uses datetime and close_p, but I think it should be MTM values to internal profit factor can be calculated


from extended_algo.engine.OrderDetails import OrderType, Order, Action, Entries

from extended_algo.engine.VectorStrategy import VectorStrategy

from extended_algo.market.SecurityMaster import SecurityMaster
