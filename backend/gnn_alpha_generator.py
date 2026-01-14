"""
GNN Alpha Generator - Main Runner Script

Orchestrates the full pipeline:
1. Fetch price data from Supabase
2. Calculate features
3. Build market graph
4. Train GNN model
5. Generate predictions
6. Upload top predictions to Supabase

Usage:
    python gnn_alpha_generator.py
"""

import os
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Local imports
from calculate_features import fetch_all_prices, calculate_complex_features
from graph_builder import build_market_graph, get_device
from gnn_model import MarketGAT, AlphaPredictor

# ============================================================================
# SETUP
# ============================================================================
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        print(f"Warning: Could not initialize Supabase client: {e}")
else:
    print("Warning: Supabase credentials not found. Upload will be skipped.")

# Factor configuration
FACTOR_NAME = "AI Alpha: Weekly Top 10%"
FACTOR_TYPE = "ML_PREDICT"
FACTOR_DESCRIPTION = "GNN-predicted top 10% stocks for next week's returns"

# Training configuration
EPOCHS = 100
LEARNING_RATE = 0.001
TOP_PERCENTILE = 0.90  # Top 10% = rank > 0.90


# ============================================================================
# TARGET GENERATION
# ============================================================================
def prepare_training_data(
    price_matrix: pd.DataFrame,
    feature_df: pd.DataFrame,
    forward_days: int = 5,
) -> tuple:
    """
    Prepare training data with forward returns as targets.
    
    Args:
        price_matrix: Price data (dates x tickers)
        feature_df: Features (tickers x features)
        forward_days: Days ahead for target calculation (default 5 = 1 week)
    
    Returns:
        tuple: (aligned_features, targets, valid_tickers)
    """
    # Calculate forward log returns (next week's return)
    log_prices = np.log(price_matrix)
    forward_returns = log_prices.shift(-forward_days) - log_prices
    
    # Get the most recent forward return that we can use for training
    # (We need to exclude the last `forward_days` rows since we don't have future data)
    latest_returns = forward_returns.iloc[-(forward_days + 1)]  # Last row with known target
    
    # Align with features
    common_tickers = sorted(set(feature_df.index) & set(latest_returns.index))
    
    # Drop stocks with NaN in either features or returns
    valid_tickers = []
    for ticker in common_tickers:
        if not pd.isna(latest_returns[ticker]) and ticker in feature_df.index:
            if not feature_df.loc[ticker].isna().any():
                valid_tickers.append(ticker)
    
    print(f"[DATA] Prepared {len(valid_tickers)} stocks with valid targets")
    
    # Extract aligned data
    aligned_features = feature_df.loc[valid_tickers]
    targets = latest_returns[valid_tickers].values
    
    return aligned_features, targets, valid_tickers


# ============================================================================
# SUPABASE OPERATIONS
# ============================================================================
def get_or_create_factor() -> int | None:
    """
    Get the factor ID for our GNN predictions, creating it if necessary.
    
    Returns:
        Factor ID or None if Supabase is not available
    """
    if not supabase:
        return None
    
    # Check if factor exists
    response = supabase.table("factors").select("id").eq("name", FACTOR_NAME).execute()
    
    if response.data:
        factor_id = response.data[0]["id"]
        print(f"[OK] Found existing factor: {FACTOR_NAME} (ID: {factor_id})")
        return factor_id
    
    # Create new factor
    print(f"[NEW] Creating new factor: {FACTOR_NAME}")
    response = supabase.table("factors").insert({
        "name": FACTOR_NAME,
        "description": FACTOR_DESCRIPTION,
        "type": FACTOR_TYPE,
        "is_active": True,
        "logic_config": {
            "metric": "gnn_predicted_return",
            "rule": "top_percentile",
            "value": 0.10
        }
    }).execute()
    
    if response.data:
        factor_id = response.data[0]["id"]
        print(f"[OK] Created factor with ID: {factor_id}")
        return factor_id
    
    print("[ERROR] Failed to create factor")
    return None


