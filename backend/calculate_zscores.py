"""
Calculate 252-day rolling Z-scores for factor performance and store in factor_zscore_history.

Z-score = (current_value - rolling_mean) / rolling_std

Run this script after factor_performance has been populated.
"""

import os
import pandas as pd
import numpy as np
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv

# Setup
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Supabase credentials missing. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

ROLLING_WINDOW = 252  # Trading days in a year


def fetch_factor_performance_history():
    """Fetch all factor performance data ordered by date."""
    print("Fetching factor performance history...")
    
    all_data = []
    offset = 0
    page_size = 1000
    
    while True:
        response = (
            supabase.table("factor_performance")
            .select("factor_id, run_date, perf_1d")
            .order("run_date", desc=False)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        
        if response.data:
            all_data.extend(response.data)
            offset += len(response.data)
            if len(response.data) < page_size:
                break
        else:
            break
    
    if not all_data:
        print("No factor performance data found.")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_data)
    df["run_date"] = pd.to_datetime(df["run_date"])
    print(f"Fetched {len(df)} performance records for {df['factor_id'].nunique()} factors")
    return df


def calculate_rolling_zscores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate 252-day rolling Z-scores for each factor."""
    if df.empty:
        return pd.DataFrame()
    
    print(f"Calculating {ROLLING_WINDOW}-day rolling Z-scores...")
    
    results = []
    
    for factor_id in df["factor_id"].unique():
        factor_df = df[df["factor_id"] == factor_id].copy()
        factor_df = factor_df.sort_values("run_date")
        
        if len(factor_df) < ROLLING_WINDOW:
            print(f"  Factor {factor_id}: Only {len(factor_df)} days, need {ROLLING_WINDOW}. Skipping.")
            continue
        
        # Calculate rolling mean and std
        factor_df["rolling_mean"] = factor_df["perf_1d"].rolling(window=ROLLING_WINDOW, min_periods=ROLLING_WINDOW).mean()
        factor_df["rolling_std"] = factor_df["perf_1d"].rolling(window=ROLLING_WINDOW, min_periods=ROLLING_WINDOW).std()
        
        # Calculate Z-score
        factor_df["zscore"] = (factor_df["perf_1d"] - factor_df["rolling_mean"]) / factor_df["rolling_std"]
        
        # Handle division by zero (std = 0)
        factor_df["zscore"] = factor_df["zscore"].replace([np.inf, -np.inf], np.nan)
        
        # Only keep rows where we have valid Z-scores
        valid_df = factor_df.dropna(subset=["zscore"])
        
        if len(valid_df) > 0:
            for _, row in valid_df.iterrows():
                results.append({
                    "factor_id": int(factor_id),
                    "date": row["run_date"].strftime("%Y-%m-%d"),
                    "zscore": float(row["zscore"]),
                    "factor_value": float(row["perf_1d"]) if pd.notna(row["perf_1d"]) else None,
                })
            print(f"  Factor {factor_id}: Calculated {len(valid_df)} Z-scores")
    
    return pd.DataFrame(results)


def upload_zscores(zscore_df: pd.DataFrame):
    """Upload Z-score data to Supabase."""
    if zscore_df.empty:
        print("No Z-scores to upload.")
        return
    
    records = zscore_df.to_dict("records")
    print(f"Uploading {len(records)} Z-score records...")
    
    # Upsert in batches
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            supabase.table("factor_zscore_history").upsert(batch).execute()
            print(f"  Uploaded batch {i} - {i + len(batch)}")
        except Exception as e:
            print(f"  Error uploading batch: {e}")
    
    print("✅ Z-score upload complete.")


def main():
    print("--- CALCULATING FACTOR Z-SCORES ---")
    
    # Fetch performance history
    perf_df = fetch_factor_performance_history()
    
    if perf_df.empty:
        print("No data to process. Run calculate_factor_performance.py first.")
        return
    
    # Calculate Z-scores
    zscore_df = calculate_rolling_zscores(perf_df)
    
    if zscore_df.empty:
        print("No Z-scores calculated. Need at least 252 days of data per factor.")
        return
    
    # Upload to Supabase
    upload_zscores(zscore_df)
    
    print("Done!")


if __name__ == "__main__":
    main()
