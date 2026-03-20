"""
Baseline model architectures for RNA 3D structure prediction.

Provides RNN-based and CNN-based models that map nucleotide index sequences
to per-residue (x, y, z) coordinates.
"""

import torch
import torch.nn as nn
from typing import Optional


class RNAEmbedding(nn.Module):
    """Shared nucleotide embedding + positional encoding."""

    def __init__(self, num_tokens: int = 5, embed_dim: int = 64, max_len: int = 2048):
        super().__init__()
        self.token_embed = nn.Embedding(num_tokens, embed_dim, padding_idx=0)
        self.pos_embed = nn.Embedding(max_len, embed_dim)

    def forward(self, seq_indices: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        seq_indices : (B, L) long tensor of nucleotide indices.

        Returns
        -------
        (B, L, embed_dim) float tensor.
        """
        B, L = seq_indices.shape
        positions = torch.arange(L, device=seq_indices.device).unsqueeze(0).expand(B, L)
        return self.token_embed(seq_indices) + self.pos_embed(positions)


class RNNModel(nn.Module):
    """Bidirectional GRU encoder → linear head for 3D coordinate prediction."""

    def __init__(
        self,
        num_tokens: int = 5,
        embed_dim: int = 64,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.1,
        output_dim: int = 3,
    ):
        super().__init__()
        self.embedding = RNAEmbedding(num_tokens, embed_dim)
        self.rnn = nn.GRU(
            embed_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(
        self, seq_indices: torch.Tensor, mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Parameters
        ----------
        seq_indices : (B, L) long tensor.
        mask : (B, L) bool tensor — True for valid positions.

        Returns
        -------
        (B, L, 3) predicted coordinates.
        """
        x = self.embedding(seq_indices)
        x, _ = self.rnn(x)
        return self.head(x)


class CNNModel(nn.Module):
    """1-D dilated convolution stack for 3D coordinate prediction."""

    def __init__(
        self,
        num_tokens: int = 5,
        embed_dim: int = 64,
        hidden_dim: int = 128,
        num_layers: int = 6,
        kernel_size: int = 5,
        dropout: float = 0.1,
        output_dim: int = 3,
    ):
        super().__init__()
        self.embedding = RNAEmbedding(num_tokens, embed_dim)

        layers = []
        in_channels = embed_dim
        for i in range(num_layers):
            dilation = 2 ** (i % 4)
            padding = (kernel_size - 1) * dilation // 2
            layers.extend([
                nn.Conv1d(in_channels, hidden_dim, kernel_size, padding=padding, dilation=dilation),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
            ])
            in_channels = hidden_dim
        self.conv_stack = nn.Sequential(*layers)
        self.head = nn.Linear(hidden_dim, output_dim)

    def forward(
        self, seq_indices: torch.Tensor, mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        x = self.embedding(seq_indices)  # (B, L, E)
        x = x.transpose(1, 2)  # (B, E, L) for Conv1d
        x = self.conv_stack(x)  # (B, H, L)
        x = x.transpose(1, 2)  # (B, L, H)
        return self.head(x)


MODEL_REGISTRY = {
    "rnn": RNNModel,
    "cnn": CNNModel,
}


def _get_full_registry():
    """Lazily import and merge GNN/Transformer models to avoid circular imports."""
    registry = dict(MODEL_REGISTRY)
    try:
        from inferencer.gnn_model import RNAGraphModel
        registry["gnn"] = RNAGraphModel
    except ImportError:
        pass
    try:
        from inferencer.transformer_model import RNATransformerModel
        registry["transformer"] = RNATransformerModel
    except ImportError:
        pass
    return registry


def create_model(model_type: str = "rnn", **kwargs) -> nn.Module:
    """Factory function to instantiate a model by name.

    Parameters
    ----------
    model_type : one of ``"rnn"``, ``"cnn"``, ``"gnn"``, or ``"transformer"``.
    **kwargs : forwarded to the model constructor.
    """
    registry = _get_full_registry()
    if model_type not in registry:
        raise ValueError(f"Unknown model_type={model_type!r}. Choose from {list(registry)}")
    return registry[model_type](**kwargs)
