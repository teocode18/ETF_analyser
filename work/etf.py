# etf_analyser_alternative.py
import os
import time
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
 
sns.set(style="whitegrid")

def download_adj_close_per_ticker(tickers, start, end, cache_dir="data", force=False, pause=0.2):

    os.makedirs(cache_dir, exist_ok=True)
    series_list = []

    for t in tickers:
        csv_path = os.path.join(cache_dir, f"{t}.csv")
        df = None

        # try cache
        if os.path.exists(csv_path) and not force:
            try:
                df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                last_date = df.index.max()
                # if cache is outdated, fetch only new rows
                if pd.to_datetime(last_date) < pd.to_datetime(end):
                    print(f"[update] fetching new data for {t} from {last_date + pd.Timedelta(days=1)} to {end}")
                    df_new = yf.download(t, start=last_date + pd.Timedelta(days=1), end=end, progress=False)
                    if not df_new.empty:
                        df = pd.concat([df, df_new])
                        df.to_csv(csv_path)
            except Exception as e:
                print(f"[cache] failed to load {csv_path}: {e}")
                df = None

        # download if no cache or forced
        if df is None:
            print(f"[download] {t} ...")
            try:
                ticker_obj = yf.Ticker(t)
                df = ticker_obj.history(start=start, end=end, actions=False)
            except Exception as e:
                print(f"  error using Ticker.history for {t}: {e}")
                df = None

            # fallback to yf.download single-ticker
            if (df is None) or df.empty:
                try:
                    df2 = yf.download(t, start=start, end=end, progress=False)
                    if isinstance(df2.columns, pd.MultiIndex):
                        if 'Adj Close' in df2.columns.levels[0]:
                            df = df2['Adj Close'].to_frame() if isinstance(df2['Adj Close'], pd.Series) else df2['Adj Close']
                        else:
                            df = df2
                    else:
                        df = df2
                except Exception as e:
                    print(f"  fallback download failed for {t}: {e}")
                    df = None

            if df is None or df.empty:
                print(f"  WARNING: no data for {t} (skipping).")
                continue

            try:
                df.to_csv(csv_path)
            except Exception as e:
                print(f"  could not cache {t}: {e}")

            time.sleep(pause)

        # pick adjusted close or close
        chosen_series = None
        if isinstance(df, pd.DataFrame):
            if 'Adj Close' in df.columns:
                chosen_series = df['Adj Close'].rename(t)
            elif 'Adj_Close' in df.columns:
                chosen_series = df['Adj_Close'].rename(t)
            elif 'Close' in df.columns:
                chosen_series = df['Close'].rename(t)
            else:
                cols = list(df.columns)
                print(f"  columns for {t}: {cols}")
                if isinstance(df.columns, pd.MultiIndex):
                    for level0 in df.columns.levels[0]:
                        if level0 in ('Adj Close', 'Close', 'Adj_Close'):
                            chosen_series = df[level0].iloc[:, 0].rename(t)
                            break
        elif isinstance(df, pd.Series):
            chosen_series = df.rename(t)

        if chosen_series is None:
            print(f"  Could not locate a close column for {t}; skipping.")
            continue

        series_list.append(chosen_series)

    if not series_list:
        raise RuntimeError("No data downloaded. Check connectivity or ticker symbols.")

    price_df = pd.concat(series_list, axis=1).sort_index()
    price_df.index = pd.to_datetime(price_df.index)
    return price_df


# ----- metric helpers -----
def compute_returns_and_metrics(price_df, risk_free_annual=0.02):
    returns = price_df.pct_change().dropna()
    ann_ret = (1 + returns.mean()) ** 252 - 1
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = (ann_ret - risk_free_annual) / ann_vol

    def max_drawdown_from_price(series):
        s = series.dropna()
        if s.empty:
            return np.nan
        roll_max = s.cummax()
        drawdown = s / roll_max - 1
        return drawdown.min()

    max_dd = {col: max_drawdown_from_price(price_df[col]) for col in price_df.columns}

    metrics = pd.DataFrame({
        "Annualized Return": ann_ret,
        "Annualized Volatility": ann_vol,
        "Sharpe": sharpe,
        "Max Drawdown": pd.Series(max_dd)
    })

    return returns, metrics

def portfolio_stats(weights, returns, risk_free_annual=0.02):
    w = np.array(weights)
    port_ret = np.sum(returns.mean() * w) * 252
    port_vol = np.sqrt(np.dot(w.T, np.dot(returns.cov() * 252, w)))
    sharpe = (port_ret - risk_free_annual) / port_vol
    return port_ret, port_vol, sharpe

def monte_carlo_simulation(returns, n_sim=3000):
    n_assets = returns.shape[1]
    results = np.zeros((n_sim, 3))
    for i in range(n_sim):
        w = np.random.random(n_assets)
        w /= w.sum()
        r, v, s = portfolio_stats(w, returns)
        results[i] = [r, v, s]
    return pd.DataFrame(results, columns=["Return", "Volatility", "Sharpe"])


# ----- main run -----
if __name__ == "__main__":
    tickers = ["SPY", "QQQ", "VTI", "AGG", "EFA"]
    start = "2024-08-01"  # get 1 year back so Aug 2024 → today
    end = datetime.datetime.today().strftime("%Y-%m-%d")

    print("Downloading prices (per-ticker, with caching)...")
    prices = download_adj_close_per_ticker(tickers, start, end=end, cache_dir="data", force=False)
    print("\nPrice head:\n", prices.head())

    returns, metrics = compute_returns_and_metrics(prices)
    print("\nPerformance metrics:\n", metrics.round(4))

    # save outputs for Power BI
    prices.to_csv("prices.csv")
    returns.to_csv("returns.csv")
    metrics.to_csv("metrics.csv")
    print("\nSaved prices.csv, returns.csv, metrics.csv")

    # correlation heatmap
    corr = returns.corr()
    plt.figure(figsize=(8,6))
    sns.heatmap(corr, annot=True, cmap="vlag")
    plt.title("Returns Correlation")
    plt.tight_layout()
    plt.show()

    # rolling volatility
    rolling_vol = returns.rolling(window=60).std() * np.sqrt(252)
    plt.figure(figsize=(10,5))
    for col in rolling_vol.columns:
        plt.plot(rolling_vol.index, rolling_vol[col], label=col)
    plt.legend()
    plt.title("60-day Rolling Volatility")
    plt.show()

    # monte carlo + efficient frontier scatter
    mc = monte_carlo_simulation(returns, n_sim=3000)
    plt.figure(figsize=(10,6))
    sc = plt.scatter(mc["Volatility"], mc["Return"], c=mc["Sharpe"], cmap="viridis", alpha=0.7)
    plt.xlabel("Volatility")
    plt.ylabel("Expected Return")
    plt.title("Random Portfolios (color = Sharpe)")
    plt.colorbar(sc, label="Sharpe")
    plt.show()
