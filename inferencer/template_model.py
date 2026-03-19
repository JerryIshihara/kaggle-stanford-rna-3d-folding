"""
Template-based RNA 3D structure prediction.

Predicts coordinates by aligning query sequences to known PDB structures
and transferring coordinates from the best-matching templates.
Includes geometric helix fallback for sequences with no template hits.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple

from data_processor.template_db import (
    PDBRNADatabase,
    needleman_wunsch,
    sequence_identity,
)


# ======================================================================
# Geometric fallback — A-form RNA helix
# ======================================================================

def generate_helix_coords(length: int) -> np.ndarray:
    """Generate idealized A-form RNA helix backbone coordinates.

    Produces C3' atom positions for a single-stranded RNA in an
    approximate A-form helical geometry.

    Returns (length, 3) array.
    """
    rise_per_residue = 2.81  # Angstroms along helix axis
    radius = 9.4             # Angstrom radius for A-form
    twist_per_residue = np.radians(32.7)  # A-form twist

    coords = np.zeros((length, 3), dtype=np.float64)
    for i in range(length):
        angle = i * twist_per_residue
        coords[i, 0] = radius * np.cos(angle)
        coords[i, 1] = radius * np.sin(angle)
        coords[i, 2] = i * rise_per_residue
    return coords


# ======================================================================
# Coordinate transfer from template to query
# ======================================================================

def transfer_coordinates(
    query_sequence: str,
    template_sequence: str,
    template_coords: np.ndarray,
    alignment_map: Dict[int, int],
) -> np.ndarray:
    """Transfer 3D coordinates from a template to the query via alignment.

    Aligned positions copy template coordinates directly.
    Gapped positions are interpolated from neighbors.

    Returns (len(query_sequence), 3) array.
    """
    query_len = len(query_sequence)
    result = np.full((query_len, 3), np.nan, dtype=np.float64)

    for q_pos, t_pos in alignment_map.items():
        if q_pos < query_len and t_pos < len(template_coords):
            result[q_pos] = template_coords[t_pos]

    # Interpolate gaps from nearest mapped neighbors
    mapped_positions = sorted(alignment_map.keys())
    if not mapped_positions:
        return generate_helix_coords(query_len)

    for i in range(query_len):
        if not np.isnan(result[i, 0]):
            continue

        # Find nearest mapped neighbors
        left = max((p for p in mapped_positions if p < i), default=None)
        right = min((p for p in mapped_positions if p > i), default=None)

        if left is not None and right is not None:
            frac = (i - left) / (right - left)
            result[i] = result[left] * (1 - frac) + result[right] * frac
        elif left is not None:
            direction = _estimate_direction(result, left, mapped_positions)
            result[i] = result[left] + direction * (i - left)
        elif right is not None:
            direction = _estimate_direction(result, right, mapped_positions)
            result[i] = result[right] - direction * (right - i)
        else:
            result[i] = [0.0, 0.0, 0.0]

    return result


def _estimate_direction(
    coords: np.ndarray, anchor: int, mapped: List[int]
) -> np.ndarray:
    """Estimate local backbone direction near a mapped position."""
    neighbors = [p for p in mapped if p != anchor and not np.isnan(coords[p, 0])]
    if not neighbors:
        return np.array([0.0, 0.0, 2.81])  # Default rise direction

    closest = min(neighbors, key=lambda p: abs(p - anchor))
    diff = coords[anchor] - coords[closest]
    dist = np.linalg.norm(diff)
    if dist < 1e-6:
        return np.array([0.0, 0.0, 2.81])
    return diff / max(abs(anchor - closest), 1)


# ======================================================================
# Superposition (Kabsch algorithm)
# ======================================================================

def kabsch_rmsd(P: np.ndarray, Q: np.ndarray) -> Tuple[float, np.ndarray, np.ndarray]:
    """Compute optimal RMSD between two coordinate sets using the Kabsch algorithm.

    Parameters
    ----------
    P, Q : (N, 3) arrays of corresponding points.

    Returns
    -------
    rmsd : float
    R : (3, 3) rotation matrix
    t : (3,) translation vector  (apply as Q_aligned = (Q - centroid_Q) @ R + centroid_P)
    """
    assert P.shape == Q.shape
    centroid_P = P.mean(axis=0)
    centroid_Q = Q.mean(axis=0)
    p = P - centroid_P
    q = Q - centroid_Q

    H = q.T @ p
    U, S, Vt = np.linalg.svd(H)

    d = np.linalg.det(Vt.T @ U.T)
    sign_matrix = np.diag([1.0, 1.0, np.sign(d)])
    R = Vt.T @ sign_matrix @ U.T

    diff = p - q @ R
    rmsd_val = float(np.sqrt((diff ** 2).sum() / len(P)))

    return rmsd_val, R, centroid_P - centroid_Q @ R


# ======================================================================
# Template Model
# ======================================================================

class TemplateModel:
    """Predict RNA 3D structures using template-based coordinate transfer.

    Parameters
    ----------
    database : PDBRNADatabase instance (must be pre-built).
    top_k : number of templates to retrieve per query.
    min_identity : minimum sequence identity threshold for template hits.
    """

    def __init__(
        self,
        database: PDBRNADatabase,
        top_k: int = 5,
        min_identity: float = 0.2,
    ):
        self.database = database
        self.top_k = top_k
        self.min_identity = min_identity

    def predict(self, sequence: str) -> Dict:
        """Predict 3D coordinates for a single RNA sequence.

        Returns a dict with:
        - coords: (L, 3) numpy array
        - method: "template" or "helix_fallback"
        - templates_used: list of template info dicts
        - confidence: float 0-1
        """
        templates = self.database.search_templates(
            sequence, top_k=self.top_k, min_identity=self.min_identity
        )

        if not templates:
            return {
                "coords": generate_helix_coords(len(sequence)),
                "method": "helix_fallback",
                "templates_used": [],
                "confidence": 0.1,
            }

        predictions = []
        weights = []

        for tpl in templates:
            tpl_coords = np.array(tpl["coords"], dtype=np.float64)
            alignment = needleman_wunsch(sequence.upper(), tpl["template_sequence"])
            transferred = transfer_coordinates(
                sequence.upper(),
                tpl["template_sequence"],
                tpl_coords,
                alignment["alignment_map_a_to_b"],
            )
            predictions.append(transferred)
            weights.append(tpl["identity"])

        coords = self._weighted_ensemble(predictions, weights)

        return {
            "coords": coords,
            "method": "template",
            "templates_used": [
                {
                    "pdb_id": t["pdb_id"],
                    "chain_id": t["chain_id"],
                    "identity": t["identity"],
                }
                for t in templates
            ],
            "confidence": float(max(weights)),
        }

    def _weighted_ensemble(
        self,
        predictions: List[np.ndarray],
        weights: List[float],
    ) -> np.ndarray:
        """Combine multiple template predictions via identity-weighted average."""
        w = np.array(weights, dtype=np.float64)
        w = w / w.sum()

        result = np.zeros_like(predictions[0])
        for pred, weight in zip(predictions, w):
            result += pred * weight
        return result

    def predict_batch(
        self,
        sequences: List[str],
        ids: Optional[List[str]] = None,
    ) -> Dict[str, Dict]:
        """Predict coordinates for a batch of sequences.

        Returns a dict mapping sample ID to prediction result.
        """
        if ids is None:
            ids = [str(i) for i in range(len(sequences))]

        results = {}
        for sid, seq in zip(ids, sequences):
            results[sid] = self.predict(seq)
        return results


class TemplateEnsemble:
    """Combine predictions from multiple TemplateModel instances or configurations."""

    def __init__(self, models: List[TemplateModel]):
        self.models = models

    def predict(self, sequence: str) -> Dict:
        """Ensemble prediction: average coordinates from all models."""
        all_preds = [model.predict(sequence) for model in self.models]

        coords_list = [p["coords"] for p in all_preds]
        confidences = [p["confidence"] for p in all_preds]

        weights = np.array(confidences)
        if weights.sum() < 1e-8:
            weights = np.ones(len(weights))
        weights = weights / weights.sum()

        ensemble_coords = np.zeros_like(coords_list[0])
        for coords, w in zip(coords_list, weights):
            ensemble_coords += coords * w

        return {
            "coords": ensemble_coords,
            "method": "template_ensemble",
            "templates_used": [
                t for p in all_preds for t in p.get("templates_used", [])
            ],
            "confidence": float(max(confidences)),
            "num_models": len(self.models),
        }
