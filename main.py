# main.py
import os
import sys

# Add the parent directory to the sys.path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from strategy.generate_random_strategy import generate_random_strategy
from backtest import Backtest

def main():
    # Paths to data files
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    data_file = os.path.join(data_dir, 'MTDR.csv')
    
    # Load data
    if not os.path.exists(data_file):
        print(f"Data file {data_file} does not exist.")
        return
    
    data_df = pd.read_csv(data_file)
    
    # Apply strategy (choose one)
    data_df = generate_random_strategy(data_df)
    
    # Run backtest
    backtest = Backtest(data_df, data_df['strategy'])
    total_gains = backtest.execute_strategy()
    backtest.plot_performance()
    stats = backtest.def_stats()
    print(f'Total Gains from Strategy: {total_gains}')
    print(f'Buy and Hold Return: {backtest.buy_and_hold()[-1]}')
    print(f'Strategy Statistics: {stats}')

if __name__ == "__main__":
    main()
