import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define tickers
tickers = ["SPY", "QQQ", "IWM", "EFA", "EEM"]

# Download data
raw_data = yf.download(tickers, start="2020-01-01", end="2025-01-01")

# Handle multi-index DataFrame (yfinance output)
if isinstance(raw_data.columns, pd.MultiIndex):
    data = raw_data["Adj Close"]
else:
    data = raw_data[["Adj Close"]]

# Calculate daily returns
returns = data.pct_change().dropna()

# ---- Performance Metrics ----
risk_free_rate = 0.02 / 252  # 2% annual risk-free, daily equivalent

metrics = pd.DataFrame(index=tickers)

# Annualized return
metrics["Annualized Return"] = (1 + returns.mean()) ** 252 - 1

# Annualized volatility
metrics["Volatility"] = returns.std() * np.sqrt(252)

# Sharpe ratio
metrics["Sharpe Ratio"] = (metrics["Annualized Return"] - 0.02) / metrics["Volatility"]

# Max drawdown
def max_drawdown(series):
    cum_returns = (1 + series).cumprod()
    rolling_max = cum_returns.cummax()
    drawdown = (cum_returns - rolling_max) / rolling_max
    return drawdown.min()

metrics["Max Drawdown"] = returns.apply(max_drawdown)

print("\nPerformance Metrics:\n")
print(metrics)

# ---- Plots ----

# Price history
plt.figure(figsize=(12, 6))
for ticker in data.columns:
    plt.plot(data.index, data[ticker], label=ticker)
plt.legend()
plt.title("ETF Adjusted Close Prices")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.show()

# Cumulative returns
cumulative_returns = (1 + returns).cumprod()
plt.figure(figsize=(12, 6))
for ticker in cumulative_returns.columns:
    plt.plot(cumulative_returns.index, cumulative_returns[ticker], label=ticker)
plt.legend()
plt.title("ETF Cumulative Returns")
plt.xlabel("Date")
plt.ylabel("Growth of $1")
plt.show()

# Rolling volatility (risk over time)
rolling_vol = returns.rolling(window=60).std() * np.sqrt(252)
plt.figure(figsize=(12, 6))
for ticker in rolling_vol.columns:
    plt.plot(rolling_vol.index, rolling_vol[ticker], label=ticker)
plt.legend()
plt.title("60-Day Rolling Volatility")
plt.xlabel("Date")
plt.ylabel("Volatility")
plt.show()

