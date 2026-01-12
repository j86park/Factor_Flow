"""
GNN Model Module - Graph Attention Network Architecture

Defines the MarketGAT neural network that learns node embeddings
from the market graph structure.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

# Import torch_geometric conditionally
try:
    from torch_geometric.nn import GATConv
except ImportError:
    raise ImportError(
        "torch_geometric not installed. Run: pip install torch-geometric torch-scatter torch-sparse"
    )


class MarketGAT(nn.Module):
    """
    Graph Attention Network for market structure learning.
    
    Architecture:
        Layer 1: GATConv (in_features → 64 hidden × 4 heads) + ELU + Dropout
        Layer 2: GATConv (64×4=256 → 32 output × 1 head)
    
    Output: 32-dimensional node embeddings for each stock
    """
    
    def __init__(
        self,
        in_features: int,
        hidden_channels: int = 64,
        out_channels: int = 32,
        heads: int = 4,
        dropout: float = 0.6,
    ):
        """
        Initialize the MarketGAT model.
        
        Args:
            in_features: Number of input features per node
            hidden_channels: Hidden dimension after first GAT layer
            out_channels: Output embedding dimension
            heads: Number of attention heads in first layer
            dropout: Dropout probability
        """
        super(MarketGAT, self).__init__()
        
        self.dropout = dropout
        
        # Layer 1: Multi-head attention
        # Output size = hidden_channels * heads = 64 * 4 = 256
        self.conv1 = GATConv(
            in_channels=in_features,
            out_channels=hidden_channels,
            heads=heads,
            dropout=dropout,
            concat=True,  # Concatenate multi-head outputs
        )
        
        # Layer 2: Single-head attention for final embeddings
        # Input size = hidden_channels * heads = 256
        # Output size = out_channels = 32
        self.conv2 = GATConv(
            in_channels=hidden_channels * heads,
            out_channels=out_channels,
            heads=1,
            dropout=dropout,
            concat=False,  # Average multi-head outputs
        )
    
    def forward(self, data) -> torch.Tensor:
        """
        Forward pass through the GAT.
        
        Args:
            data: PyTorch Geometric Data object with x and edge_index
        
        Returns:
            Node embeddings of shape (num_nodes, out_channels)
        """
        x, edge_index = data.x, data.edge_index
        
        # Layer 1
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.conv1(x, edge_index)
        x = F.elu(x)
        
        # Layer 2
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.conv2(x, edge_index)
        
        return x


class AlphaPredictor(nn.Module):
    """
    Complete Alpha Prediction model.
    
    Combines the MarketGAT encoder with a prediction head
    to output predicted returns for each stock.
    
    Architecture:
        MarketGAT (→ 32-dim embeddings)
        → Linear(32 → 16) → ReLU → Dropout
        → Linear(16 → 1) → Predicted Return
    """
    
    def __init__(
        self,
        gat_model: MarketGAT,
        embedding_dim: int = 32,
        hidden_dim: int = 16,
        dropout: float = 0.3,
    ):
        """
        Initialize the AlphaPredictor.
        
        Args:
            gat_model: Pre-initialized MarketGAT model
            embedding_dim: Dimension of GAT output embeddings
            hidden_dim: Hidden dimension in prediction head
            dropout: Dropout probability in prediction head
        """
        super(AlphaPredictor, self).__init__()
        
        self.gat = gat_model
        
        # Prediction head: embeddings → predicted return
        self.predictor = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )
    
    def forward(self, data) -> torch.Tensor:
        """
        Forward pass to predict returns.
        
        Args:
            data: PyTorch Geometric Data object
        
        Returns:
            Predicted returns of shape (num_nodes, 1)
        """
        # Get node embeddings from GAT
        embeddings = self.gat(data)
        
        # Predict returns
        predictions = self.predictor(embeddings)
        
        return predictions


if __name__ == "__main__":
    # Quick architecture test
    print("Testing MarketGAT Architecture...")
    
    # Create dummy data
    num_nodes = 100
    in_features = 7  # Number of features from calculate_features.py
    
    x = torch.randn(num_nodes, in_features)
    edge_index = torch.randint(0, num_nodes, (2, 500))
    
    from torch_geometric.data import Data
    data = Data(x=x, edge_index=edge_index)
    
    # Initialize models
    gat = MarketGAT(in_features=in_features)
    model = AlphaPredictor(gat)
    
    print(f"\nModel Architecture:")
    print(model)
    
    # Forward pass
    model.eval()
    with torch.no_grad():
        predictions = model(data)
    
    print(f"\n✅ Forward pass successful!")
    print(f"   Input: {num_nodes} nodes × {in_features} features")
    print(f"   Output: {predictions.shape}")
