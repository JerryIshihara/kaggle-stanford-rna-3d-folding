"""
Evaluation metrics for RNA 3D structure prediction.

Primary metric: RMSD (Root Mean Square Deviation) — lower is better.
"""

import numpy as np
from typing import Dict, List, Optional


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
