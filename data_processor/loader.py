"""
RNA data loading utilities for Stanford RNA 3D Folding 2 competition.

Handles loading of training/test CSVs, MSA files, and sample submissions.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from Bio import SeqIO


class RNADataLoader:
    """Loads and parses competition data from disk."""

    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)

    def load_train(self) -> pd.DataFrame:
        path = self.data_dir / "train.csv"
        if not path.exists():
            raise FileNotFoundError(f"Training data not found at {path}")
        return pd.read_csv(path)

    def load_test(self) -> pd.DataFrame:
        path = self.data_dir / "test.csv"
        if not path.exists():
            raise FileNotFoundError(f"Test data not found at {path}")
        return pd.read_csv(path)

    def load_sample_submission(self) -> pd.DataFrame:
        path = self.data_dir / "sample_submission.csv"
        if not path.exists():
            raise FileNotFoundError(f"Sample submission not found at {path}")
        return pd.read_csv(path)

    def load_msa(self, rna_id: str) -> List[Dict]:
        """Load a Multiple Sequence Alignment file for a given RNA ID."""
        msa_path = self.data_dir / "MSA" / f"{rna_id}.MSA.fasta"
        if not msa_path.exists():
            raise FileNotFoundError(f"MSA file not found: {msa_path}")

        sequences = []
        for record in SeqIO.parse(str(msa_path), "fasta"):
            sequences.append({
                "id": record.id,
                "sequence": str(record.seq),
                "description": record.description,
            })
        return sequences

    def list_msa_ids(self) -> List[str]:
        """List all available MSA RNA IDs."""
        msa_dir = self.data_dir / "MSA"
        if not msa_dir.exists():
            return []
        return sorted(f.stem.replace(".MSA", "") for f in msa_dir.glob("*.fasta"))

    def get_msa_stats(self, rna_id: str) -> Dict:
        """Compute basic statistics for an MSA file."""
        sequences = self.load_msa(rna_id)
        if not sequences:
            return {}
        lengths = [len(s["sequence"]) for s in sequences]
        return {
            "rna_id": rna_id,
            "num_sequences": len(sequences),
            "min_length": min(lengths),
            "max_length": max(lengths),
            "mean_length": float(np.mean(lengths)),
        }


def parse_coordinates(coord_string: str) -> np.ndarray:
    """Parse a space-separated coordinate string into an (N, 3) array.

    Expected format per residue: ``x y z`` values separated by spaces,
    with residues delimited by semicolons or stored row-per-residue.
    Adjust parsing logic once the actual competition format is confirmed.
    """
    values = list(map(float, coord_string.split()))
    return np.array(values).reshape(-1, 3)


def encode_sequence(sequence: str) -> np.ndarray:
    """One-hot encode an RNA sequence. Unknown characters map to all-zero."""
    mapping = {"A": 0, "C": 1, "G": 2, "U": 3, "T": 3}
    indices = np.array([mapping.get(c, -1) for c in sequence.upper()])
    one_hot = np.zeros((len(sequence), 4), dtype=np.float32)
    valid = indices >= 0
    one_hot[valid, indices[valid]] = 1.0
    return one_hot
