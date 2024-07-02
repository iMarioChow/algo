from backtest import DoubleRSIBacktest

if __name__ == "__main__":
    symbol = 'META'
    start_date = '2018-01-01'
    end_date = '2023-12-31'
    short_period = 7
    long_period = 14
    threshold = 10
    hold_period = 15

    backtester = DoubleRSIBacktest(symbol, start_date, end_date)
    backtester.backtest(short_period, long_period, threshold, hold_period)
