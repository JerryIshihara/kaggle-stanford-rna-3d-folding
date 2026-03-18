"""
Cross-validation split generation for RNA 3D structure prediction.

Provides strategies that prevent data leakage (e.g. GroupKFold on RNA family).
"""

import numpy as np
from typing import List, Tuple, Optional
from sklearn.model_selection import KFold, GroupKFold, StratifiedKFold


def simple_kfold(
    n_samples: int,
    n_splits: int = 5,
    shuffle: bool = True,
    random_state: int = 42,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Basic K-Fold splitting.

    Returns a list of ``(train_indices, val_indices)`` tuples.
    """
    kf = KFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
    indices = np.arange(n_samples)
    return [(train_idx, val_idx) for train_idx, val_idx in kf.split(indices)]


def group_kfold(
    n_samples: int,
    groups: np.ndarray,
    n_splits: int = 5,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Group K-Fold splitting to prevent leakage across related samples.

    Parameters
    ----------
    n_samples : total number of samples.
    groups : (n_samples,) array of group labels (e.g. RNA family IDs).
        Samples sharing a group never appear in both train and val.
    n_splits : number of folds.
    """
    gkf = GroupKFold(n_splits=n_splits)
    X = np.arange(n_samples)
    return [(train_idx, val_idx) for train_idx, val_idx in gkf.split(X, groups=groups)]


def length_stratified_kfold(
    lengths: np.ndarray,
    n_splits: int = 5,
    n_bins: int = 10,
    random_state: int = 42,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Stratified K-Fold where strata are defined by binned sequence lengths.

    Ensures each fold has a similar distribution of short/long sequences.
    """
    bins = np.digitize(lengths, np.linspace(lengths.min(), lengths.max(), n_bins))
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    X = np.arange(len(lengths))
    return [(train_idx, val_idx) for train_idx, val_idx in skf.split(X, bins)]


SPLIT_REGISTRY = {
    "kfold": simple_kfold,
    "group_kfold": group_kfold,
    "length_stratified": length_stratified_kfold,
}


def get_splitter(name: str = "kfold"):
    """Retrieve a split function by name."""
    if name not in SPLIT_REGISTRY:
        raise ValueError(f"Unknown splitter {name!r}. Choose from {list(SPLIT_REGISTRY)}")
    return SPLIT_REGISTRY[name]