def upload_predictions(
    factor_id: int,
    tickers: list,
    predictions: np.ndarray,
    top_percentile: float = TOP_PERCENTILE,
) -> int:
    """
    Upload top predictions to Supabase.
    
    Args:
        factor_id: Factor ID in database
        tickers: List of ticker symbols
        predictions: Array of predicted returns
        top_percentile: Percentile cutoff for top stocks
    
    Returns:
        Number of uploaded records
    """
    if not supabase:
        print("[WARN] Supabase not available. Skipping upload.")
        return 0
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate percentile ranks
    df = pd.DataFrame({
        "ticker": tickers,
        "predicted_return": predictions.flatten(),
    })
    df["percentile_rank"] = df["predicted_return"].rank(pct=True)
    
    # Filter for top performers
    top_stocks = df[df["percentile_rank"] >= top_percentile].copy()
    top_stocks = top_stocks.sort_values("predicted_return", ascending=False)
    
    print(f"\n[TOP] Top {len(top_stocks)} stocks (>={top_percentile*100:.0f}th percentile):")
    for _, row in top_stocks.head(10).iterrows():
        print(f"   {row['ticker']}: {row['predicted_return']*100:+.2f}% (rank: {row['percentile_rank']:.2f})")
    
    # Prepare records for upload
    records = []
    for _, row in top_stocks.iterrows():
        records.append({
            "factor_id": factor_id,
            "ticker": row["ticker"],
            "metric_value": float(row["predicted_return"]),
            "percentile_rank": float(row["percentile_rank"]),
            "run_date": today,
        })
    
    if not records:
        print("[WARN] No stocks passed the percentile filter.")
        return 0
    
    # Clear old results for today
    supabase.table("factor_results_statistical").delete().eq(
        "factor_id", factor_id
    ).eq("run_date", today).execute()
    
    # Batch upload
    batch_size = 500
    uploaded = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        supabase.table("factor_results_statistical").insert(batch).execute()
        uploaded += len(batch)
    
    print(f"[OK] Uploaded {uploaded} signals to Supabase.")
    return uploaded


# ============================================================================
# TRAINING LOOP
# ============================================================================
def train_model(
    model: AlphaPredictor,
    data,
    targets: torch.Tensor,
    device: torch.device,
    epochs: int = EPOCHS,
    lr: float = LEARNING_RATE,
) -> AlphaPredictor:
    """
    Train the AlphaPredictor model.
    
    Args:
        model: AlphaPredictor model
        data: PyTorch Geometric Data object
        targets: Target returns tensor
        device: Device to train on
        epochs: Number of training epochs
        lr: Learning rate
    
    Returns:
        Trained model
    """
    model = model.to(device)
    data = data.to(device)
    targets = targets.to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    criterion = nn.MSELoss()
    
    print(f"\n[TRAIN] Training for {epochs} epochs...")
    print("-" * 40)
    
    model.train()
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        
        # Forward pass
        predictions = model(data)
        loss = criterion(predictions.squeeze(), targets)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Log progress
        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch {epoch:3d}/{epochs}: Loss = {loss.item():.6f}")
    
    print("-" * 40)
    print(f"[OK] Training complete. Final loss: {loss.item():.6f}")
    
    return model


