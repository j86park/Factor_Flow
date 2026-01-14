"""
Graph Builder Module for GNN Alpha Generator

Transforms raw tabular price/feature data into a PyTorch Geometric graph structure.
This module acts as the bridge between calculate_features.py and the neural network.
"""

import sys
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Import torch_geometric conditionally to handle installation issues gracefully
try:
    from torch_geometric.data import Data
except ImportError:
    raise ImportError(
        "torch_geometric not installed. Run: pip install torch-geometric torch-scatter torch-sparse"
    )


def build_market_graph(
    price_matrix: pd.DataFrame,
    feature_df: pd.DataFrame,
    correlation_threshold: float = 0.65,
) -> tuple:
    """
    Build a market graph from price and feature data.
    
    Args:
        price_matrix: DataFrame with dates as index and tickers as columns (close prices)
        feature_df: DataFrame with tickers as index and features as columns
        correlation_threshold: Minimum absolute correlation to create an edge (default 0.65)
    
    Returns:
        tuple: (Data object with x and edge_index, list of tickers)
    """
    # =========================================================================
    # STEP 1: Align tickers between price matrix and features
    # =========================================================================
    price_tickers = set(price_matrix.columns)
    feature_tickers = set(feature_df.index)
    common_tickers = sorted(price_tickers & feature_tickers)
    
    if len(common_tickers) == 0:
        raise ValueError("No common tickers between price_matrix and feature_df")
    
    print(f"[GRAPH] Building graph with {len(common_tickers)} stocks")
    
    # Filter to common tickers
    price_matrix = price_matrix[common_tickers]
    feature_df = feature_df.loc[common_tickers]
    
    # =========================================================================
    # STEP 2: Create Node Features (x) - Normalized with StandardScaler
    # =========================================================================
    # Drop rows with any NaN values for clean training
    feature_df_clean = feature_df.dropna()
    valid_tickers = list(feature_df_clean.index)
    
    if len(valid_tickers) < 10:
        raise ValueError(f"Only {len(valid_tickers)} stocks with complete features. Need at least 10.")
    
    print(f"   [OK] {len(valid_tickers)} stocks have complete feature data")
    
    # Normalize features: mean=0, std=1
    scaler = StandardScaler()
    node_features = scaler.fit_transform(feature_df_clean.values)
    x = torch.FloatTensor(node_features)
    
    print(f"   [OK] Node features shape: {x.shape}")
    
    # =========================================================================
    # STEP 3: Create Edges based on correlation (edge_index)
    # =========================================================================
    # Calculate log returns for correlation
    log_returns = np.log(price_matrix[valid_tickers] / price_matrix[valid_tickers].shift(1)).dropna()
    
    # Correlation matrix
    corr_matrix = log_returns.corr().values
    
    # Find edges: |correlation| > threshold (excluding self-loops)
    num_stocks = len(valid_tickers)
    edge_list = []
    
    for i in range(num_stocks):
        for j in range(num_stocks):
            if i != j and abs(corr_matrix[i, j]) > correlation_threshold:
                edge_list.append([i, j])
    
    if len(edge_list) == 0:
        print(f"   [WARN] No edges found with threshold {correlation_threshold}. Lowering to 0.5...")
        for i in range(num_stocks):
            for j in range(num_stocks):
                if i != j and abs(corr_matrix[i, j]) > 0.5:
                    edge_list.append([i, j])
    
    if len(edge_list) == 0:
        # Create a simple k-nearest neighbor graph as fallback
        print("   [WARN] Still no edges. Creating 5-NN graph based on correlation...")
        for i in range(num_stocks):
            # Get top 5 correlated stocks (excluding self)
            corrs = [(j, abs(corr_matrix[i, j])) for j in range(num_stocks) if i != j]
            corrs.sort(key=lambda x: x[1], reverse=True)
            for j, _ in corrs[:5]:
                edge_list.append([i, j])
    
    edge_index = torch.LongTensor(edge_list).t().contiguous()
    
    print(f"   [OK] Created {edge_index.shape[1]} edges (avg {edge_index.shape[1] / num_stocks:.1f} per node)")
    
    # =========================================================================
    # STEP 4: Build PyTorch Geometric Data object
    # =========================================================================
    data = Data(x=x, edge_index=edge_index)
    
    return data, valid_tickers


def get_device() -> torch.device:
    """Get the best available device (CUDA > CPU)."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"[GPU] Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("[CPU] Using CPU (CUDA not available)")
    return device


if __name__ == "__main__":
    # Test the graph builder
    from calculate_features import fetch_all_prices, calculate_complex_features
    
    print("Testing Graph Builder...")
    prices = fetch_all_prices()
    
    if not prices.empty:
        features = calculate_complex_features(prices)
        data, tickers = build_market_graph(prices, features)
        
        print(f"\n[OK] Graph Built Successfully!")
        print(f"   Nodes: {data.num_nodes}")
        print(f"   Edges: {data.num_edges}")
        print(f"   Features per node: {data.num_node_features}")
        print(f"   Sample tickers: {tickers[:5]}")
    else:
        print("No price data available.")
