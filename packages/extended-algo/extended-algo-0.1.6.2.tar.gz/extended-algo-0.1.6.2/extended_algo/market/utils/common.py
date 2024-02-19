from enum import Enum, auto
from pathlib import Path
import os


class MarketSource(Enum):
    IQFEED_TICK = auto()
    IQFEED_SECOND = auto()
    IQFEED_MINUTE = auto()
    IQFEED_MINUTE_FEATHER = auto()
    IQFEED_SECOND_FEATHER = auto()
    IQFEED_TICK_FEATHER = auto()


class MarketDataType(Enum):
    TICK = auto()
    TIME = auto()
    TICK_RANGE = auto()
    TICK_VOLUME = auto()
    TICK_COUNT = auto()
    TICK_DOLLAR = auto()


def get_market_data_source_dir(source: MarketSource):
    assert source in (MarketSource.IQFEED_MINUTE_FEATHER, MarketSource.IQFEED_TICK_FEATHER,
                      MarketSource.IQFEED_SECOND_FEATHER), f'Only Feature supported! "{source}" provided...'

    path_root_market_data_dir = Path(os.getenv('MARKET_DATA_LOCAL_DIR'))

    match source:
        case MarketSource.IQFEED_TICK:
            return path_root_market_data_dir / 'iqfeed_tick'
        case MarketSource.IQFEED_SECOND:
            return path_root_market_data_dir / 'iqfeed_second'
        case MarketSource.IQFEED_MINUTE:
            return path_root_market_data_dir / 'iqfeed_minute'

        case MarketSource.IQFEED_TICK_FEATHER:
            return path_root_market_data_dir / 'iqfeed_tick_feather'
        case MarketSource.IQFEED_SECOND_FEATHER:
            return path_root_market_data_dir / 'iqfeed_second_feather'
        case MarketSource.IQFEED_MINUTE_FEATHER:
            return path_root_market_data_dir / 'iqfeed_minute_feather'
