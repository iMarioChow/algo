import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import pandas_ta as ta
import itertools

# Function to calculate RSI using pandas_ta
def calculate_rsi(data, short_period, long_period):
    data['RSI_short'] = ta.rsi(data['Close'], length=short_period)
    data['RSI_long'] = ta.rsi(data['Close'], length=long_period)
    data['RSI_diff'] = data['RSI_long'] - data['RSI_short']
    return data

# Function to generate trading signals
def generate_signals(data, short_period, long_period, threshold):
    data = calculate_rsi(data, short_period, long_period)
    data['Signal'] = 0
    data.loc[data['RSI_diff'] > threshold, 'Signal'] = 1  # Buy signal
    data.loc[data['RSI_diff'] < -threshold, 'Signal'] = -1  # Sell signal
    return data

# Function to calculate profit with stop loss and take profit based on equity
def calculate_profit(data, hold_period, transaction_fee=0.0004, take_profit_rate=0.3, stop_loss_rate=0.15):
    data = data.copy()
    data['Position'] = 0
    data['Returns'] = 0.0
    data['Balance'] = 1000.0  # Initial balance
    data['Buy_Signal'] = pd.NaT
    data['Sell_Signal'] = pd.NaT
    data['Holding'] = 0
    position_open = False
    position_entry_price = 0.0
    balance = 1000.0  # To maintain balance across trades
    unrealized_pnl = 0.0

    for i in range(len(data)):
        if position_open:
            current_price = data['Close'].iloc[i]
            tp_value = balance * take_profit_rate
            sl_value = balance * stop_loss_rate
            unrealized_pnl = (current_price - position_entry_price) * position_size if position_entry > 0 else (position_entry_price - current_price) * position_size

            if (position_entry > 0 and (unrealized_pnl >= tp_value or unrealized_pnl <= -sl_value or (i - position_open_index) >= hold_period)) or \
               (position_entry < 0 and (unrealized_pnl >= tp_value or unrealized_pnl <= -sl_value or (i - position_open_index) >= hold_period)):
                # Closing position
                profit = unrealized_pnl
                balance += profit
                data.loc[data.index[position_open_index:i+1], 'Holding'] = 1 if position_entry > 0 else -1
                data.at[data.index[i], 'Returns'] = profit
                position_open = False
                print(f"Closed {'Buy' if position_entry > 0 else 'Sell'} Position at {current_price}, PnL: {profit}, Balance: {balance}")

        if not position_open:
            if data['Signal'].iloc[i] == 1:  # Buy signal
                position_open = True
                position_entry = balance  # Use the entire balance for the position
                position_entry_price = data['Close'].iloc[i]
                position_open_index = i
                position_size = position_entry / position_entry_price
                # Apply transaction fee
                balance -= position_entry * transaction_fee
                data.at[data.index[i], 'Buy_Signal'] = data.index[i]
                print(f"Opened Buy Position at {position_entry_price}, Balance: {balance}")
            elif data['Signal'].iloc[i] == -1:  # Sell signal
                position_open = True
                position_entry = -balance  # Use the entire balance for the position
                position_entry_price = data['Close'].iloc[i]
                position_open_index = i
                position_size = -position_entry / position_entry_price
                # Apply transaction fee
                balance -= abs(position_entry) * transaction_fee
                data.at[data.index[i], 'Sell_Signal'] = data.index[i]
                print(f"Opened Sell Position at {position_entry_price}, Balance: {balance}")

        data.at[data.index[i], 'Balance'] = balance

    return data

# Main script
if __name__ == "__main__":
    # Download ADA data from Yahoo Finance
    btc_data = yf.download('BTC-USD', start='2018-01-01', end='2022-01-31')

    # Define parameter ranges for optimization
    short_period_range = range(5, 15, 2)
    long_period_multipliers = range(2, 5)
    threshold_range = range(5, 20, 5)
    hold_period_range = range(5, 15, 5)

    best_params = None
    best_balance = 0

    # Perform grid search for parameter optimization
    for short_period, multiplier, threshold, hold_period in itertools.product(short_period_range, long_period_multipliers, threshold_range, hold_period_range):
        long_period = short_period * multiplier
        signals = generate_signals(btc_data.copy(), short_period, long_period, threshold)
        results = calculate_profit(signals, hold_period)
        final_balance = results['Balance'].iloc[-1]
        
        if final_balance > best_balance:
            best_balance = final_balance
            best_params = (short_period, long_period, threshold, hold_period)

    # Print best parameters
    print(f"Best Parameters: Short Period: {best_params[0]}, Long Period: {best_params[1]}, Threshold: {best_params[2]}, Hold Period: {best_params[3]}")
    print(f"Best Final Balance: {best_balance}")

    # Generate trading signals and calculate profit with best parameters
    short_period, long_period, threshold, hold_period = best_params
    signals = generate_signals(btc_data.copy(), short_period, long_period, threshold)
    results = calculate_profit(signals, hold_period)

    # Plot the graphs
    fig, axs = plt.subplots(3, 1, figsize=(12, 18), gridspec_kw={'height_ratios': [1, 1, 1]})

    # Plot the balance curve
    axs[0].plot(results.index, results['Balance'], label='Balance Curve')
    axs[0].set_title('Balance Curve of Double RSI Strategy')
    axs[0].set_xlabel('Date')
    axs[0].set_ylabel('Balance')
    axs[0].legend()
    axs[0].grid(True)

    # Plot ADA price with buy and sell signals
    axs[1].plot(results.index, results['Close'], label='BTC Price', color='blue')
    buy_signals = results.loc[results['Buy_Signal'].notna()]
    sell_signals = results.loc[results['Sell_Signal'].notna()]
    axs[1].scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', label='Buy Signal', s=100)
    axs[1].scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell Signal', s=100)
    axs[1].set_title('BTC Price with Buy and Sell Signals')
    axs[1].set_xlabel('Date')
    axs[1].set_ylabel('BTC Price')
    axs[1].legend()
    axs[1].grid(True)

    # Plot the RSI difference
    axs[2].plot(results.index, results['RSI_diff'], label='RSI Difference', color='green')
    axs[2].axhline(threshold, color='red', linestyle='--', label=f'Threshold +{threshold}')
    axs[2].axhline(-threshold, color='blue', linestyle='--', label=f'Threshold -{threshold}')
    axs[2].set_title('RSI Difference')
    axs[2].set_xlabel('Date')
    axs[2].set_ylabel('RSI Difference')
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()
    #plt.show()  # Removed plt.show() as requested

    # Save the plot
    plt.savefig('double_rsi_strategy_btc.png')
