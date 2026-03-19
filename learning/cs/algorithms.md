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

## Fragment-Based Assembly [IT005]

- **What**: Splits long sequences into overlapping fragments, finds best template per fragment, transfers coordinates per fragment, and stitches them together using Kabsch superposition on overlapping regions.
- **How it works**:
  1. Split query into fragments of size F (100nt) with overlap O (30nt)
  2. For each fragment, run template search independently (smaller sequences match better)
  3. Transfer coordinates per fragment using NW alignment
  4. For each subsequent fragment, use Kabsch superposition on the overlapping region to align it to the already-placed coordinates
  5. In overlap regions, blend coordinates with position-weighted averaging
- **Complexity**: O(K * F * T) per fragment where K is number of fragments, F is fragment size, T is template search cost
- **Use in pipeline**: For long RNA chains (>200nt) where no good full-length template exists, fragment assembly provides better coordinate coverage than a single poor full-length template.
- **Key parameters**: FRAGMENT_SIZE=100, FRAGMENT_OVERLAP=30, FRAGMENT_MIN_SIM=0.15
- **Source**: Inspired by Rosetta (protein structure prediction) and I-TASSER fragment assembly approaches.

## Affine Gap Penalties [IT005]

- **What**: Extension of NW alignment where gap opening and gap extension have different penalties.
- **Gap open**: -4 (cost to start a new gap)
- **Gap extend**: -1 (cost to extend an existing gap)
- **Why**: In RNA, insertions/deletions tend to occur as contiguous blocks (e.g., loops). Affine gaps model this better than linear gap penalties.
- **Use in pipeline**: Replaces the linear gap penalty (-2) used in IT002-IT004.

## Coverage-Weighted Template Scoring [IT005]

- **What**: Template quality metric that combines sequence similarity with coverage and length compatibility.
- **Formula**: `score = nw_similarity × sqrt(min(qlen, tlen) / max(qlen, tlen)) × valid_fraction`
- **Why**: A template with 90% sequence identity but only 30% length coverage is worse than one with 70% identity and 95% coverage.
- **Use in pipeline**: Replaces simple NW-score-only ranking from IT002-IT004.

## Sequence Identity [IT002]

- **What**: Fraction of aligned positions where both sequences have the same nucleotide.
- **Formula**: identity = matches / aligned_length (excludes pure-gap columns).
- **Use in pipeline**: Ranks template hits; higher identity templates are weighted more heavily in the ensemble. Minimum threshold of 0.2 filters out poor matches.
