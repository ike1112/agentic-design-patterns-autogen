# filename: fetch_and_plot_stocks.py
import yfinance as yf
import matplotlib.pyplot as plt

# Fetching stock data for the year 2025 up to today.
start_date = '2025-01-01'
end_date = '2025-12-24'
ticker_symbols = ['NVDA', 'TSLA']

data = yf.download(ticker_symbols, start=start_date, end=end_date)

# Calculate the YTD gain as a percentage of the price on the first day of the year
percent_gains = (data['Adj Close'] / data['Adj Close'].iloc[0] - 1) * 100

# Plotting the results
plt.figure(figsize=(10, 6))
for ticker in ticker_symbols:
    plt.plot(percent_gains.index, percent_gains[ticker], label=f'{ticker} YTD Gain %')

plt.title('YTD Stock Gains for NVDA and TSLA (up to 2025-12-24)')
plt.xlabel('Date')
plt.ylabel('Gain (%)')
plt.legend()
plt.grid(True)

# Save the plot as a PNG file
plt.savefig('ytd_stock_gains.png')
plt.close()