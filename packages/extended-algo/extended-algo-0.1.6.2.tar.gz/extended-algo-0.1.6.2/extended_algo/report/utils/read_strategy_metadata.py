import ast
import json
import logging
import pandas as pd
from pathlib import Path
import warnings
import logging

warnings.filterwarnings('ignore')

pd.set_option('display.width', 1000, 'display.max_columns', 1000)

# TODO: If this file gets very large we will run out of memory

seperator_length = 130


def process_stats_data(x):
    x = pd.read_json(x)
    x['id'] = x.index
    x['id'] = x['id'].apply(lambda x: ast.literal_eval(x))
    x['direction'] = x['id'].apply(lambda x: x[0])
    x['batch'] = x['id'].apply(lambda x: x[1])
    x = x[x.direction == 'BOTH']

    # TODO: You really need the max drawdown, sharpie, sortio stats to review strategies against
    #   I may need to handle this separately

    x = x.set_index(['direction', 'batch'])
    x = x.drop('id', errors='ignore', axis=1)

    net_profit = x['net_profit'].sum()
    gross_profit = x['gross_profit'].sum()
    gross_loss = x['gross_loss'].sum()
    total_commission = x['total_commission'].sum()
    number_of_winning_trades = x['number_of_winning_trades'].sum()
    number_of_losing_trades = x['number_of_losing_trades'].sum()
    total_trade_count = x['total_trade_count'].sum()
    largest_winning_trade = x['largest_winning_trade'].max()
    largest_losing_trade = x['largest_losing_trade'].min()

    return pd.Series({'net_profit': net_profit, 'gross_profit': gross_profit, 'gross_loss': gross_loss,
                      'total_commission': total_commission, 'number_of_winning_trades': number_of_winning_trades,
                      'number_of_losing_trades': number_of_losing_trades, 'total_trade_count': total_trade_count,
                      'largest_winning_trade': largest_winning_trade, 'largest_losing_trade': largest_losing_trade})


def read_strategy_metadata(strategy_dir: Path | str):
    '''
    Allows you to see audit history of a strategy run
    '''
    strategy_dir = strategy_dir if isinstance(strategy_dir, Path) else Path(strategy_dir)

    with open(strategy_dir / 'metadata.json', 'r') as f:
        data = json.load(f)
        metadata = data[0]

        strategy_name = metadata.get('strategy_name')
        strategy_doc = metadata.get('strategy_doc')
        func_signal = metadata.get('func_signal')
        save_dir = metadata.get('save_dir')
        run_dir = metadata.get('run_file')

        logging.info(f'{strategy_name}')
        logging.info(f'   - run_script: {run_dir}')
        logging.info(f'   - save_dir: {save_dir}')

        logging.info("\nStrategy Doc String\n" + "-" * seperator_length)
        logging.info(strategy_doc)

        logging.info('\nSignal Definition')
        logging.info("-" * seperator_length)
        logging.info(func_signal)

        logging.info("-" * seperator_length)

        data = data[1:]
        data = pd.DataFrame(data)
        data = pd.concat([data, data.stats_data.apply(lambda x: process_stats_data(x))], axis=1)
        data = data.drop(['stats_data'], axis=1, errors='ignore')
        logging.info(data)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    df = read_strategy_metadata(
        r'C:\Users\karun\Documents\PycharmProjects\extended_algo\extended_algo\test\data\vectorized_strategies\Test_EMA_Crossover\vector')
