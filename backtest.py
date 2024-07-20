# backtest.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Backtest:
    def __init__(self, data, strategy):
        self.data = data
        self.strategy = strategy
        self.current_inventory = 0
        self.profit = 0
        self.profit_history = []  # Start with an empty list
        self.buy_price = 0
        self.short_price = 0
        self.trade_pnl = []
        self.trade_max_drawdown_pct = []
        self.trades = 0
        self.trade_durations = []
        self.temp_prices = []

    def execute_strategy(self):
        for i in range(len(self.data)):
            if self.strategy[i] == 1 and self.current_inventory == 0:  # Buy signal
                self.current_inventory = 1
                self.buy_price = self.data['Close'][i]
                self.trade_durations.append((i, "buy", self.data['Close'][i]))
                self.temp_prices.append(self.data['Close'][i])
                print(f'day {i}: buy at price {self.data["Close"][i]}, current profit {self.profit}')
            elif self.strategy[i] == -1 and self.current_inventory == 0:  # Short signal
                self.current_inventory = -1
                self.short_price = self.data['Close'][i]
                self.trade_durations.append((i, "short", self.data['Close'][i]))
                self.temp_prices.append(self.data['Close'][i])
                print(f'day {i}: short at price {self.data["Close"][i]}, current profit {self.profit}')
            elif self.strategy[i] == 0 and self.current_inventory == 1:  # Sell to close buy position
                trade_profit = self.data['Close'][i] - self.buy_price
                self.profit += trade_profit
                self.trade_pnl.append(trade_profit)
                self.temp_prices.append(self.data['Close'][i])
                self.update_max_drawdown("buy")
                self.current_inventory = 0
                self.trades += 1
                print(f'day {i}: sell at price {self.data["Close"][i]}, current profit {self.profit}')
            elif self.strategy[i] == 0 and self.current_inventory == -1:  # Buy to close short position
                trade_profit = self.short_price - self.data['Close'][i]
                self.profit += trade_profit
                self.trade_pnl.append(trade_profit)
                self.temp_prices.append(self.data['Close'][i])
                self.update_max_drawdown("short")
                self.current_inventory = 0
                self.trades += 1
                print(f'day {i}: buy to cover at price {self.data["Close"][i]}, current profit {self.profit}')
            
            # Update profit history for each day
            if self.current_inventory == 1:
                current_profit = self.profit + (self.data['Close'][i] - self.buy_price)
            elif self.current_inventory == -1:
                current_profit = self.profit + (self.short_price - self.data['Close'][i])
            else:
                current_profit = self.profit
            self.profit_history.append(current_profit)
        
        total_gains = self.profit_history[-1]
        return total_gains

    def update_max_drawdown(self, position_type):
        initial_price = self.temp_prices[0]
        if position_type == "buy":
            min_price = min(self.temp_prices)
            drawdown = (min_price - initial_price) / initial_price * 100
        else:  # position_type == "short"
            max_price = max(self.temp_prices)
            drawdown = (initial_price - max_price) / initial_price * 100

        self.trade_max_drawdown_pct.append(drawdown)
        self.temp_prices.clear()

    def buy_and_hold(self):
        initial_price = self.data['Close'][0]
        buy_and_hold_history = [(price - initial_price) for price in self.data['Close']]
        return buy_and_hold_history

    def plot_performance(self):
        # Ensure both arrays have the same length
        profit_history_aligned = self.profit_history  # Use the full profit history
        dates_aligned = self.data['Date']  # Use the full dates

        # Plot the price with buy/sell signals
        plt.figure(figsize=(14, 7))
        plt.plot(self.data['Date'], self.data['Close'], color='r', lw=2.)
        plt.plot(self.data['Date'][self.strategy == 1], self.data['Close'][self.strategy == 1], '^', markersize=10, color='g', lw=0, label='buying signal')
        plt.plot(self.data['Date'][self.strategy == -1], self.data['Close'][self.strategy == -1], 'v', markersize=10, color='k', lw=0, label='shorting signal')
        plt.title('Trading Strategy Performance')
        plt.legend()
        plt.show()

        # Plot profit
        buy_and_hold_history = self.buy_and_hold()
        plt.figure(figsize=(14, 7))
        plt.plot(dates_aligned, profit_history_aligned, color='b', lw=2., label='Strategy Profit')
        plt.plot(dates_aligned, buy_and_hold_history, color='orange', lw=2., label='Buy and Hold Profit')
        plt.title('Profit Comparison')
        plt.xlabel('Date')
        plt.ylabel('Profit')
        plt.legend()
        plt.show()

    def def_stats(self):
        # Number of trades
        num_trades = self.trades
        
        # Largest maximum drawdown
        max_drawdown_pct = min(self.trade_max_drawdown_pct, default=0)

        # Sharpe ratio
        pnl_series = pd.Series(self.trade_pnl)
        sharpe_ratio = (pnl_series.mean() / pnl_series.std()) * np.sqrt(252) if len(pnl_series) > 1 else 0
        
        return {
            'Number of Trades': num_trades,
            'Maximum Drawdown (%)': max_drawdown_pct,
            'Sharpe Ratio': sharpe_ratio
        }
