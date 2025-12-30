import os
import pandas as pd
import numpy as np
from supabase import create_client, Client
import dotenv

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

def fetch_all_prices():
    """
    Downloads the entire price history from Supabase efficiently.
    Returns a MultiIndex DataFrame (Date, Ticker).
    """
    print("Fetching price history from database...")
    # fetch only necessary columns to save memory
    response = supabase.table("stock_prices").select("ticker, date, close").execute()
    
    df = pd.DataFrame(response.data)
    df['date'] = pd.to_datetime(df['date'])
    
    price_matrix = df.pivot(index='date', columns='ticker', values='close')
    return price_matrix.sort_index()

def _safe_lookback(series_length: int, lookback: int, label: str) -> bool:
    if series_length <= lookback:
        print(f"⚠️ Not enough history ({series_length}) for {label} ({lookback} days).")
        return False
    return True


def calculate_complex_features(price_matrix):
    """
    Computes SOTA metrics: Beta, Residual Volatility, Momentum.
    """
    features = pd.DataFrame(index=price_matrix.columns)
    if price_matrix.empty:
        print("⚠️ Price matrix is empty. Skipping feature calculation.")
        return features

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
        print("⚠️ Not enough data for 90-day volatility.")
        features["volatility_90d"] = np.nan
    
    # 2. MOMENTUM (Simple Rolling Math)
    print("Calculating Momentum & Volatility...")
    # 12-Month Return (approx 252 trading days)
    features['return_12m'] = price_matrix.iloc[-1] / price_matrix.iloc[-252] - 1
    # 3-Month Return (approx 63 trading days)
    features['return_3m'] = price_matrix.iloc[-1] / price_matrix.iloc[-63] - 1
    # 1-Month Return (approx 21 trading days)
    features['return_1m'] = price_matrix.iloc[-1] / price_matrix.iloc[-21] - 1
    
    # Volatility (90-day annualized std dev)
    features['volatility_90d'] = log_rets.rolling(window=90).std().iloc[-1] * np.sqrt(252)

    # 3. REGRESSION METRICS (Beta & Rezzy)
    # We regress every stock against SPY to find "Alpha" and "Idiosyncratic Risk"
    print("Calculating Beta and Residuals (Regression)...")
    
    if BENCHMARK_TICKER not in log_rets.columns:
        print(f"Warning: {BENCHMARK_TICKER} not found. Skipping Beta calculations.")
        return features

    market_rets = log_rets[BENCHMARK_TICKER].dropna()
    
    betas = []
    residual_vols = []
    
    # Loop efficiently only for regression (hard to vectorize perfectly)
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