# ============================================================================
# MAIN PIPELINE
# ============================================================================
def run_gnn_alpha_generator():
    """
    Main entry point for the GNN Alpha Generator pipeline.
    """
    print("=" * 60)
    print("GNN ALPHA GENERATOR - SOTA Weekly Return Predictor")
    print("=" * 60)
    
    # -------------------------------------------------------------------------
    # STEP 1: Fetch Data
    # -------------------------------------------------------------------------
    print("\n[STEP 1] Fetching price data...")
    prices = fetch_all_prices()
    
    if prices.empty:
        print("[ERROR] No price data found. Run ingest_prices.py first.")
        return
    
    # -------------------------------------------------------------------------
    # STEP 2: Calculate Features
    # -------------------------------------------------------------------------
    print("\n[STEP 2] Calculating features...")
    features = calculate_complex_features(prices)
    
    if features.empty:
        print("[ERROR] Could not calculate features.")
        return
    
    print(f"   Features: {list(features.columns)}")
    
    # -------------------------------------------------------------------------
    # STEP 3: Build Graph
    # -------------------------------------------------------------------------
    print("\n[STEP 3] Building market graph...")
    try:
        data, valid_tickers = build_market_graph(prices, features)
    except ValueError as e:
        print(f"[ERROR] Building graph: {e}")
        return
    
    # -------------------------------------------------------------------------
    # STEP 4: Prepare Training Data
    # -------------------------------------------------------------------------
    print("\n[STEP 4] Preparing training targets...")
    try:
        aligned_features, targets, target_tickers = prepare_training_data(
            prices, features, forward_days=5
        )
    except Exception as e:
        print(f"[ERROR] Preparing targets: {e}")
        return
    
    # Ensure alignment between graph and targets
    common_tickers = sorted(set(valid_tickers) & set(target_tickers))
    if len(common_tickers) < 10:
        print(f"[ERROR] Not enough common tickers: {len(common_tickers)}")
        return
    
    # Re-align data
    ticker_to_idx = {t: i for i, t in enumerate(valid_tickers)}
    common_indices = [ticker_to_idx[t] for t in common_tickers if t in ticker_to_idx]
    
    # Get targets for common tickers only
    target_to_idx = {t: i for i, t in enumerate(target_tickers)}
    aligned_targets = np.array([targets[target_to_idx[t]] for t in common_tickers])
    
    # Filter graph data to common tickers
    x_filtered = data.x[common_indices]
    
    # Rebuild edge index for filtered nodes
    new_idx_map = {old: new for new, old in enumerate(common_indices)}
    edge_list = []
    for i in range(data.edge_index.shape[1]):
        src, dst = data.edge_index[0, i].item(), data.edge_index[1, i].item()
        if src in new_idx_map and dst in new_idx_map:
            edge_list.append([new_idx_map[src], new_idx_map[dst]])
    
    if len(edge_list) > 0:
        edge_index_filtered = torch.LongTensor(edge_list).t().contiguous()
    else:
        # Create simple connections if no edges remain
        edge_list = [[i, (i + 1) % len(common_tickers)] for i in range(len(common_tickers))]
        edge_index_filtered = torch.LongTensor(edge_list).t().contiguous()
    
    from torch_geometric.data import Data
    filtered_data = Data(x=x_filtered, edge_index=edge_index_filtered)
    
    print(f"   Aligned {len(common_tickers)} stocks for training")
    
    # -------------------------------------------------------------------------
    # STEP 5: Initialize Model
    # -------------------------------------------------------------------------
    print("\n[STEP 5] Initializing model...")
    device = get_device()
    
    in_features = filtered_data.num_node_features
    gat = MarketGAT(in_features=in_features)
    model = AlphaPredictor(gat)
    
    print(f"   Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # -------------------------------------------------------------------------
    # STEP 6: Train Model
    # -------------------------------------------------------------------------
    print("\n[STEP 6] Training model...")
    targets_tensor = torch.FloatTensor(aligned_targets)
    
    # Handle NaN targets
    valid_mask = ~torch.isnan(targets_tensor)
    if valid_mask.sum() < 10:
        print("[ERROR] Not enough valid targets for training")
        return
    
    # Replace NaN with 0 for training (masked loss would be better but simpler for now)
    targets_tensor = torch.nan_to_num(targets_tensor, nan=0.0)
    
    model = train_model(model, filtered_data, targets_tensor, device)
    
    # -------------------------------------------------------------------------
    # STEP 7: Generate Predictions
    # -------------------------------------------------------------------------
    print("\n[STEP 7] Generating predictions...")
    model.eval()
    filtered_data = filtered_data.to(device)
    
    with torch.no_grad():
        predictions = model(filtered_data).cpu().numpy()
    
    print(f"   Generated predictions for {len(predictions)} stocks")
    
    # Show top picks
    pred_df = pd.DataFrame({
        "ticker": common_tickers,
        "predicted_return": predictions.flatten()
    }).sort_values("predicted_return", ascending=False)
    
    print("\n[TOP 5] Predicted Performers:")
    for _, row in pred_df.head(5).iterrows():
        print(f"   {row['ticker']}: {row['predicted_return']*100:+.2f}%")
    
    # -------------------------------------------------------------------------
    # STEP 8: Upload to Supabase
    # -------------------------------------------------------------------------
    print("\n[STEP 8] Uploading to Supabase...")
    factor_id = get_or_create_factor()
    
    if factor_id:
        uploaded = upload_predictions(
            factor_id=factor_id,
            tickers=common_tickers,
            predictions=predictions,
            top_percentile=TOP_PERCENTILE,
        )
        print(f"\n[DONE] Pipeline complete! Uploaded {uploaded} signals.")
    else:
        print("\n[WARN] Pipeline complete but upload skipped (no Supabase connection).")
    
    print("=" * 60)


if __name__ == "__main__":
    run_gnn_alpha_generator()
