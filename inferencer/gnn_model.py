"""
Graph Neural Network for RNA 3D structure prediction.

Implements an E(n)-equivariant graph neural network (EGNN-style) that operates
on RNA graphs with backbone, skip-connection, and k-nearest-neighbor edges.
Each message-passing layer updates both node features and 3D coordinates,
maintaining equivariance to rotations and translations.

References:
    - Satorras et al., "E(n) Equivariant Graph Neural Networks", ICML 2021
    - Jing et al., "Equivariant Graph Neural Networks for 3D Macromolecular Structure", ICLR 2021
    - EquiRNA, ICLR 2025 (size-insensitive K-NN for RNA)
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


def build_rna_graph(
    batch_size: int,
    seq_len: int,
    mask: torch.Tensor,
    k_neighbors: int = 10,
    skip_connections: Tuple[int, ...] = (2, 4, 8, 16),
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Construct RNA graph edges for a padded batch.

    Produces three types of edges per sample:
      1. Backbone: (i, i+1) bidirectional
      2. Skip-connections: (i, i+k) for each k in *skip_connections*
      3. K-nearest neighbors based on sequence distance heuristic

    Returns
    -------
    edge_index : (2, E) long tensor with global node indices
    edge_attr  : (E, 3) float tensor — [edge_type_onehot(3)]
    batch_idx  : (E,) long tensor mapping each edge to its sample index
    """
    device = mask.device
    all_src, all_dst, all_types, all_batch = [], [], [], []

    for b in range(batch_size):
        length = int(mask[b].sum().item())
        if length < 2:
            continue
        offset = b * seq_len

        src_list, dst_list, type_list = [], [], []

        for i in range(length - 1):
            src_list.extend([offset + i, offset + i + 1])
            dst_list.extend([offset + i + 1, offset + i])
            type_list.extend([0, 0])

        for k in skip_connections:
            for i in range(length - k):
                src_list.extend([offset + i, offset + i + k])
                dst_list.extend([offset + i + k, offset + i])
                type_list.extend([1, 1])

        effective_k = min(k_neighbors, length - 1)
        if effective_k > 0:
            for i in range(length):
                distances = []
                for j in range(length):
                    if i != j:
                        distances.append((abs(i - j) + 0.1 * (hash((i, j)) % 10), j))
                distances.sort()
                for _, j in distances[:effective_k]:
                    src_list.append(offset + i)
                    dst_list.append(offset + j)
                    type_list.append(2)

        all_src.extend(src_list)
        all_dst.extend(dst_list)
        all_types.extend(type_list)
        all_batch.extend([b] * len(src_list))

    if not all_src:
        edge_index = torch.zeros(2, 0, dtype=torch.long, device=device)
        edge_attr = torch.zeros(0, 3, dtype=torch.float, device=device)
        batch_idx = torch.zeros(0, dtype=torch.long, device=device)
        return edge_index, edge_attr, batch_idx

    edge_index = torch.tensor([all_src, all_dst], dtype=torch.long, device=device)

    edge_type = torch.tensor(all_types, dtype=torch.long, device=device)
    edge_attr = F.one_hot(edge_type, num_classes=3).float()

    batch_idx = torch.tensor(all_batch, dtype=torch.long, device=device)

    return edge_index, edge_attr, batch_idx


