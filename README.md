# ETF Analysis & Dashboard with Python + Power BI  

##  Overview  
This project combines Python and Power BI to analyse and visualise Exchange-Traded Funds (ETFs).  

- **Python**: Downloads ETF data, computes key performance metrics, and exports clean CSVs  
- **Power BI**: Transforms the data and creates an interactive dashboard for analysis  

ETFs analysed: **SPY, QQQ, VTI, AGG, EFA**  

---
##  About the ETFs  
- **SPY (SPDR S&P 500 ETF Trust)**  
  Tracks the S&P 500 Index (500 largest U.S. companies).  
  Represents the overall U.S. stock market performance.  
  Very liquid, often used as a benchmark for U.S. equities.  

- **QQQ (Invesco QQQ Trust)**  
  Tracks the Nasdaq-100 Index (largest 100 non-financial companies on Nasdaq).  
  Tech-heavy (Apple, Microsoft, Nvidia, etc.), growth-oriented with higher volatility.  

- **VTI (Vanguard Total Stock Market ETF)**  
  Covers the entire U.S. stock market (large, mid, small, and micro-cap).  
  Extremely diversified with 3,000+ companies.  
  Good for broad exposure to U.S. equities.  

- **AGG (iShares Core U.S. Aggregate Bond ETF)**  
  Tracks the U.S. investment-grade bond market.  
  Includes U.S. Treasuries, corporate bonds, mortgage-backed securities.  
  Lower risk, often used for diversification and stability.  

- **EFA (iShares MSCI EAFE ETF)**  
  Tracks the MSCI EAFE Index (Europe, Australasia, Far East developed markets).  
  Provides exposure to global equities outside the U.S. & Canada.  
  Useful for international diversification.  

---

## Workflow  

###  Step 1: Data Extraction & Processing (Python)  
- Script: `etf.py`  
- Downloads adjusted close prices using [yfinance](https://github.com/ranaroussi/yfinance)  
- Calculates:  
  - Daily returns  
  - Annualised return & volatility  
  - Sharpe ratio  
  - Max drawdown  
- Exports results to:  
  - `prices.csv` → historical ETF prices  
  - `returns.csv` → daily returns  
  - `metrics.csv` → performance metrics  

---

###  Step 2: Data Modelling (Power BI)  
- Imported CSV files into Power BI  
- Transformed with Power Query:  
  - Unpivoted ETF columns → clean format (`Date, Ticker, Value`)  
  - Created a Date Table for time intelligence  
  - Established relationships between Prices, Returns, and Metrics
 
---

###  Step 3: Dashboard Creation (Power BI)  
The dashboard includes:  
- **ETF Price Trends** → line chart by ticker  
- **Daily Returns** → line chart by ticker 
- **Performance Metrics** → table of Sharpe, volatility, returns, drawdowns  
- **Filters** → date range slicer 



<img width="842" height="476" alt="image" src="https://github.com/user-attachments/assets/ba60928f-5154-4d59-85ef-2a71d4554422" />

---

## Individual Analysis

AGG: This ticker shows a stable, low-volatility trend. Its price stayed in a tight range and experienced a slow, gradual increase. This type of performance is often characteristic of bond ETFs or other low-risk assets.

EFA: This ticker demonstrates strong and consistent growth. Its price trend is clearly upward, with a noticeable gain from the beginning of the period to the end. It shows moderate volatility, but the overall direction is consistently positive.

SPY: This ticker shows the most significant price appreciation. Its price experienced explosive growth, climbing hundreds of points over the period. It also appears to have the highest volatility, with sharp fluctuations accompanying its strong upward trend.

<img width="931" height="319" alt="image" src="https://github.com/user-attachments/assets/ced234f8-3d30-4aea-bdde-78cca35e6f2e" />

