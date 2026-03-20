# Algorithms

## Needleman-Wunsch Global Sequence Alignment [IT002]

- **What**: Dynamic programming algorithm for optimal global pairwise sequence alignment.
- **Complexity**: O(nm) time and space where n, m are sequence lengths.
- **How it works**: Fills a scoring matrix with match/mismatch/gap penalties, then traces back to find the optimal alignment path.
- **Parameters used**: match_score=2, mismatch_score=-1, gap_penalty=-2.
- **Output**: Aligned sequences, match count, aligned length, and a position mapping (query_pos -> template_pos).
- **Use in pipeline**: Aligns query RNA sequences to PDB template sequences to determine which residues correspond, enabling coordinate transfer.
- **Limitation**: O(nm) is expensive for long sequences (>1000 nt). For large-scale search, a k-mer pre-filter is used first.
- **Source**: Needleman & Wunsch, "A general method applicable to the search for similarities in the amino acid sequence of two proteins", J. Mol. Biol. 48(3):443-453, 1970. https://doi.org/10.1016/0022-2836(70)90057-4

## K-mer Jaccard Pre-filter [IT002]

- **What**: Fast approximate sequence similarity filter using k-mer (substring) sets.
- **How it works**: Extract all k-length substrings from two sequences, compute Jaccard similarity = |intersection| / |union|.
- **Parameters used**: k=4, threshold = min_identity * 0.3 (loose filter to avoid missing good candidates).
- **Complexity**: O(n + m) to build k-mer sets, O(min(|A|, |B|)) for Jaccard computation.
- **Use in pipeline**: Pre-filters template database before running expensive Needleman-Wunsch alignment. Reduces candidates from thousands to ~top_k * 5.
- **Source**: General bioinformatics technique. Used in tools like minimap2 and MMseqs2.

## Kabsch Algorithm [IT002]

- **What**: Computes the optimal rotation matrix to superpose two sets of paired 3D points, minimizing RMSD.
- **How it works**:
  1. Center both point sets at their centroids.
  2. Compute cross-covariance matrix H = Q^T P.
  3. SVD: H = U S V^T.
  4. Rotation: R = V diag(1, 1, sign(det(V U^T))) U^T.
  5. RMSD = sqrt(sum((P_centered - Q_centered @ R)^2) / N).
- **Complexity**: O(N) for N point pairs (SVD on 3x3 matrix is constant).
- **Use in pipeline**: Evaluates structural similarity between predicted and reference coordinates. Also used for template superposition.
- **Source**: Kabsch, "A solution for the best rotation to relate two sets of vectors", Acta Crystallographica A32:922-923, 1976. https://doi.org/10.1107/S0567739476001873

## Linear Interpolation for Gap Filling [IT002]

- **What**: Fills unmapped residue positions by linearly interpolating coordinates between the nearest mapped neighbors.
- **How it works**: For a gap position i between mapped positions left and right: `coords[i] = coords[left] * (1 - frac) + coords[right] * frac` where frac = (i - left) / (right - left).
- **Edge case**: For terminal gaps (no left or right neighbor), extrapolates using estimated local backbone direction.
- **Use in pipeline**: After coordinate transfer from template to query via alignment, gapped positions (insertions relative to template) need coordinates. Interpolation provides reasonable initial guesses.

## TM-Score Computation [IT005]

- **What**: Template Modeling score — a metric for evaluating structural similarity independent of protein/RNA length.
- **Formula**: TM = (1/L) * sum(1 / (1 + (d_i / d0)^2)) where d0 = 0.6 * sqrt(L - 0.5) - 2.5
- **Properties**:
  - Length-independent: normalized by target length L
  - Range [0, 1]: 1.0 = identical structures
  - TM > 0.45: correct global fold (for RNA)
  - TM > 0.17: better than random
- **Implementation**: Requires Kabsch superposition first to find optimal R, t, then compute per-residue distances.
- **Use in pipeline**: Primary metric for competition evaluation. Also used for local validation.
- **Source**: Zhang & Skolnick, RNA-align. https://zhanggroup.org/RNA-align/

## RNA-Aware NW Scoring [IT005]

- **What**: Modified Needleman-Wunsch scoring that distinguishes transition vs transversion mutations in RNA.
- **Transitions**: A<->G (purine-purine) or C<->U (pyrimidine-pyrimidine), penalty=-0.5
- **Transversions**: Purine<->pyrimidine, penalty=-1.5
- **Rationale**: Transitions are more conservative mutations and sequences with transitions are more likely to share structure.
- **Use in pipeline**: Improves alignment quality by penalizing structurally disruptive mutations more heavily.

## Multi-Template Blending with Kabsch [IT005]

- **What**: Combine coordinate predictions from multiple templates using Kabsch-aligned weighted average.
- **How**: 
  1. Transfer coordinates from each template to query via NW alignment
  2. Superpose all transfers onto reference (first template) using Kabsch
  3. Compute weighted average coordinates with similarity-based weights
- **Use in pipeline**: Produces smoother consensus prediction for one of 5 prediction slots.

## Sequence Identity [IT002]

- **What**: Fraction of aligned positions where both sequences have the same nucleotide.
- **Formula**: identity = matches / aligned_length (excludes pure-gap columns).
- **Use in pipeline**: Ranks template hits; higher identity templates are weighted more heavily in the ensemble. Minimum threshold of 0.2 filters out poor matches.

## Distance Geometry / Multidimensional Scaling (MDS) [IT007]

- **What**: Method to embed objects in Euclidean space from pairwise distance information.
- **Classical MDS algorithm**:
  1. Construct squared distance matrix D² from pairwise distances
  2. Double-center: B = -0.5 * H * D² * H where H = I - (1/n)*11'
  3. Eigendecompose B = V * Λ * V'
  4. Take top 3 eigenvectors/eigenvalues → coordinates X = V_3 * sqrt(Λ_3)
- **For RNA**: Build distance matrix from backbone (5.95 Å), base-pair (10.5 Å), and stacking (3.4 Å) constraints
- **Complexity**: O(n³) for eigendecomposition, O(n²) for subsampled MDS with interpolation
- **Use in pipeline**: De novo 3D coordinate generation for targets without good templates.
- **Source**: Crippen & Havel (1988), Distance Geometry and Molecular Conformation

## Simulated Annealing (SA) Refinement [IT007]

- **What**: Optimization that allows uphill moves with decreasing probability over time.
- **Temperature schedule**: T(t) = T_init * (T_final/T_init)^(t/t_max), exponential cooling
- **For RNA refinement**: Energy = E_bond + E_pair + E_stack + E_clash + E_smooth
  - E_bond: backbone distance deviation from 5.95 Å
  - E_pair: base-pair distance deviation from 10.5 Å  
  - E_stack: stacking distance deviation from 3.4 Å
  - E_clash: penalty for non-bonded distances < 3.2 Å
  - E_smooth: Laplacian smoothing penalty
- **Use in pipeline**: 25-30 iterations of coordinate refinement after template transfer or de novo generation.

## Max-Dispersion Selection [IT007]

- **What**: Greedy algorithm to select the k most diverse items from a set.
- **Algorithm**:
  1. Start with best item (highest quality/confidence)
  2. Repeat k-1 times: select the item maximizing min RMSD to already-selected set
- **Complexity**: O(n²k) where n is candidate pool, k is selection size
- **Use in pipeline**: Generate 10 prediction candidates, select 5 most structurally diverse to optimize best-of-5 metric.
