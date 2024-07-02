import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import pandas_ta as ta

# Setting pandas display options
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Define the ticker symbol and date variables
tickerSymbol = 'TSLA'
start_date = '2021-09-01'
end_date = '2021-12-31'
yf_start_date = str(int(start_date[0:4])-1) + '-07-01'  # Fetch data starting from Nov of the previous year

# Get data on this ticker
tickerData = yf.Ticker(tickerSymbol)

# Get the historical prices for this ticker with the modified date range
df = tickerData.history(period='1d', start=yf_start_date, end=end_date)

# Calculate RSI for lengths of 7 and 35
df['RSI_7'] = ta.rsi(df['Close'], length=7)
df['RSI_35'] = ta.rsi(df['Close'], length=35)
df['RSI_Diff'] = df['RSI_35'] - df['RSI_7']

# Filter the DataFrame to only include data within the specified start and end dates
df = df[(df.index >= start_date) & (df.index <= end_date)]
# Identify dates where RSI_Diff is greater than 20
significant_dates = df[df['RSI_Diff'] > 20].index

# Plotting the closing prices along with RSI values with adjusted figsize
fig, ax = plt.subplots(3, 1, figsize=(8, 8), gridspec_kw={'height_ratios': [2, 1, 1]})

# Plot close price
ax[0].plot(df.index, df['Close'], label='Close Price')
ax[0].set_title('TSLA Closing Prices')
ax[0].set_xlabel('Date')
ax[0].set_ylabel('Price (USD)')
ax[0].legend(loc='best')

# Plot RSI values and add vertical lines where RSI_Diff > 20
ax[1].plot(df.index, df['RSI_7'], label='RSI (7 days)', color='deepskyblue')
ax[1].plot(df.index, df['RSI_35'], label='RSI (35 days)', color='olive')
for date in significant_dates:
    rsi7_value = df.loc[date, 'RSI_7']
    rsi35_value = df.loc[date, 'RSI_35']
    min_rsi = min(rsi7_value, rsi35_value)
    max_rsi = max(rsi7_value, rsi35_value)
    ax[1].plot([date, date], [min_rsi, max_rsi], color='red', linestyle='--', linewidth=2)  # Drawing a line segment
ax[1].set_title('RSI Value')
ax[1].set_xlabel('Date')
ax[1].set_ylabel('RSI')
ax[1].legend(loc='best')

# Plot RSI Difference with horizontal lines at +20 and -20
ax[2].plot(df.index, df['RSI_Diff'], label='RSI Difference (35-7)', color='purple')
ax[2].axhline(20, color='green', linestyle='--', label='Level +20')
ax[2].axhline(-20, color='red', linestyle='--', label='Level -20')
ax[2].set_title('RSI Difference')
ax[2].set_xlabel('Date')
ax[2].set_ylabel('RSI Difference')
ax[2].legend(loc='best')

print(df)

plt.tight_layout()
plt.show()