"""
Calculate 252-day rolling Z-scores for factor performance and store in factor_zscore_history.

Z-score = (current_value - rolling_mean) / rolling_std

SMART MODE (per-factor):
- For each factor, check how many days of Z-score history exist
- If < 252 days: Backfill all historical Z-scores for that factor
- If >= 252 days: Only calculate today's Z-score

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

ROLLING_WINDOW = 252  


def get_zscore_counts_per_factor() -> dict[int, int]:
    """Get count of Z-score records per factor."""
    print("Checking existing Z-score history per factor...")
    
    all_data = []
    offset = 0
    page_size = 1000
    
    while True:
        response = (
            supabase.table("factor_zscore_history")
            .select("factor_id")
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
    
    # Count records per factor
    counts = {}
    for row in all_data:
        fid = row["factor_id"]
        counts[fid] = counts.get(fid, 0) + 1
    
    return counts


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


def calculate_zscores_smart(df: pd.DataFrame, zscore_counts: dict[int, int]) -> tuple[pd.DataFrame, list[int]]:
    """
    SMART MODE: Check each factor individually.
    - Backfill factors with < 252 days of Z-score history
    - Only today's Z-score for factors with >= 252 days
    """
    if df.empty:
        return pd.DataFrame(), []
    
    results = []
    backfilled_factors = []
    
    for factor_id in df["factor_id"].unique():
        factor_df = df[df["factor_id"] == factor_id].copy()
        factor_df = factor_df.sort_values("run_date")
        
        if len(factor_df) < ROLLING_WINDOW:
            print(f"  Factor {factor_id}: Only {len(factor_df)} perf days, need {ROLLING_WINDOW}. Skipping.")
            continue
        
        existing_count = zscore_counts.get(factor_id, 0)
        needs_backfill = existing_count < ROLLING_WINDOW
        
        if needs_backfill:
            # BACKFILL MODE for this factor
            print(f"  Factor {factor_id}: Only {existing_count} Z-score days → BACKFILLING all history")
            backfilled_factors.append(factor_id)
            
            # Calculate rolling mean and std for ALL days
            factor_df["rolling_mean"] = factor_df["perf_1d"].rolling(window=ROLLING_WINDOW, min_periods=ROLLING_WINDOW).mean()
            factor_df["rolling_std"] = factor_df["perf_1d"].rolling(window=ROLLING_WINDOW, min_periods=ROLLING_WINDOW).std()
            
            # Calculate Z-score
            factor_df["zscore"] = (factor_df["perf_1d"] - factor_df["rolling_mean"]) / factor_df["rolling_std"]
            factor_df["zscore"] = factor_df["zscore"].replace([np.inf, -np.inf], np.nan)
            
            valid_df = factor_df.dropna(subset=["zscore"])
            
            for _, row in valid_df.iterrows():
                results.append({
                    "factor_id": int(factor_id),
                    "date": row["run_date"].strftime("%Y-%m-%d"),
                    "zscore": float(row["zscore"]),
                    "factor_value": float(row["perf_1d"]) if pd.notna(row["perf_1d"]) else None,
                })
            print(f"           → Generated {len(valid_df)} Z-scores")
        else:
            # DAILY MODE for this factor
            recent_df = factor_df.tail(ROLLING_WINDOW)
            
            rolling_mean = recent_df["perf_1d"].mean()
            rolling_std = recent_df["perf_1d"].std()
            
            latest_row = recent_df.iloc[-1]
            today_value = latest_row["perf_1d"]
            today_date = latest_row["run_date"]
            
            if rolling_std > 0 and pd.notna(today_value):
                zscore = (today_value - rolling_mean) / rolling_std
                
                results.append({
                    "factor_id": int(factor_id),
                    "date": today_date.strftime("%Y-%m-%d"),
                    "zscore": float(zscore),
                    "factor_value": float(today_value),
                })
                print(f"  Factor {factor_id}: {existing_count} days → daily update, Z={zscore:.2f}")
    
    return pd.DataFrame(results), backfilled_factors


def upload_zscores(zscore_df: pd.DataFrame, backfilled_factors: list[int]):
    """Upload Z-score data to Supabase."""
    if zscore_df.empty:
        print("No Z-scores to upload.")
        return
    
    records = zscore_df.to_dict("records")
    print(f"\nUploading {len(records)} Z-score records...")
    
    # For backfilled factors, delete ALL their existing records first
    if backfilled_factors:
        print(f"  Clearing history for {len(backfilled_factors)} backfilled factors...")
        for fid in backfilled_factors:
            try:
                supabase.table("factor_zscore_history").delete().eq("factor_id", fid).execute()
            except Exception as e:
                print(f"  Error clearing factor {fid}: {e}")
    
    # For daily updates, clear just today's date
    daily_records = zscore_df[~zscore_df["factor_id"].isin(backfilled_factors)]
    if not daily_records.empty:
        unique_dates = daily_records["date"].unique().tolist()
        factor_ids = daily_records["factor_id"].unique().tolist()
        print(f"  Clearing today's records for {len(factor_ids)} daily factors...")
        for date in unique_dates:
            for fid in factor_ids:
                try:
                    supabase.table("factor_zscore_history").delete().eq("date", date).eq("factor_id", fid).execute()
                except Exception:
                    pass  # Ignore errors for non-existent records
    
    # Insert in batches
    batch_size = 500
    uploaded = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            supabase.table("factor_zscore_history").insert(batch).execute()
            uploaded += len(batch)
            print(f"  Uploaded batch {i//batch_size + 1}: {len(batch)} records")
        except Exception as e:
            print(f"  Error uploading batch: {e}")
    
    print(f"✅ Z-score upload complete. {uploaded} records inserted.")


def main():
    print("=" * 60)
    print("FACTOR Z-SCORE CALCULATOR (Smart Per-Factor Mode)")
    print("=" * 60)
    
    # Get existing Z-score counts per factor
    zscore_counts = get_zscore_counts_per_factor()
    print(f"Found Z-score history for {len(zscore_counts)} factors\n")
    
    # Fetch performance history
    perf_df = fetch_factor_performance_history()
    
    if perf_df.empty:
        print("No data to process. Run calculate_factor_performance.py first.")
        return
    
    # Calculate Z-scores (smart mode - per factor)
    print(f"\nProcessing {perf_df['factor_id'].nunique()} factors...\n")
    zscore_df, backfilled_factors = calculate_zscores_smart(perf_df, zscore_counts)
    
    if zscore_df.empty:
        print("No Z-scores calculated. Need at least 252 days of data per factor.")
        return
    
    print(f"\n📊 Summary:")
    print(f"   Backfilled factors: {len(backfilled_factors)}")
    print(f"   Daily updates: {len(zscore_df['factor_id'].unique()) - len(backfilled_factors)}")
    
    # Upload to Supabase
    upload_zscores(zscore_df, backfilled_factors)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
