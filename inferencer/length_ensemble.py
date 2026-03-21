"""
Length-aware ensemble for RNA 3D structure prediction.

Computes ensemble weights as smooth functions of sequence length, replacing
hardcoded length-bin cutoffs with sigmoid interpolation for more robust
predictions across the full length spectrum.
"""

import math
import numpy as np
from typing import Dict, List, Optional, Tuple


def _sigmoid(x: float) -> float:
    """Numerically stable sigmoid."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    ex = math.exp(x)
    return ex / (1.0 + ex)


class LengthAwareEnsemble:
    """Ensemble that adapts component weights based on sequence length.

    Weight curves are parameterized by sigmoid transitions:
    - Template weight increases with length (more reliable for long sequences)
    - Neural weights decrease with length (less training data for long sequences)

    Parameters
    ----------
    template_min : float
        Template weight floor (for very short sequences).
    template_max : float
        Template weight ceiling (for very long sequences).
    transition_center : float
        Length at which template/neural weights are equal.
    transition_steepness : float
        How quickly the transition happens (higher = sharper).
    resnet_fraction : float
        Fraction of neural weight allocated to ResNet (rest to Transformer).
    """

    def __init__(
        self,
        template_min: float = 0.15,
        template_max: float = 0.60,
        transition_center: float = 100.0,
        transition_steepness: float = 0.03,
        resnet_fraction: float = 0.5,
    ):
        self.template_min = template_min
        self.template_max = template_max
        self.transition_center = transition_center
        self.transition_steepness = transition_steepness
        self.resnet_fraction = resnet_fraction

    def get_ensemble_weights(self, length: int) -> Dict[str, float]:
        """Compute component weights for a given sequence length.

        Returns dict with keys: 'template', 'resnet', 'transformer'.
        All weights sum to 1.0.
        """
        t = _sigmoid(self.transition_steepness * (length - self.transition_center))
        template_w = self.template_min + (self.template_max - self.template_min) * t
        neural_w = 1.0 - template_w
        resnet_w = neural_w * self.resnet_fraction
        transformer_w = neural_w * (1.0 - self.resnet_fraction)

        return {
            "template": template_w,
            "resnet": resnet_w,
            "transformer": transformer_w,
        }

    def get_refinement_iterations(self, length: int) -> int:
        """Number of iterative refinement steps, adapted to sequence length.

        Short RNAs get more refinement (accuracy matters more, cost is low).
        Long RNAs get fewer (already good from templates, cost is high).
        """
        if length < 50:
            return 3
        elif length < 150:
            return 2
        elif length < 500:
            return 1
        else:
            return 1

    def get_diversity_strategy(self, length: int) -> Dict[str, any]:
        """Returns diversity generation strategy parameters per length bin.

        Short: more aggressive diversity (motif search + perturbations)
        Medium: balanced (multi-template + light perturbation)
        Long: template-focused (top-k templates only)
        """
        if length < 50:
            return {
                "num_templates": 3,
                "num_perturbations": 2,
                "perturbation_scale": 1.5,  # Angstroms
                "use_motif_search": True,
                "use_ss_guided": True,
            }
        elif length < 200:
            return {
                "num_templates": 4,
                "num_perturbations": 1,
                "perturbation_scale": 1.0,
                "use_motif_search": False,
                "use_ss_guided": False,
            }
        else:
            return {
                "num_templates": 5,
                "num_perturbations": 0,
                "perturbation_scale": 0.5,
                "use_motif_search": False,
                "use_ss_guided": False,
            }

    def ensemble_predict(
        self,
        predictions: Dict[str, np.ndarray],
        length: int,
    ) -> np.ndarray:
        """Weighted combination of multi-model predictions.

        Parameters
        ----------
        predictions : dict mapping component name to (L, 3) coordinate arrays.
            Expected keys: 'template', 'resnet', 'transformer' (any subset).
        length : actual sequence length.

        Returns
        -------
        (L, 3) weighted average of predictions.
        """
        weights = self.get_ensemble_weights(length)

        total_weight = 0.0
        result = None
        for component, coords in predictions.items():
            if component not in weights:
                continue
            w = weights[component]
            if result is None:
                result = np.zeros_like(coords, dtype=np.float64)
            result += w * coords.astype(np.float64)
            total_weight += w

        if result is None or total_weight == 0:
            # Fallback: return first available prediction
            return next(iter(predictions.values()))

        return (result / total_weight).astype(np.float32)


def generate_diverse_predictions(
    ensemble: LengthAwareEnsemble,
    template_coords_list: List[np.ndarray],
    neural_coords: Optional[np.ndarray],
    length: int,
    num_predictions: int = 5,
) -> List[np.ndarray]:
    """Generate diverse predictions using length-aware strategy.

    Parameters
    ----------
    ensemble : LengthAwareEnsemble instance.
    template_coords_list : list of (L, 3) arrays from different templates.
    neural_coords : (L, 3) array from neural model, or None.
    length : actual sequence length.
    num_predictions : number of diverse predictions to generate.

    Returns
    -------
    List of num_predictions (L, 3) coordinate arrays.
    """
    strategy = ensemble.get_diversity_strategy(length)
    predictions = []

    n_templates = min(len(template_coords_list), strategy["num_templates"])

    # Slot 1: Best template (or ensemble if neural is available)
    if neural_coords is not None and n_templates > 0:
        pred_dict = {
            "template": template_coords_list[0],
            "resnet": neural_coords,
            "transformer": neural_coords,
        }
        predictions.append(ensemble.ensemble_predict(pred_dict, length))
    elif n_templates > 0:
        predictions.append(template_coords_list[0].copy())

    # Remaining slots: different templates
    for i in range(1, min(n_templates, num_predictions)):
        predictions.append(template_coords_list[i].copy())

    # Fill remaining slots with perturbations
    while len(predictions) < num_predictions:
        if len(predictions) == 0:
            break
        base = predictions[0].copy()
        noise = np.random.randn(*base.shape) * strategy["perturbation_scale"]
        predictions.append(base + noise)

    return predictions[:num_predictions]
