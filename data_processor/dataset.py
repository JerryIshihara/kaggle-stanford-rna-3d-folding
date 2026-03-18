"""
PyTorch Dataset and collation utilities for RNA 3D structure prediction.
"""

import torch
import numpy as np
from torch.utils.data import Dataset
from typing import List, Dict, Optional, Tuple


NUC_TO_IDX = {"A": 0, "C": 1, "G": 2, "U": 3, "T": 3}
NUM_NUCLEOTIDES = 4


class RNAStructureDataset(Dataset):
    """Dataset that pairs RNA sequences with their 3D coordinate targets.

    Parameters
    ----------
    sequences : list[str]
        RNA nucleotide strings (e.g. ``["ACGU...", ...]``).
    coordinates : list[np.ndarray]
        Per-residue 3D coordinates, each shaped ``(seq_len, 3)``.
    ids : list[str] or None
        Optional identifiers for each sample.
    max_len : int or None
        If set, sequences longer than this are truncated.
    """

    def __init__(
        self,
        sequences: List[str],
        coordinates: List[np.ndarray],
        ids: Optional[List[str]] = None,
        max_len: Optional[int] = None,
    ):
        assert len(sequences) == len(coordinates)
        self.sequences = sequences
        self.coordinates = coordinates
        self.ids = ids or [str(i) for i in range(len(sequences))]
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        seq = self.sequences[idx]
        coords = self.coordinates[idx]

        if self.max_len is not None:
            seq = seq[: self.max_len]
            coords = coords[: self.max_len]

        seq_indices = torch.tensor(
            [NUC_TO_IDX.get(c, 0) for c in seq.upper()], dtype=torch.long
        )
        coord_tensor = torch.tensor(coords, dtype=torch.float32)
        length = torch.tensor(len(seq), dtype=torch.long)

        return {
            "seq_indices": seq_indices,
            "coordinates": coord_tensor,
            "length": length,
            "id": self.ids[idx],
        }


class RNATestDataset(Dataset):
    """Dataset for test-time inference (no coordinate targets)."""

    def __init__(
        self,
        sequences: List[str],
        ids: Optional[List[str]] = None,
        max_len: Optional[int] = None,
    ):
        self.sequences = sequences
        self.ids = ids or [str(i) for i in range(len(sequences))]
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        seq = self.sequences[idx]
        if self.max_len is not None:
            seq = seq[: self.max_len]

        seq_indices = torch.tensor(
            [NUC_TO_IDX.get(c, 0) for c in seq.upper()], dtype=torch.long
        )
        length = torch.tensor(len(seq), dtype=torch.long)

        return {
            "seq_indices": seq_indices,
            "length": length,
            "id": self.ids[idx],
        }


def collate_rna(batch: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
    """Pad variable-length RNA samples into a single batch.

    Returns a dict with:
    - ``seq_indices``: (B, max_len) long tensor
    - ``coordinates``: (B, max_len, 3) float tensor  (zero-filled if missing)
    - ``lengths``: (B,) long tensor
    - ``mask``: (B, max_len) bool tensor — True for real positions
    - ``ids``: list[str]
    """
    lengths = torch.stack([b["length"] for b in batch])
    max_len = int(lengths.max().item())
    batch_size = len(batch)

    seq_indices = torch.zeros(batch_size, max_len, dtype=torch.long)
    has_coords = "coordinates" in batch[0]
    coordinates = torch.zeros(batch_size, max_len, 3, dtype=torch.float32)
    mask = torch.zeros(batch_size, max_len, dtype=torch.bool)
    ids = []

    for i, b in enumerate(batch):
        L = int(b["length"].item())
        seq_indices[i, :L] = b["seq_indices"]
        if has_coords:
            coordinates[i, :L] = b["coordinates"]
        mask[i, :L] = True
        ids.append(b["id"])

    result = {
        "seq_indices": seq_indices,
        "lengths": lengths,
        "mask": mask,
        "ids": ids,
    }
    if has_coords:
        result["coordinates"] = coordinates
    return result
