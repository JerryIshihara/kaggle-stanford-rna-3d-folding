"""
Evaluation metrics for RNA 3D structure prediction.

Primary metric: RMSD (Root Mean Square Deviation) — lower is better.
Competition metric: TM-score — higher is better (best-of-5, averaged).

TM-score reference: Zhang & Skolnick, "Scoring function for automated
assessment of protein structure template quality", Proteins 2004.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


def rmsd(pred: np.ndarray, target: np.ndarray) -> float:
    """Compute RMSD between two sets of 3D coordinates.

    Parameters
    ----------
    pred : (N, 3) predicted coordinates.
    target : (N, 3) ground-truth coordinates.

    Returns
    -------
    RMSD as a scalar float.
    """
    assert pred.shape == target.shape, f"Shape mismatch: {pred.shape} vs {target.shape}"
    sq_diff = (pred - target) ** 2
    return float(np.sqrt(sq_diff.sum(axis=-1).mean()))


def rmsd_per_sample(
    predictions: Dict[str, np.ndarray],
    targets: Dict[str, np.ndarray],
) -> Dict[str, float]:
    """Compute per-sample RMSD for a dict of predictions.

    Parameters
    ----------
    predictions : mapping from sample ID to (N, 3) predicted coordinates.
    targets : mapping from sample ID to (N, 3) ground-truth coordinates.

    Returns
    -------
    Dict mapping sample ID to its RMSD score.
    """
    scores = {}
    for sid in predictions:
        if sid not in targets:
            continue
        scores[sid] = rmsd(predictions[sid], targets[sid])
    return scores


def aggregate_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """Compute summary statistics over per-sample RMSD scores."""
    values = list(scores.values())
    if not values:
        return {"mean": float("nan"), "std": float("nan"), "median": float("nan"), "count": 0}
    arr = np.array(values)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "median": float(np.median(arr)),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "count": len(arr),
    }


def evaluate_fold(
    predictions: Dict[str, np.ndarray],
    targets: Dict[str, np.ndarray],
    fold_id: Optional[int] = None,
) -> Dict:
    """Full evaluation for a single CV fold.

    Returns per-sample scores and aggregate statistics.
    """
    per_sample = rmsd_per_sample(predictions, targets)
    agg = aggregate_scores(per_sample)
    return {
        "fold_id": fold_id,
        "per_sample": per_sample,
        "aggregate": agg,
    }


def tm_score_d0(length: int) -> float:
    """Compute the TM-score d0 normalization factor for a given sequence length.

    d0 = 1.24 * cbrt(L - 15) - 1.8   if L > 21
    d0 = 0.5                           otherwise
    """
    if length <= 21:
        return 0.5
    return 1.24 * ((length - 15) ** (1.0 / 3.0)) - 1.8


def tm_score(pred: np.ndarray, target: np.ndarray) -> float:
    """Compute TM-score between predicted and target 3D coordinates.

    Uses Kabsch superposition to optimally align structures before scoring.
    TM-score ranges from 0 to 1, higher is better.

    Parameters
    ----------
    pred : (N, 3) predicted coordinates.
    target : (N, 3) ground-truth coordinates.

    Returns
    -------
    TM-score as a scalar float.
    """
    assert pred.shape == target.shape, f"Shape mismatch: {pred.shape} vs {target.shape}"
    L = len(target)
    if L == 0:
        return 0.0

    d0 = tm_score_d0(L)
    d0_sq = d0 * d0

    aligned_pred = _kabsch_align(pred, target)

    dist_sq = ((aligned_pred - target) ** 2).sum(axis=-1)
    scores = 1.0 / (1.0 + dist_sq / d0_sq)

    return float(scores.sum() / L)


def _kabsch_align(pred: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Optimally superpose pred onto target using Kabsch algorithm.

    Returns the aligned pred coordinates.
    """
    pred_center = pred.mean(axis=0)
    target_center = target.mean(axis=0)

    p = pred - pred_center
    q = target - target_center

    H = p.T @ q
    U, S, Vt = np.linalg.svd(H)

    d = np.linalg.det(Vt.T @ U.T)
    sign_matrix = np.diag([1.0, 1.0, np.sign(d)])
    R = Vt.T @ sign_matrix @ U.T

    aligned = p @ R + target_center
    return aligned


def tm_score_best_of_k(
    predictions: List[np.ndarray],
    target: np.ndarray,
) -> Tuple[float, int]:
    """Compute best-of-K TM-score (competition metric).

    Parameters
    ----------
    predictions : list of K (N, 3) predicted coordinate arrays.
    target : (N, 3) ground-truth coordinates.

    Returns
    -------
    (best_tm_score, best_index) tuple.
    """
    best_score = -1.0
    best_idx = 0
    for i, pred in enumerate(predictions):
        score = tm_score(pred, target)
        if score > best_score:
            best_score = score
            best_idx = i
    return best_score, best_idx


def tm_score_per_sample(
    predictions: Dict[str, np.ndarray],
    targets: Dict[str, np.ndarray],
) -> Dict[str, float]:
    """Compute per-sample TM-score for a dict of predictions."""
    scores = {}
    for sid in predictions:
        if sid not in targets:
            continue
        scores[sid] = tm_score(predictions[sid], targets[sid])
    return scores


def evaluate_cv(fold_results: List[Dict]) -> Dict:
    """Aggregate evaluation across all CV folds.

    Parameters
    ----------
    fold_results : list of dicts returned by ``evaluate_fold``.

    Returns
    -------
    Dict with per-fold means, overall mean, and overall std.
    """
    fold_means = [r["aggregate"]["mean"] for r in fold_results]
    arr = np.array(fold_means)
    return {
        "fold_means": fold_means,
        "cv_mean": float(arr.mean()),
        "cv_std": float(arr.std()),
        "num_folds": len(fold_results),
    }
