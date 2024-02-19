import inspect
from pytz import timezone
import json
import logging
import os
import datetime as dt
import pandas as pd


def create_audit_file(strategy_obj):
    metadata_filepath = strategy_obj.save_dir / 'metadata.json'

    strategy_parameters = vars(strategy_obj).copy()
    signal = inspect.getsource(strategy_obj.signal)
    restrict_feature_cols = strategy_parameters.pop('restrict_feature_cols')
    save_dir = strategy_parameters.pop('save_dir')
    strategy_doc = inspect.getdoc(strategy_obj)

    for _ in ['self', 'market_data', 'features_data', 'signal_data', 'trade_data', 'pnl_data']:
        _ = strategy_parameters.pop(_, None)

    if not (metadata_filepath).exists():
        try:
            with open(metadata_filepath, 'w') as f:
                init_data = [{'strategy_name': strategy_obj.strategy_name, 'strategy_doc': strategy_doc, 'func_signal': signal,
                              'run_file': inspect.getfile(strategy_obj.__class__), 'save_dir': str(save_dir),
                              'restrict_feature_cols': list(restrict_feature_cols)}]
                f.write(json.dumps(init_data))

        except TypeError as err:
            logging.error('Could not save JSON Object because object was not serializable...')
            logging.error(init_data)
            os.remove(metadata_filepath)

    with open(metadata_filepath, 'rb+') as f:
        f.seek(-1, os.SEEK_END)
        f.truncate()

    record = dict()
    with open(metadata_filepath, 'a') as f:
        record['run_datetime'] = str(dt.datetime.now(tz=timezone('america/new_york')))
        record['stats_data'] = strategy_parameters.pop('stats_data', pd.DataFrame()).to_json()
        for k, v in strategy_parameters.items():
            record[k] = str(v)
        f.write(',')
        f.write(json.dumps(record, indent=4))
        f.write(']')
