import os
import pandas as pd
import numpy as np
from supabase import create_client, Client
import dotenv
import yfinance as yf
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. SETUP
dotenv.load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

BENCHMARK_TICKER = "SPY" 


def linear_regression_slope_and_predictions(
    market: np.ndarray, stock: np.ndarray
) -> tuple[float, np.ndarray]:
    """Perform a simple OLS to return slope (beta) and the fitted values."""
    X = np.column_stack((np.ones_like(market), market))
    coeffs, *_ = np.linalg.lstsq(X, stock, rcond=None)
    predictions = X @ coeffs
    return coeffs[1], predictions

def fetch_all_prices(lookback_days: int = 400):
    """
    Downloads price history from Supabase for the past N days from today.
    Returns a DataFrame with dates as index and tickers as columns.
    
    Args:
        lookback_days: Number of calendar days to look back (default: 400 to ensure 252+ trading days)
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=lookback_days)
    
    print(f"Fetching price history from {start_date} to {today}...")
    
    # Paginate through all results (Supabase default limit is 1000)
    all_data = []
    page_size = 1000  # Supabase max is 1000 per request
    offset = 0
    
    while True:
        response = (
            supabase.table("stock_prices")
            .select("ticker, date, close")
            .gte("date", start_date.isoformat())
            .lte("date", today.isoformat())
            .order("date")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        
        if not response.data:
            break
            
        all_data.extend(response.data)
        
        if len(response.data) < page_size:
            print(f"   ... fetched {len(all_data)} rows (final page)")
            break  # Last page
        
        if len(all_data) % 10000 == 0:  # Progress every 10k rows
            print(f"   ... fetched {len(all_data)} rows so far")
        
        offset += page_size
    
    if not all_data:
        print("[WARN] No data found in the specified date range.")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_data)
    df["date"] = pd.to_datetime(df["date"])
    
    # Remove duplicate (ticker, date) entries, keeping the last one
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["ticker", "date"], keep="last")
    if len(df) < before_dedup:
        print(f"[WARN] Removed {before_dedup - len(df)} duplicate entries")
    
    print(f"[DATA] Retrieved {len(df)} price records for {df['ticker'].nunique()} tickers")

    price_matrix = df.pivot(index="date", columns="ticker", values="close")
    price_matrix = price_matrix.sort_index()
    
    print(f"[DATE] Date range: {price_matrix.index.min().date()} to {price_matrix.index.max().date()} ({len(price_matrix)} trading days)")
    
    return ensure_spy_history(price_matrix)


def filter_full_history_tickers(price_matrix: pd.DataFrame, min_pct: float = 0.95) -> pd.DataFrame:
    """Keep tickers that have at least min_pct of all trading days (default 95%)."""
    total_days = price_matrix.index.nunique()
    min_required = int(total_days * min_pct)
    
    counts = price_matrix.count()
    sufficient_history = counts[counts >= min_required].index
    
    # Always keep benchmark if present
    if BENCHMARK_TICKER in price_matrix.columns and BENCHMARK_TICKER not in sufficient_history:
        sufficient_history = sufficient_history.append(pd.Index([BENCHMARK_TICKER]))
    
    filtered = price_matrix.loc[:, sufficient_history]
    print(f"[INFO] Keeping {len(sufficient_history)} tickers with >= {min_required}/{total_days} days ({min_pct*100:.0f}%)")
    return filtered


def ensure_spy_history(price_matrix: pd.DataFrame) -> pd.DataFrame:
    """Ensure the benchmark ticker is present using Yahoo Finance when needed."""
    if BENCHMARK_TICKER in price_matrix.columns or price_matrix.empty:
        return price_matrix

    start = price_matrix.index.min()
    end = price_matrix.index.max() + timedelta(days=1)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    print(f"[DOWNLOAD] Downloading {BENCHMARK_TICKER} from Yahoo Finance ({start_str} to {end_str})...")
    try:
        spy_data = yf.download(
            BENCHMARK_TICKER,
            start=start_str,
            end=end_str,
            progress=False,
            auto_adjust=False,
        )
        if spy_data.empty:
            print("[WARN] Yahoo Finance returned empty SPY data.")
            return price_matrix

        # Handle MultiIndex columns that yfinance sometimes returns
        if isinstance(spy_data.columns, pd.MultiIndex):
            spy_data.columns = spy_data.columns.get_level_values(0)

        if "Close" not in spy_data.columns:
            raise ValueError(f"Close column not found. Available: {list(spy_data.columns)}")

        spy_series = spy_data["Close"].squeeze()  # Ensure it's a Series
        spy_series = spy_series.reindex(price_matrix.index).ffill()

        if spy_series.isna().all():
            print("[WARN] SPY data is all NaN after reindex.")
            return price_matrix

        price_matrix[BENCHMARK_TICKER] = spy_series.values
        print(f"[OK] Added {BENCHMARK_TICKER} history from Yahoo Finance ({len(spy_series.dropna())} rows).")
        return price_matrix
    except Exception as exc:
        print(f"[WARN] Failed to download SPY from Yahoo Finance: {exc}")
        import traceback
        traceback.print_exc()
        return price_matrix

def _safe_lookback(series_length: int, lookback: int, label: str) -> bool:
    if series_length <= lookback:
        print(f"[WARN] Not enough history ({series_length}) for {label} ({lookback} days).")
        return False
    return True


def calculate_complex_features(price_matrix):
    """
    Computes SOTA metrics: Beta, Residual Volatility, Momentum.
    """
    if price_matrix.empty:
        print("[WARN] Price matrix is empty. Skipping feature calculation.")
        return pd.DataFrame()

    price_matrix = filter_full_history_tickers(price_matrix.copy())
    if price_matrix.empty:
        print("[WARN] No tickers with 252+ observations. Skipping feature calculation.")
        return pd.DataFrame()

    features = pd.DataFrame(index=price_matrix.columns)

    # 1. PREP: Calculate Log Returns (Better for math than % change)
    log_rets = np.log(price_matrix / price_matrix.shift(1))

    # 2. MOMENTUM (Simple Rolling Math)
    print("Calculating Momentum & Volatility...")
    if _safe_lookback(len(price_matrix), 252, "12m return"):
        features["return_12m"] = price_matrix.iloc[-1] / price_matrix.iloc[-252] - 1
    else:
        features["return_12m"] = np.nan

    if _safe_lookback(len(price_matrix), 63, "3m return"):
        features["return_3m"] = price_matrix.iloc[-1] / price_matrix.iloc[-63] - 1
    else:
        features["return_3m"] = np.nan

    if _safe_lookback(len(price_matrix), 21, "1m return"):
        features["return_1m"] = price_matrix.iloc[-1] / price_matrix.iloc[-21] - 1
    else:
        features["return_1m"] = np.nan

    if len(log_rets.dropna(how="all")) >= 90:
        features["volatility_90d"] = log_rets.rolling(window=90).std().iloc[-1] * np.sqrt(252)
    else:
        print("[WARN] Not enough data for 90-day volatility.")
        features["volatility_90d"] = np.nan
    
    # 3. REGRESSION METRICS (Beta & Rezzy)
    # We regress every stock against SPY to find "Alpha" and "Idiosyncratic Risk"
    print("Calculating Beta and Residuals (Regression)...")
    
    if BENCHMARK_TICKER not in log_rets.columns:
        print(f"Warning: {BENCHMARK_TICKER} not found. Skipping Beta calculations.")
        return features

    market_rets = log_rets[BENCHMARK_TICKER].dropna()
    
    betas = []
    residual_vols = []
    
    # Loop efficiently only for regression 
    if len(market_rets) < 200:
        print("[WARN] Not enough market data for regression. Skipping Beta calculations.")
        features["beta"] = np.nan
        features["idiosyncratic_vol"] = np.nan
        features["upside_beta"] = np.nan
        return features

    for ticker in price_matrix.columns:
        try:
            # Align data: Drop missing days for specific stock
            stock_rets = log_rets[ticker].dropna()
            
            # Intersection of dates (Market AND Stock must exist)
            common_dates = market_rets.index.intersection(stock_rets.index)
            
            # Use last 1 year (252 days) for Beta calculation
            if len(common_dates) < 200: 
                betas.append(np.nan)
                residual_vols.append(np.nan)
                continue
                
            y_vals = stock_rets.loc[common_dates].values
            x_vals = market_rets.loc[common_dates].values

            beta, preds = linear_regression_slope_and_predictions(x_vals, y_vals)
            betas.append(beta)
            residuals = y_vals - preds
            residual_vols.append(np.std(residuals) * np.sqrt(252))
            
        except Exception as e:
            betas.append(np.nan)
            residual_vols.append(np.nan)

    features['beta'] = betas
    features['idiosyncratic_vol'] = residual_vols # Mapped to 'Vol Rezzy'
    
    # 4. UPSIDE BETA (For 'Beta Upside High')
    # Calculate Beta ONLY on days when SPY was Green
    # This is a SOTA technique for finding stocks that rally hard but don't crash hard
    print("Calculating Asymmetric Beta...")
    upside_betas = []
    
    green_days = market_rets[market_rets > 0].index
    
    for ticker in price_matrix.columns:
        try:
            stock_rets = log_rets[ticker].loc[green_days].dropna()
            # Re-align with green market days
            common = green_days.intersection(stock_rets.index)
            if len(common) < 50:
                upside_betas.append(np.nan)
                continue
                
            y_vals = stock_rets.loc[common].values
            x_vals = market_rets.loc[common].values

            upside_beta, _ = linear_regression_slope_and_predictions(x_vals, y_vals)
            upside_betas.append(upside_beta)
        except:
            upside_betas.append(np.nan)
            
    features['upside_beta'] = upside_betas

    return features


def _fetch_single_ticker_fundamentals(ticker: str) -> dict:
    """
    Fetch fundamental data for a single ticker from yfinance.
    Returns a dict with the ticker and its fundamental metrics.
    """
    result = {'ticker': ticker}
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # PE Ratio (trailing)
        result['pe_ratio'] = info.get('trailingPE')
        
        # Debt to Equity
        result['debt_to_equity'] = info.get('debtToEquity')
        
        # Leverage Ratio (same as debt_to_equity for our purposes)
        result['leverage_ratio'] = info.get('debtToEquity')
        
        # Return on Capital / ROIC
        # yfinance doesn't have direct ROIC, so we calculate from available data
        # ROIC = EBIT / (Total Assets - Current Liabilities)
        # Or use returnOnEquity as a proxy if returnOnCapital not available
        roic = info.get('returnOnCapital')
        if roic is None:
            # Use ROE * (1 - debt ratio) as rough proxy
            roe = info.get('returnOnEquity')
            if roe is not None:
                debt_ratio = info.get('debtToEquity', 0)
                if debt_ratio and debt_ratio > 0:
                    # Rough ROIC approximation
                    result['roic'] = roe / (1 + debt_ratio / 100)
                else:
                    result['roic'] = roe
            else:
                result['roic'] = None
        else:
            result['roic'] = roic
        
        # Net Income
        result['net_income'] = info.get('netIncomeToCommon')
        
        # Buyback Yield calculation
        # buyback_yield = shares repurchased value / market cap
        market_cap = info.get('marketCap')
        shares_repurchased = info.get('sharesRepurchased')
        if market_cap and shares_repurchased and market_cap > 0:
            result['buyback_yield'] = shares_repurchased / market_cap
        else:
            result['buyback_yield'] = None
            
    except Exception as e:
        # Return None for all metrics on error
        result['pe_ratio'] = None
        result['debt_to_equity'] = None
        result['leverage_ratio'] = None
        result['roic'] = None
        result['net_income'] = None
        result['buyback_yield'] = None
        
    return result


def calculate_fundamental_features(tickers: list) -> pd.DataFrame:
    """
    Fetches fundamental data from yfinance for a list of tickers.
    Uses parallel execution for speed.
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        DataFrame with tickers as index and fundamental metrics as columns
    """
    print(f"Fetching fundamental data for {len(tickers)} tickers...")
    
    results = []
    failed_count = 0
    
    # Use ThreadPoolExecutor for parallel fetching
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {
            executor.submit(_fetch_single_ticker_fundamentals, ticker): ticker 
            for ticker in tickers
        }
        
        for i, future in enumerate(as_completed(future_to_ticker)):
            ticker = future_to_ticker[future]
            try:
                result = future.result()
                results.append(result)
                
                # Check if we got any valid data
                has_data = any(v is not None for k, v in result.items() if k != 'ticker')
                if not has_data:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                results.append({
                    'ticker': ticker,
                    'pe_ratio': None,
                    'debt_to_equity': None,
                    'leverage_ratio': None,
                    'roic': None,
                    'net_income': None,
                    'buyback_yield': None
                })
            
            # Progress update every 50 tickers
            if (i + 1) % 50 == 0:
                print(f"   ... processed {i + 1}/{len(tickers)} tickers")
    
    df = pd.DataFrame(results).set_index('ticker')
    
    # Summary stats
    valid_counts = df.notna().sum()
    print(f"[FUNDAMENTAL] Fetched data for {len(tickers)} tickers ({failed_count} failed)")
    for col in df.columns:
        print(f"   {col}: {valid_counts[col]} valid values")
    
    return df

if __name__ == "__main__":
    # Test Run
    prices = fetch_all_prices()
    if not prices.empty:
        df_feats = calculate_complex_features(prices)
        print("\n--- Calculated Features Sample ---")
        print(df_feats.head())
        print(f"\nTotal Stocks Processed: {len(df_feats)}")
        
    else:
        print("Database is empty. Run ingest_prices.py first.")