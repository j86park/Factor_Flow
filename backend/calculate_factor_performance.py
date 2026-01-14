"""
Calculate performance metrics for each statistical factor.
For each factor, compute the equal-weighted average return of its constituent stocks.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv
from calculate_features import fetch_all_prices

# Setup
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Time periods in trading days (approximate)
PERIODS = {
    "perf_1d": 1,
    "perf_5d": 5,
    "perf_1m": 21,
    "perf_3m": 63,
    "perf_6m": 126,
    "perf_1y": 252,
}


def get_factor_holdings() -> dict[int, list[str]]:
    """
    Fetch the latest factor results from both statistical and thematic tables,
    and group tickers by factor_id.
    Returns: {factor_id: [ticker1, ticker2, ...]}
    """
    holdings = {}
    
    # =========================================================================
    # Part 1: Fetch from factor_results_statistical
    # =========================================================================
    print("Fetching factor holdings from factor_results_statistical...")
    
    # Get the most recent run_date for statistical
    response = (
        supabase.table("factor_results_statistical")
        .select("run_date")
        .order("run_date", desc=True)
        .limit(1)
        .execute()
    )
    
    statistical_count = 0
    if response.data:
        latest_date_stat = response.data[0]["run_date"]
        print(f"  Using statistical results from {latest_date_stat}")
        
        # Fetch all results for the latest run (with pagination)
        offset = 0
        page_size = 1000
        
        while True:
            response = (
                supabase.table("factor_results_statistical")
                .select("factor_id, ticker")
                .eq("run_date", latest_date_stat)
                .range(offset, offset + page_size - 1)
                .execute()
            )
            
            if not response.data:
                break
            
            for row in response.data:
                fid = row["factor_id"]
                ticker = row["ticker"]
                if fid not in holdings:
                    holdings[fid] = set()  # Use set to avoid duplicates
                holdings[fid].add(ticker)
                statistical_count += 1
            
            if len(response.data) < page_size:
                break
            offset += page_size
        
        print(f"  Found {statistical_count} holdings from statistical factors")
    else:
        print("  ⚠️ No statistical factor results found.")
    
    # =========================================================================
    # Part 2: Fetch from factor_results_thematic
    # =========================================================================
    print("Fetching factor holdings from factor_results_thematic...")
    
    # Get the most recent run_date for thematic
    response = (
        supabase.table("factor_results_thematic")
        .select("run_date")
        .order("run_date", desc=True)
        .limit(1)
        .execute()
    )
    
    thematic_count = 0
    if response.data:
        latest_date_thematic = response.data[0]["run_date"]
        print(f"  Using thematic results from {latest_date_thematic}")
        
        # Fetch all results for the latest run (with pagination)
        offset = 0
        page_size = 1000
        
        while True:
            response = (
                supabase.table("factor_results_thematic")
                .select("factor_id, ticker")
                .eq("run_date", latest_date_thematic)
                .range(offset, offset + page_size - 1)
                .execute()
            )
            
            if not response.data:
                break
            
            for row in response.data:
                fid = row["factor_id"]
                ticker = row["ticker"]
                if fid not in holdings:
                    holdings[fid] = set()  # Use set to avoid duplicates
                holdings[fid].add(ticker)
                thematic_count += 1
            
            if len(response.data) < page_size:
                break
            offset += page_size
        
        print(f"  Found {thematic_count} holdings from thematic factors")
    else:
        print("  ⚠️ No thematic factor results found.")
    
    # =========================================================================
    # Convert sets to lists and summarize
    # =========================================================================
    holdings = {fid: list(tickers) for fid, tickers in holdings.items()}
    total_holdings = sum(len(t) for t in holdings.values())
    
    print(f"Found {len(holdings)} total factors with {total_holdings} total holdings")
    return holdings


def get_factor_names() -> dict[int, str]:
    """Fetch factor names from the factors table."""
    response = supabase.table("factors").select("id, name").execute()
    return {row["id"]: row["name"] for row in response.data}


def calculate_period_return(price_matrix: pd.DataFrame, tickers: list[str], days: int) -> float:
    """
    Calculate the equal-weighted average return for a list of tickers over N trading days.
    Return is calculated from (today - N days) to today.
    """
    if len(price_matrix) <= days:
        return np.nan
    
    # Filter to tickers that exist in price_matrix
    valid_tickers = [t for t in tickers if t in price_matrix.columns]
    if not valid_tickers:
        return np.nan
    
    # Get prices at start and end
    end_prices = price_matrix[valid_tickers].iloc[-1]
    start_prices = price_matrix[valid_tickers].iloc[-days - 1]
    
    # Calculate returns for each ticker
    returns = (end_prices / start_prices) - 1
    
    # Equal-weighted average (ignore NaN)
    avg_return = returns.mean()
    
    return avg_return if not pd.isna(avg_return) else np.nan


def calculate_all_factor_performance(price_matrix: pd.DataFrame, holdings: dict[int, list[str]]) -> pd.DataFrame:
    """
    Calculate performance metrics for all factors.
    Returns a DataFrame with factor_id as index and period returns as columns.
    """
    results = []
    
    for factor_id, tickers in holdings.items():
        row = {"factor_id": factor_id, "num_holdings": len(tickers)}
        
        for period_name, days in PERIODS.items():
            ret = calculate_period_return(price_matrix, tickers, days)
            row[period_name] = ret
        
        results.append(row)
    
    return pd.DataFrame(results)


def upload_factor_performance(df: pd.DataFrame, factor_names: dict[int, str]):
    """Upload factor performance to Supabase."""
    today = datetime.now().date().isoformat()
    
    records = []
    for _, row in df.iterrows():
        factor_id = int(row["factor_id"])
        records.append({
            "factor_id": factor_id,
            "run_date": today,
            "num_holdings": int(row["num_holdings"]),
            "perf_1d": float(row["perf_1d"]) if not pd.isna(row["perf_1d"]) else None,
            "perf_5d": float(row["perf_5d"]) if not pd.isna(row["perf_5d"]) else None,
            "perf_1m": float(row["perf_1m"]) if not pd.isna(row["perf_1m"]) else None,
            "perf_3m": float(row["perf_3m"]) if not pd.isna(row["perf_3m"]) else None,
            "perf_6m": float(row["perf_6m"]) if not pd.isna(row["perf_6m"]) else None,
            "perf_1y": float(row["perf_1y"]) if not pd.isna(row["perf_1y"]) else None,
        })
    
    if records:
        # Clear old results for today
        supabase.table("factor_performance").delete().eq("run_date", today).execute()
        
        # Insert new results
        supabase.table("factor_performance").insert(records).execute()
        print(f"✅ Uploaded performance for {len(records)} factors")


def run_factor_performance():
    """Main function to calculate and display factor performance."""
    print("--- CALCULATING FACTOR PERFORMANCE ---\n")
    
    # 1. Get factor holdings
    holdings = get_factor_holdings()
    if not holdings:
        return
    
    # 2. Get factor names
    factor_names = get_factor_names()
    
    # 3. Fetch price data (need more history for 1y calculation)
    print("\nFetching price history...")
    price_matrix = fetch_all_prices(lookback_days=400)
    
    if price_matrix.empty:
        print("⚠️ No price data available.")
        return
    
    # 4. Calculate performance
    print("\nCalculating factor performance...")
    df_performance = calculate_all_factor_performance(price_matrix, holdings)
    
    # 5. Add factor names for display
    df_performance["factor_name"] = df_performance["factor_id"].map(factor_names)
    
    # Reorder columns for display
    cols = ["factor_id", "factor_name", "num_holdings", "perf_1d", "perf_5d", "perf_1m", "perf_3m", "perf_6m", "perf_1y"]
    df_display = df_performance[[c for c in cols if c in df_performance.columns]]
    
    # Format percentages for display
    print("\n" + "=" * 100)
    print("FACTOR PERFORMANCE SUMMARY")
    print("=" * 100)
    
    # Pretty print
    for _, row in df_display.iterrows():
        name = row.get("factor_name", f"Factor {row['factor_id']}")
        holdings_count = row["num_holdings"]
        
        perfs = []
        for period in ["perf_1d", "perf_5d", "perf_1m", "perf_3m", "perf_6m", "perf_1y"]:
            val = row.get(period)
            if pd.notna(val):
                pct = val * 100
                sign = "+" if pct >= 0 else ""
                perfs.append(f"{period.replace('perf_', '')}: {sign}{pct:.2f}%")
            else:
                perfs.append(f"{period.replace('perf_', '')}: N/A")
        
        print(f"\n📊 {name} ({holdings_count} stocks)")
        print(f"   {' | '.join(perfs)}")
    
    print("\n" + "=" * 100)
    
    # 6. Try to upload (will fail gracefully if table doesn't exist)
    try:
        upload_factor_performance(df_performance, factor_names)
    except Exception as e:
        print(f"\n⚠️ Could not upload to factor_performance table: {e}")
        print("   Run create_performance_table.sql to create the table.")
    
    return df_performance


if __name__ == "__main__":
    run_factor_performance()

