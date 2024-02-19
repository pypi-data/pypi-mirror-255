import os
import pandas as pd
from pathlib import Path
import functools
import dotenv
dotenv.load_dotenv()

use_cache = True

cache_dir = Path(os.environ['CACHE_MARKET_DATA_DIR'])


def use_cached_market_data(func, **kwargs):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        obj = args[0]
        use_cache = obj.use_cache

        if use_cache:
            bar_type = obj.__class__.__name__
            start = obj.start.date()
            end = obj.end.date()
            freq = obj.freq
            symbol = obj.symbol
            try:
                obj_use_agg_last_px = obj.agg_consecutive_last_px
            except:
                obj_use_agg_last_px = True

            save_filename = f'{bar_type}.{symbol}.{start:%Y%m%d}.{end:%Y%m%d}.{freq}.{obj_use_agg_last_px}.p'.upper()
            filepath = cache_dir / save_filename

            try:
                result = pd.read_pickle(filepath)
                return result

            except FileNotFoundError:
                result = func(*args, **kwargs)
                result.to_pickle(filepath)
                return result

        return func(*args, **kwargs)

    return wrapper