class EGNNLayer(nn.Module):
    """Single E(n)-equivariant graph neural network layer.

    Updates node features and coordinates simultaneously while maintaining
    equivariance to rotations and translations.
    """

    def __init__(
        self,
        node_dim: int,
        edge_dim: int = 3,
        coord_dim: int = 3,
        hidden_dim: int = 128,
        act: str = "silu",
    ):
        super().__init__()
        act_fn = nn.SiLU() if act == "silu" else nn.ReLU()

        self.message_mlp = nn.Sequential(
            nn.Linear(2 * node_dim + edge_dim + 1, hidden_dim),
            act_fn,
            nn.Linear(hidden_dim, hidden_dim),
            act_fn,
        )

        self.coord_mlp = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            act_fn,
            nn.Linear(hidden_dim, 1),
        )

        self.node_mlp = nn.Sequential(
            nn.Linear(node_dim + hidden_dim, hidden_dim),
            act_fn,
            nn.Linear(hidden_dim, node_dim),
        )

        self.node_norm = nn.LayerNorm(node_dim)

    def forward(
        self,
        h: torch.Tensor,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Parameters
        ----------
        h : (N, node_dim) node features (flattened across batch)
        x : (N, 3) node coordinates
        edge_index : (2, E) source/target indices
        edge_attr : (E, edge_dim) edge features

        Returns
        -------
        h_out : (N, node_dim) updated node features
        x_out : (N, 3) updated coordinates
        """
        src, dst = edge_index[0], edge_index[1]
        N = h.size(0)

        rel_pos = x[src] - x[dst]
        dist_sq = (rel_pos ** 2).sum(dim=-1, keepdim=True)

        msg_input = torch.cat([h[src], h[dst], edge_attr, dist_sq], dim=-1)
        msg = self.message_mlp(msg_input)

        coord_weight = self.coord_mlp(msg)
        coord_shift = rel_pos * coord_weight

        agg_coord = torch.zeros_like(x)
        agg_coord.scatter_add_(0, dst.unsqueeze(-1).expand(-1, 3), coord_shift)

        count = torch.zeros(N, 1, device=x.device)
        count.scatter_add_(0, dst.unsqueeze(-1), torch.ones(src.size(0), 1, device=x.device))
        count = count.clamp(min=1.0)
        x_out = x + agg_coord / count

        agg_msg = torch.zeros(N, msg.size(-1), device=h.device)
        agg_msg.scatter_add_(0, dst.unsqueeze(-1).expand(-1, msg.size(-1)), msg)

        h_out = self.node_mlp(torch.cat([h, agg_msg], dim=-1))
        h_out = self.node_norm(h + h_out)

        return h_out, x_out


class RNAGraphModel(nn.Module):
    """RNA 3D structure prediction via E(n)-equivariant graph neural network.

    Constructs an RNA graph from the sequence, runs EGNN message-passing layers,
    and outputs per-residue 3D coordinates. Compatible with the Trainer interface
    (forward takes seq_indices and optional mask).
    """

    def __init__(
        self,
        num_tokens: int = 5,
        embed_dim: int = 64,
        hidden_dim: int = 128,
        num_layers: int = 6,
        dropout: float = 0.1,
        output_dim: int = 3,
        k_neighbors: int = 10,
        max_len: int = 2048,
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.k_neighbors = k_neighbors

        self.token_embed = nn.Embedding(num_tokens, embed_dim, padding_idx=0)

        self.pos_freq = nn.Parameter(
            self._sinusoidal_encoding(max_len, embed_dim), requires_grad=False
        )

        self.input_proj = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.SiLU(),
            nn.Dropout(dropout),
        )

        self.coord_init = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, 3),
        )

        self.layers = nn.ModuleList([
            EGNNLayer(
                node_dim=hidden_dim,
                edge_dim=3,
                coord_dim=3,
                hidden_dim=hidden_dim,
            )
            for _ in range(num_layers)
        ])

        self.coord_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, output_dim),
        )

    @staticmethod
    def _sinusoidal_encoding(max_len: int, d_model: int) -> torch.Tensor:
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float) * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe

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
        device = seq_indices.device

        if mask is None:
            mask = torch.ones(B, L, dtype=torch.bool, device=device)

        tok = self.token_embed(seq_indices)
        pos = self.pos_freq[:L].unsqueeze(0).expand(B, -1, -1).to(device)
        h = self.input_proj(tok + pos)

        x_init = self.coord_init(h)

        h_flat = h.reshape(B * L, -1)
        x_flat = x_init.reshape(B * L, 3)

        edge_index, edge_attr, _ = build_rna_graph(
            B, L, mask, k_neighbors=self.k_neighbors
        )

        for layer in self.layers:
            h_flat, x_flat = layer(h_flat, x_flat, edge_index, edge_attr)

        h_out = h_flat.reshape(B, L, -1)
        x_egnn = x_flat.reshape(B, L, 3)

        coord_correction = self.coord_head(h_out)
        coords = x_egnn + coord_correction

        return coords
