"""
Short RNA specialization for structure prediction.

Provides motif-based prediction and secondary structure-guided coordinate
generation for short RNAs (<50nt) where template matching is unreliable
and TM-score normalization is harshest.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


# ======================================================================
# Minimal secondary structure prediction (Nussinov algorithm)
# ======================================================================

# Watson-Crick and wobble base pairs
_VALID_PAIRS = {
    ("A", "U"), ("U", "A"),
    ("G", "C"), ("C", "G"),
    ("G", "U"), ("U", "G"),
}

MIN_LOOP_SIZE = 3


def nussinov_fold(sequence: str) -> str:
    """Predict RNA secondary structure using the Nussinov algorithm.

    Returns dot-bracket notation string.

    Parameters
    ----------
    sequence : RNA sequence string (ACGU).

    Returns
    -------
    Dot-bracket string (e.g., "(((...)))").
    """
    seq = sequence.upper()
    n = len(seq)
    if n < 2 * MIN_LOOP_SIZE + 2:
        return "." * n

    # Fill DP table
    dp = np.zeros((n, n), dtype=np.int32)
    for span in range(MIN_LOOP_SIZE + 1, n):
        for i in range(n - span):
            j = i + span
            # Case 1: j unpaired
            dp[i, j] = dp[i, j - 1]
            # Case 2: j pairs with some k
            for k in range(i, j - MIN_LOOP_SIZE):
                if (seq[k], seq[j]) in _VALID_PAIRS:
                    score = 1 + (dp[i, k - 1] if k > i else 0) + (dp[k + 1, j - 1] if k + 1 <= j - 1 else 0)
                    dp[i, j] = max(dp[i, j], score)

    # Traceback
    structure = ["."] * n
    _traceback(dp, seq, 0, n - 1, structure)
    return "".join(structure)


def _traceback(dp, seq, i, j, structure):
    """Recursive traceback for Nussinov DP."""
    if i >= j or j - i <= MIN_LOOP_SIZE:
        return

    if dp[i, j] == dp[i, j - 1]:
        _traceback(dp, seq, i, j - 1, structure)
    else:
        for k in range(i, j - MIN_LOOP_SIZE):
            if (seq[k], seq[j]) in _VALID_PAIRS:
                left = dp[i, k - 1] if k > i else 0
                inner = dp[k + 1, j - 1] if k + 1 <= j - 1 else 0
                if dp[i, j] == 1 + left + inner:
                    structure[k] = "("
                    structure[j] = ")"
                    if k > i:
                        _traceback(dp, seq, i, k - 1, structure)
                    if k + 1 <= j - 1:
                        _traceback(dp, seq, k + 1, j - 1, structure)
                    return


# ======================================================================
# Secondary structure to 3D coordinate generation
# ======================================================================

# RNA A-form geometry constants
RISE_PER_RESIDUE = 2.81    # Angstroms along helix axis
HELIX_RADIUS = 9.4         # Angstrom radius for A-form
TWIST_PER_RESIDUE = 0.5712  # radians (32.7 degrees)
BASE_PAIR_DISTANCE = 5.9   # Approximate C1'-C1' distance for a base pair


def ss_to_coords(
    sequence: str,
    ss_string: str,
) -> np.ndarray:
    """Convert secondary structure to approximate 3D coordinates.

    Uses RNA A-form helix geometry for stems and extended backbone for loops.
    Base-paired residues are placed at complementary positions across the helix.

    Parameters
    ----------
    sequence : RNA sequence string.
    ss_string : dot-bracket notation.

    Returns
    -------
    (L, 3) array of approximate C1' coordinates.
    """
    n = len(sequence)
    coords = np.zeros((n, 3), dtype=np.float64)

    # Parse base pairs from dot-bracket
    pairs = _parse_pairs(ss_string)

    # Assign coordinates along backbone with helix geometry for paired regions
    placed = set()
    pos = 0  # linear backbone position counter

    for i in range(n):
        if i in placed:
            continue

        if i in pairs:
            j = pairs[i]
            # Place stem: i and j are paired
            angle = pos * TWIST_PER_RESIDUE
            coords[i, 0] = HELIX_RADIUS * np.cos(angle)
            coords[i, 1] = HELIX_RADIUS * np.sin(angle)
            coords[i, 2] = pos * RISE_PER_RESIDUE

            # Place partner across the helix
            coords[j, 0] = HELIX_RADIUS * np.cos(angle + np.pi)
            coords[j, 1] = HELIX_RADIUS * np.sin(angle + np.pi)
            coords[j, 2] = pos * RISE_PER_RESIDUE

            placed.add(i)
            placed.add(j)
        else:
            # Unpaired: place along backbone
            angle = pos * TWIST_PER_RESIDUE
            coords[i, 0] = HELIX_RADIUS * np.cos(angle)
            coords[i, 1] = HELIX_RADIUS * np.sin(angle)
            coords[i, 2] = pos * RISE_PER_RESIDUE
            placed.add(i)

        pos += 1

    return coords


def _parse_pairs(ss_string: str) -> Dict[int, int]:
    """Parse dot-bracket notation into a dict of paired positions."""
    pairs = {}
    stack = []
    for i, c in enumerate(ss_string):
        if c == "(":
            stack.append(i)
        elif c == ")":
            if stack:
                j = stack.pop()
                pairs[j] = i
                pairs[i] = j
    return pairs


# ======================================================================
# Motif library for short RNAs
# ======================================================================

class ShortRNAMotifLibrary:
    """Library of known short RNA structural motifs from training data.

    Indexes short RNA structures by secondary structure pattern for
    fast lookup when predicting new short sequences.
    """

    def __init__(self):
        self.motifs: List[Dict] = []
        self._ss_index: Dict[str, List[int]] = {}

    def build_from_templates(
        self,
        sequences: List[str],
        coords_list: List[np.ndarray],
        max_length: int = 60,
    ):
        """Build motif library from training data templates.

        Parameters
        ----------
        sequences : list of RNA sequences.
        coords_list : list of (L, 3) coordinate arrays.
        max_length : only include sequences shorter than this.
        """
        for i, (seq, coords) in enumerate(zip(sequences, coords_list)):
            if len(seq) > max_length or len(seq) < 5:
                continue
            if coords is None or len(coords) != len(seq):
                continue
            # Check for valid coordinates (no NaN, no sentinel values)
            coords_arr = np.array(coords, dtype=np.float64)
            if np.any(np.isnan(coords_arr)) or np.any(np.abs(coords_arr) > 1e10):
                continue

            ss = nussinov_fold(seq)
            motif = {
                "index": len(self.motifs),
                "sequence": seq,
                "ss": ss,
                "coords": coords_arr,
                "length": len(seq),
            }
            self.motifs.append(motif)

            # Index by SS pattern (collapsed: count of paired vs unpaired)
            ss_key = _ss_signature(ss)
            if ss_key not in self._ss_index:
                self._ss_index[ss_key] = []
            self._ss_index[ss_key].append(motif["index"])

    def search(
        self,
        query_sequence: str,
        top_k: int = 5,
    ) -> List[Dict]:
        """Find matching motifs for a short query sequence.

        Uses secondary structure similarity + sequence similarity to rank.
        """
        query_ss = nussinov_fold(query_sequence)
        query_key = _ss_signature(query_ss)

        # Collect candidates from similar SS patterns
        candidate_indices = set()
        for key, indices in self._ss_index.items():
            if _ss_key_distance(query_key, key) <= 3:
                candidate_indices.update(indices)

        # Score candidates
        scored = []
        for idx in candidate_indices:
            motif = self.motifs[idx]
            ss_sim = _ss_similarity(query_ss, motif["ss"])
            seq_sim = _sequence_similarity(query_sequence, motif["sequence"])
            length_ratio = min(len(query_sequence), motif["length"]) / max(len(query_sequence), motif["length"])

            score = 0.4 * ss_sim + 0.4 * seq_sim + 0.2 * length_ratio
            scored.append((motif, score))

        scored.sort(key=lambda x: -x[1])
        return [{"motif": m, "score": s} for m, s in scored[:top_k]]


def _ss_signature(ss: str) -> str:
    """Compact signature of secondary structure for indexing."""
    n_paired = ss.count("(") + ss.count(")")
    n_unpaired = ss.count(".")
    n_stems = 0
    in_stem = False
    for c in ss:
        if c == "(" and not in_stem:
            n_stems += 1
            in_stem = True
        elif c != "(":
            in_stem = False
    return f"{len(ss)}_{n_stems}_{n_paired}"


def _ss_key_distance(key1: str, key2: str) -> int:
    """Simple distance between SS signatures."""
    parts1 = [int(x) for x in key1.split("_")]
    parts2 = [int(x) for x in key2.split("_")]
    if len(parts1) != len(parts2):
        return 100
    return sum(abs(a - b) for a, b in zip(parts1, parts2))


def _ss_similarity(ss1: str, ss2: str) -> float:
    """Similarity between two secondary structure strings."""
    n = min(len(ss1), len(ss2))
    if n == 0:
        return 0.0
    matches = sum(1 for a, b in zip(ss1[:n], ss2[:n]) if a == b)
    return matches / max(len(ss1), len(ss2))


def _sequence_similarity(seq1: str, seq2: str) -> float:
    """Simple sequence similarity (fraction of matching positions)."""
    n = min(len(seq1), len(seq2))
    if n == 0:
        return 0.0
    matches = sum(1 for a, b in zip(seq1.upper()[:n], seq2.upper()[:n]) if a == b)
    return matches / max(len(seq1), len(seq2))


def predict_short_rna(
    sequence: str,
    motif_library: Optional[ShortRNAMotifLibrary] = None,
    use_ss_guided: bool = True,
) -> np.ndarray:
    """Specialized prediction for short RNA sequences.

    Tries motif library first, falls back to SS-guided coordinate generation.

    Parameters
    ----------
    sequence : RNA sequence (<50nt).
    motif_library : optional ShortRNAMotifLibrary for motif matching.
    use_ss_guided : if True, use secondary structure to guide coords.

    Returns
    -------
    (L, 3) predicted coordinates.
    """
    # Try motif library first
    if motif_library is not None:
        matches = motif_library.search(sequence, top_k=3)
        if matches and matches[0]["score"] > 0.5:
            best = matches[0]["motif"]
            # Transfer coordinates via alignment-like mapping
            return _transfer_motif_coords(sequence, best["sequence"], best["coords"])

    # Fallback: SS-guided coordinate generation
    if use_ss_guided:
        ss = nussinov_fold(sequence)
        return ss_to_coords(sequence, ss)

    # Last resort: A-form helix
    from inferencer.template_model import generate_helix_coords
    return generate_helix_coords(len(sequence))


def _transfer_motif_coords(
    query: str,
    motif_seq: str,
    motif_coords: np.ndarray,
) -> np.ndarray:
    """Transfer coordinates from a motif to the query sequence."""
    q_len = len(query)
    m_len = len(motif_seq)

    if q_len == m_len:
        return motif_coords.copy()

    # Simple positional mapping for length-mismatched sequences
    coords = np.zeros((q_len, 3), dtype=np.float64)
    for i in range(q_len):
        # Map query position to motif position (proportional)
        m_pos = i * (m_len - 1) / max(q_len - 1, 1)
        m_idx = int(m_pos)
        frac = m_pos - m_idx
        if m_idx >= m_len - 1:
            coords[i] = motif_coords[-1]
        else:
            coords[i] = (1 - frac) * motif_coords[m_idx] + frac * motif_coords[m_idx + 1]

    return coords
