"""
Transformer model for RNA 3D structure prediction.

Implements a pre-norm Transformer encoder that maps nucleotide sequences to
per-residue 3D coordinates. Inspired by the architectures of RhoFold+,
trRosettaRNA, and RibonanzaNet, adapted for direct coordinate regression.

Key design choices:
    - Sinusoidal positional encoding (not learned) for length generalization
    - Pre-LayerNorm for more stable training
    - Bidirectional self-attention (no causal mask)
    - Optional pair bias in attention (AlphaFold-style)
    - Structure module with coordinate head

References:
    - RhoFold+ (Nature Methods 2024): RNA-FM + IPA module
    - trRosettaRNA (Nature Communications 2023): Transformer + geometry prediction
    - RibonanzaNet: Transformer+CNN for Kaggle RNA competition
    - Vaswani et al., "Attention is All You Need", NeurIPS 2017
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional


class SinusoidalPositionalEncoding(nn.Module):
    """Fixed sinusoidal positional encoding for length generalization."""

    def __init__(self, d_model: int, max_len: int = 4096, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float) * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (B, L, D) -> (B, L, D) with positional encoding added."""
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)


class PreNormTransformerLayer(nn.Module):
    """Pre-LayerNorm Transformer encoder layer with optional pair bias.

    Pre-norm places LayerNorm before (not after) the attention and FFN sublayers,
    yielding more stable training gradients — critical for deeper models.
    """

    def __init__(
        self,
        d_model: int,
        nhead: int,
        dim_feedforward: int = 512,
        dropout: float = 0.1,
        use_pair_bias: bool = False,
    ):
        super().__init__()
        self.nhead = nhead
        self.d_model = d_model
        self.head_dim = d_model // nhead
        self.use_pair_bias = use_pair_bias

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)

        if use_pair_bias:
            self.pair_bias_proj = nn.Linear(d_model, nhead)

        self.ffn = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim_feedforward, d_model),
            nn.Dropout(dropout),
        )

        self.attn_dropout = nn.Dropout(dropout)
        self.res_dropout = nn.Dropout(dropout)

    def _attention(
        self,
        x: torch.Tensor,
        key_padding_mask: Optional[torch.Tensor] = None,
        pair_repr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        B, L, D = x.shape

        q = self.q_proj(x).reshape(B, L, self.nhead, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).reshape(B, L, self.nhead, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).reshape(B, L, self.nhead, self.head_dim).transpose(1, 2)

        scale = self.head_dim ** -0.5
        attn = torch.matmul(q, k.transpose(-2, -1)) * scale

        if self.use_pair_bias and pair_repr is not None:
            bias = self.pair_bias_proj(pair_repr).permute(0, 3, 1, 2)
            attn = attn + bias

        if key_padding_mask is not None:
            attn_mask = ~key_padding_mask.unsqueeze(1).unsqueeze(2)
            attn = attn.masked_fill(attn_mask, float("-inf"))

        attn = F.softmax(attn, dim=-1)
        attn = self.attn_dropout(attn)

        out = torch.matmul(attn, v)
        out = out.transpose(1, 2).reshape(B, L, D)
        return self.out_proj(out)

    def forward(
        self,
        x: torch.Tensor,
        key_padding_mask: Optional[torch.Tensor] = None,
        pair_repr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        residual = x
        x_norm = self.norm1(x)
        x = residual + self.res_dropout(self._attention(x_norm, key_padding_mask, pair_repr))

        residual = x
        x = residual + self.ffn(self.norm2(x))

        return x


class PairRepresentation(nn.Module):
    """Lightweight pairwise representation module (AlphaFold-style).

    Constructs an L x L pair representation from single representations using
    outer product and relative positional encoding.
    """

    def __init__(self, d_model: int, d_pair: int = 64, max_len: int = 2048):
        super().__init__()
        self.left_proj = nn.Linear(d_model, d_pair)
        self.right_proj = nn.Linear(d_model, d_pair)
        self.rel_pos_embed = nn.Embedding(2 * max_len + 1, d_pair)
        self.max_len = max_len
        self.out_proj = nn.Linear(d_pair, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        x : (B, L, D) single representations

        Returns
        -------
        (B, L, L, D) pair representations
        """
        B, L, _ = x.shape

        left = self.left_proj(x)
        right = self.right_proj(x)
        pair = left.unsqueeze(2) + right.unsqueeze(1)

        pos = torch.arange(L, device=x.device)
        rel_pos = (pos.unsqueeze(0) - pos.unsqueeze(1)).clamp(-self.max_len, self.max_len)
        rel_pos = rel_pos + self.max_len
        pair = pair + self.rel_pos_embed(rel_pos).unsqueeze(0)

        return self.out_proj(pair)


class StructureModule(nn.Module):
    """Converts per-residue features to 3D coordinates.

    Uses a multi-layer MLP with residual connections and layer normalization.
    Inspired by the IPA (Invariant Point Attention) structure module in
    AlphaFold2 / RhoFold+, but simplified for direct coordinate regression.
    """

    def __init__(self, d_model: int, hidden_dim: int = 128, output_dim: int = 3):
        super().__init__()
        self.layers = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (B, L, D) -> (B, L, 3)"""
        return self.layers(x)


class RNATransformerModel(nn.Module):
    """RNA 3D structure prediction via Transformer encoder.

    Architecture:
        1. Token embedding + sinusoidal positional encoding
        2. Optional pair representation with attention bias
        3. Stack of pre-norm Transformer encoder layers
        4. Structure module for coordinate output

    Compatible with the Trainer interface (forward takes seq_indices and mask).
    """

    def __init__(
        self,
        num_tokens: int = 5,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 6,
        dim_feedforward: int = 512,
        dropout: float = 0.1,
        output_dim: int = 3,
        max_len: int = 2048,
        use_pair_bias: bool = True,
    ):
        super().__init__()
        self.d_model = d_model

        self.token_embed = nn.Embedding(num_tokens, d_model, padding_idx=0)
        self.pos_encoding = SinusoidalPositionalEncoding(d_model, max_len, dropout)

        self.input_norm = nn.LayerNorm(d_model)

        self.use_pair_bias = use_pair_bias
        if use_pair_bias:
            self.pair_repr = PairRepresentation(d_model, d_pair=64, max_len=max_len)

        self.encoder_layers = nn.ModuleList([
            PreNormTransformerLayer(
                d_model=d_model,
                nhead=nhead,
                dim_feedforward=dim_feedforward,
                dropout=dropout,
                use_pair_bias=use_pair_bias,
            )
            for _ in range(num_layers)
        ])

        self.final_norm = nn.LayerNorm(d_model)

        self.structure_module = StructureModule(
            d_model=d_model,
            hidden_dim=d_model,
            output_dim=output_dim,
        )

    def forward(
        self, seq_indices: torch.Tensor, mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Parameters
        ----------
        seq_indices : (B, L) long tensor of nucleotide indices
        mask : (B, L) bool tensor — True for valid positions

        Returns
        -------
        (B, L, 3) predicted coordinates
        """
        B, L = seq_indices.shape

        x = self.token_embed(seq_indices)
        x = self.pos_encoding(x)
        x = self.input_norm(x)

        pair_repr = None
        if self.use_pair_bias:
            pair_repr = self.pair_repr(x)

        for layer in self.encoder_layers:
            x = layer(x, key_padding_mask=mask, pair_repr=pair_repr)

        x = self.final_norm(x)

        coords = self.structure_module(x)

        return coords
