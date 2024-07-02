import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import pandas_ta as ta

class DoubleRSIBacktest:
    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.download_data()
    
    def download_data(self):
        return yf.download(self.symbol, start=self.start_date, end=self.end_date)

    def calculate_rsi(self, short_period, long_period):
        self.data['RSI_short'] = ta.rsi(self.data['Close'], length=short_period)
        self.data['RSI_long'] = ta.rsi(self.data['Close'], length=long_period)
        self.data['RSI_diff'] = self.data['RSI_long'] - self.data['RSI_short']

    def generate_signals(self, short_period, long_period, threshold):
        self.calculate_rsi(short_period, long_period)
        self.data['Signal'] = 0
        self.data.loc[self.data['RSI_diff'] > threshold, 'Signal'] = 1  # Buy signal
        self.data.loc[self.data['RSI_diff'] < -threshold, 'Signal'] = -1  # Sell signal

    def calculate_profit(self, hold_period, transaction_fee=0.0004, take_profit_rate=0.3, stop_loss_rate=0.15):
        self.data['Position'] = 0
        self.data['Returns'] = 0.0
        self.data['Balance'] = 1000.0  # Initial balance
        self.data['Buy_Signal'] = pd.NaT
        self.data['Sell_Signal'] = pd.NaT
        self.data['Holding'] = 0
        position_open = False
        position_entry_price = 0.0
        balance = 1000.0  # To maintain balance across trades
        unrealized_pnl = 0.0
        num_trades = 0  # Count the number of trades

        for i in range(len(self.data)):
            if position_open:
                current_price = self.data['Close'].iloc[i]
                tp_value = balance * take_profit_rate
                sl_value = balance * stop_loss_rate
                unrealized_pnl = (current_price - position_entry_price) * position_size if position_entry > 0 else (position_entry_price - current_price) * position_size

                if (position_entry > 0 and (unrealized_pnl >= tp_value or unrealized_pnl <= -sl_value or (i - position_open_index) >= hold_period)) or \
                   (position_entry < 0 and (unrealized_pnl >= tp_value or unrealized_pnl <= -sl_value or (i - position_open_index) >= hold_period)):
                    # Closing position
                    profit = unrealized_pnl
                    balance += profit
                    self.data.loc[self.data.index[position_open_index:i+1], 'Holding'] = 1 if position_entry > 0 else -1
                    self.data.at[self.data.index[i], 'Returns'] = profit
                    position_open = False
                    num_trades += 1  # Increment the number of trades
                    print(f"Closed {'Buy' if position_entry > 0 else 'Sell'} Position at {current_price}, PnL: {profit}, Balance: {balance}")

            if not position_open:
                if self.data['Signal'].iloc[i] == 1:  # Buy signal
                    position_open = True
                    position_entry = balance  # Use the entire balance for the position
                    position_entry_price = self.data['Close'].iloc[i]
                    position_open_index = i
                    position_size = position_entry / position_entry_price
                    # Apply transaction fee
                    balance -= position_entry * transaction_fee
                    self.data.at[self.data.index[i], 'Buy_Signal'] = self.data.index[i]
                    num_trades += 1  # Increment the number of trades
                    print(f"Opened Buy Position at {position_entry_price}, Balance: {balance}")
                elif self.data['Signal'].iloc[i] == -1:  # Sell signal
                    position_open = True
                    position_entry = -balance  # Use the entire balance for the position
                    position_entry_price = self.data['Close'].iloc[i]
                    position_open_index = i
                    position_size = -position_entry / position_entry_price
                    # Apply transaction fee
                    balance -= abs(position_entry) * transaction_fee
                    self.data.at[self.data.index[i], 'Sell_Signal'] = self.data.index[i]
                    num_trades += 1  # Increment the number of trades
                    print(f"Opened Sell Position at {position_entry_price}, Balance: {balance}")

            self.data.at[self.data.index[i], 'Balance'] = balance

        return num_trades

    def backtest(self, short_period, long_period, threshold, hold_period, transaction_fee=0.0004, take_profit_rate=0.3, stop_loss_rate=0.15):
        self.generate_signals(short_period, long_period, threshold)
        num_trades = self.calculate_profit(hold_period, transaction_fee, take_profit_rate, stop_loss_rate)
        self.plot_results()
        print(f"Number of trades: {num_trades}")

    def plot_results(self):
        fig, axs = plt.subplots(3, 1, figsize=(12, 18), gridspec_kw={'height_ratios': [1, 1, 1]})

        # Plot the balance curve
        axs[0].plot(self.data.index, self.data['Balance'], label='Balance Curve')
        axs[0].set_title('Balance Curve of Double RSI Strategy')
        axs[0].set_xlabel('Date')
        axs[0].set_ylabel('Balance')
        axs[0].legend()
        axs[0].grid(True)

        # Plot symbol price with buy and sell signals
        axs[1].plot(self.data.index, self.data['Close'], label=f'{self.symbol} Price', color='blue')
        buy_signals = self.data.loc[self.data['Buy_Signal'].notna()]
        sell_signals = self.data.loc[self.data['Sell_Signal'].notna()]
        axs[1].scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', label='Buy Signal', s=100)
        axs[1].scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell Signal', s=100)
        axs[1].set_title(f'{self.symbol} Price with Buy and Sell Signals')
        axs[1].set_xlabel('Date')
        axs[1].set_ylabel(f'{self.symbol} Price')
        axs[1].legend()
        axs[1].grid(True)

        # Plot the RSI difference
        axs[2].plot(self.data.index, self.data['RSI_diff'], label='RSI Difference', color='green')
        axs[2].axhline(threshold, color='red', linestyle='--', label='Threshold +10')
        axs[2].axhline(-threshold, color='blue', linestyle='--', label='Threshold -10')
        axs[2].set_title('RSI Difference')
        axs[2].set_xlabel('Date')
        axs[2].set_ylabel('RSI Difference')
        axs[2].legend()
        axs[2].grid(True)

        plt.tight_layout()
        plt.show()

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
