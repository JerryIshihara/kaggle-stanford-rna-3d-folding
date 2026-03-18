"""
Loss functions for RNA 3D structure prediction.

The competition metric is RMSD (Root Mean Square Deviation) between predicted
and true atomic coordinates. This module provides differentiable loss variants
aligned with that metric.
"""

import torch
import torch.nn as nn
from typing import Optional


def rmsd_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    mask: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """Differentiable per-sample RMSD loss averaged over the batch.

    Parameters
    ----------
    pred : (B, L, 3) predicted coordinates.
    target : (B, L, 3) ground-truth coordinates.
    mask : (B, L) bool tensor — True for valid residues.

    Returns
    -------
    Scalar tensor: mean RMSD across the batch.
    """
    sq_diff = (pred - target) ** 2  # (B, L, 3)
    per_residue = sq_diff.sum(dim=-1)  # (B, L)

    if mask is not None:
        per_residue = per_residue * mask.float()
        n_valid = mask.float().sum(dim=-1).clamp(min=1.0)  # (B,)
    else:
        n_valid = torch.tensor(pred.shape[1], dtype=pred.dtype, device=pred.device)

    msd = per_residue.sum(dim=-1) / n_valid  # (B,)
    rmsd = torch.sqrt(msd + 1e-8)  # (B,)
    return rmsd.mean()


def masked_mse_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    mask: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """MSE loss respecting the padding mask.

    Parameters
    ----------
    pred : (B, L, 3) predicted coordinates.
    target : (B, L, 3) ground-truth coordinates.
    mask : (B, L) bool tensor.

    Returns
    -------
    Scalar mean squared error over valid positions.
    """
    sq_diff = (pred - target) ** 2  # (B, L, 3)

    if mask is not None:
        sq_diff = sq_diff * mask.unsqueeze(-1).float()
        n_valid = mask.float().sum().clamp(min=1.0) * 3
    else:
        n_valid = torch.tensor(pred.numel(), dtype=pred.dtype, device=pred.device)

    return sq_diff.sum() / n_valid


LOSS_REGISTRY = {
    "rmsd": rmsd_loss,
    "mse": masked_mse_loss,
}


def get_loss_fn(name: str = "rmsd"):
    """Retrieve a loss function by name."""
    if name not in LOSS_REGISTRY:
        raise ValueError(f"Unknown loss {name!r}. Choose from {list(LOSS_REGISTRY)}")
    return LOSS_REGISTRY[name]
