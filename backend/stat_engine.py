import os
import pandas as pd
import numpy as np
from supabase import create_client, Client
from calculate_features import fetch_all_prices, calculate_complex_features, calculate_fundamental_features
from dotenv import load_dotenv

# 1. SETUP
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def run_statistical_engine():
    print("--- STARTING STATISTICAL ENGINE ---")
    
    prices = fetch_all_prices()
    if prices.empty:
        print("Error: No price data found. Run ingest_prices.py first.")
        return

    # 'df_features' now holds Beta, Rezzy, Momentum for EVERY stock
    df_features = calculate_complex_features(prices)
    
    # Add fundamental features (PE, D/E, ROIC, etc.)
    df_fundamental = calculate_fundamental_features(df_features.index.tolist())
    df_features = pd.concat([df_features, df_fundamental], axis=1)
    
    print(f"Computed metrics for {len(df_features)} stocks.")

    # STEP 2: FETCH RULES (From Supabase)
    print("Fetching factor definitions...")
    response = supabase.table("factors") \
        .select("*") \
        .eq("type", "STATISTICAL") \
        .eq("is_active", True) \
        .execute()
    
    factors = response.data
    results_to_upload = []

    # STEP 3: APPLY LOGIC (The Filtering)
    for f in factors:
        config = f['logic_config']
        metric_name = config.get('metric') # e.g., 'volatility_90d'
        rule = config.get('rule')          # e.g., 'top_percentile'
        threshold = config.get('value')    # e.g., 0.10

        # Safety Check: Does this metric exist in our calculations?
        if metric_name not in df_features.columns:
            # Only print warning if it's not a known missing metric (like 13F data)
            if "hf_" not in metric_name: 
                print(f"Skipping '{f['name']}': Metric '{metric_name}' not calculated.")
            continue

        # Get the specific column of data (drop NaNs to avoid errors)
        series = df_features[metric_name].dropna()
        
        # Determine the Cutoff Value
        matches = []
        
        if rule == 'top_percentile':
            # e.g., Top 10% means percentile > 0.90
            cutoff = series.quantile(1.0 - threshold)
            matches = series[series >= cutoff]
            
        elif rule == 'bottom_percentile':
            # e.g., Bottom 10% means percentile < 0.10
            cutoff = series.quantile(threshold)
            matches = series[series <= cutoff]
            
        elif rule == 'greater_than':
            matches = series[series > threshold]
            
        elif rule == 'less_than':
            matches = series[series < threshold]
            
        elif rule == 'equals':
            matches = series[series == threshold]

        # Prepare Results for Upload
        # We assume 'matches' is a Series where Index=Ticker, Value=Metric
        for ticker, val in matches.items():
            # Optional: Calculate exact rank (0.0 to 1.0) for the UI
            # (Simple rank calculation relative to full universe)
            rank = series.rank(pct=True)[ticker]
            
            results_to_upload.append({
                "factor_id": f['id'],
                "ticker": ticker,
                "metric_value": float(val),     # The raw number (e.g., 1.5 Beta)
                "percentile_rank": float(rank), # The percentile (e.g., 0.99)
                "run_date": pd.Timestamp.now().strftime('%Y-%m-%d')
            })

    # STEP 4: UPLOAD (Batch Insert)
    if results_to_upload:
        print(f"Found {len(results_to_upload)} total matches across {len(factors)} factors.")
        
        # Clear old results for today (to avoid duplicates if re-run)
        today = pd.Timestamp.now().strftime('%Y-%m-%d')
        # Note: In a real prod env, you might delete by specific factor_ids instead
        supabase.table("factor_results_statistical").delete().eq("run_date", today).execute()
        
        # Batch insert (Supabase limit is usually ~10k rows per request)
        batch_size = 1000
        for i in range(0, len(results_to_upload), batch_size):
            batch = results_to_upload[i:i + batch_size]
            supabase.table("factor_results_statistical").insert(batch).execute()
            print(f"Uploaded batch {i} - {i+len(batch)}")
            
        print("Success! Statistical Engine complete.")
    else:
        print("No matches found. Check your logic rules or data.")

if __name__ == "__main__":
    run_statistical_engine()