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


def _tm_d0(length: int) -> float:
    """TM-score d0 normalization factor for a given sequence length."""
    if length <= 21:
        return 0.5
    return 1.24 * ((length - 15) ** (1.0 / 3.0)) - 1.8


def tm_aware_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    mask: Optional[torch.Tensor] = None,
    lengths: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """TM-score-aware loss that weights residue errors by d0 normalization.

    Approximates 1 - TM-score as a differentiable loss. Each residue's squared
    distance is weighted by 1/(1 + d_i^2/d0^2), making the loss focus on
    residues that are close to correct (where TM-score gains are largest).

    Parameters
    ----------
    pred : (B, L, 3) predicted coordinates.
    target : (B, L, 3) ground-truth coordinates.
    mask : (B, L) bool tensor — True for valid residues.
    lengths : (B,) actual sequence lengths (used for d0 computation).

    Returns
    -------
    Scalar tensor: mean (1 - approx_TM) across the batch.
    """
    B, L, _ = pred.shape
    dist_sq = ((pred - target) ** 2).sum(dim=-1)  # (B, L)

    if lengths is not None:
        d0 = torch.tensor(
            [_tm_d0(int(l.item())) for l in lengths],
            dtype=pred.dtype, device=pred.device,
        ).unsqueeze(1)  # (B, 1)
    else:
        d0 = torch.tensor(
            _tm_d0(L), dtype=pred.dtype, device=pred.device,
        )

    d0_sq = d0 * d0
    tm_per_residue = 1.0 / (1.0 + dist_sq / d0_sq)  # (B, L)

    if mask is not None:
        tm_per_residue = tm_per_residue * mask.float()
        n_valid = mask.float().sum(dim=-1).clamp(min=1.0)  # (B,)
    else:
        n_valid = torch.tensor(L, dtype=pred.dtype, device=pred.device)

    tm_score_approx = tm_per_residue.sum(dim=-1) / n_valid  # (B,)
    loss = 1.0 - tm_score_approx  # (B,)
    return loss.mean()


def length_weighted_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    mask: Optional[torch.Tensor] = None,
    lengths: Optional[torch.Tensor] = None,
    base_loss: str = "rmsd",
    short_weight: float = 3.0,
    medium_weight: float = 1.5,
    long_weight: float = 1.0,
    short_threshold: int = 50,
    long_threshold: int = 200,
) -> torch.Tensor:
    """Loss that upweights short sequences to counteract length bias.

    Computes per-sample loss using the base loss function, then applies
    length-dependent weights before averaging across the batch.

    Parameters
    ----------
    pred : (B, L, 3) predicted coordinates.
    target : (B, L, 3) ground-truth coordinates.
    mask : (B, L) bool tensor.
    lengths : (B,) actual sequence lengths.
    base_loss : underlying loss function name ("rmsd" or "mse").
    short_weight : multiplier for sequences < short_threshold.
    medium_weight : multiplier for sequences between thresholds.
    long_weight : multiplier for sequences > long_threshold.
    short_threshold : length cutoff for "short" bin.
    long_threshold : length cutoff for "long" bin.

    Returns
    -------
    Scalar weighted loss.
    """
    B = pred.shape[0]

    # Compute per-sample loss
    per_sample_losses = torch.zeros(B, dtype=pred.dtype, device=pred.device)
    for i in range(B):
        L_i = int(lengths[i].item()) if lengths is not None else pred.shape[1]
        p_i = pred[i:i+1, :L_i]
        t_i = target[i:i+1, :L_i]
        m_i = mask[i:i+1, :L_i] if mask is not None else None

        if base_loss == "rmsd":
            per_sample_losses[i] = rmsd_loss(p_i, t_i, m_i)
        else:
            per_sample_losses[i] = masked_mse_loss(p_i, t_i, m_i)

    # Apply length-dependent weights
    if lengths is not None:
        weights = torch.ones(B, dtype=pred.dtype, device=pred.device)
        for i in range(B):
            L_i = int(lengths[i].item())
            if L_i < short_threshold:
                weights[i] = short_weight
            elif L_i < long_threshold:
                weights[i] = medium_weight
            else:
                weights[i] = long_weight
        weighted = per_sample_losses * weights
        return weighted.sum() / weights.sum()
    else:
        return per_sample_losses.mean()


LOSS_REGISTRY = {
    "rmsd": rmsd_loss,
    "mse": masked_mse_loss,
    "tm_aware": tm_aware_loss,
    "length_weighted": length_weighted_loss,
}


def get_loss_fn(name: str = "rmsd"):
    """Retrieve a loss function by name."""
    if name not in LOSS_REGISTRY:
        raise ValueError(f"Unknown loss {name!r}. Choose from {list(LOSS_REGISTRY)}")
    return LOSS_REGISTRY[name]
