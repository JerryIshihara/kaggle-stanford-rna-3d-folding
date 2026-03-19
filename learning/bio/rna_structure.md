# RNA 3D Structure

## RNA Basics [IT001]

- **RNA (Ribonucleic Acid)**: Single-stranded nucleic acid polymer. Four nucleotides: Adenine (A), Cytosine (C), Guanine (G), Uracil (U).
- **Primary structure**: The linear nucleotide sequence (e.g., "GGCAUUCCGGA").
- **Secondary structure**: Base-pairing patterns. Watson-Crick pairs (A-U, G-C) and wobble pairs (G-U). Forms stems, loops, bulges, junctions.
- **Tertiary structure**: The full 3D arrangement of atoms in space. This is what the competition predicts.
- **Functional importance**: RNA 3D structure determines function -- catalysis (ribozymes), gene regulation (riboswitches), protein synthesis (ribosome).

## A-form Helix Geometry [IT002]

- **What**: The canonical helical conformation of double-stranded RNA.
- **Parameters**:
  - Rise per residue: 2.81 Angstroms along the helix axis
  - Helix radius: 9.4 Angstroms (for backbone C3' atom)
  - Twist per residue: 32.7 degrees (about 11 base pairs per turn)
- **Use in pipeline**: Geometric fallback -- when no template is found, generate an idealized A-form helix as a baseline prediction. Produces physically plausible (though likely wrong) backbone coordinates.
- **Difference from B-form DNA**: RNA adopts A-form (wider, shorter) rather than B-form (narrower, taller) due to the 2'-OH group on ribose.

## Key Atoms per Residue [IT002, SUB001]

- **C1' (C1-prime)**: The glycosidic carbon connecting the sugar to the base. This is the atom whose coordinates the competition evaluates (TM-score on C1' positions).
- **C3' (C3-prime)**: Carbon in the sugar ring. Often used as a backbone representative in structural biology. The original pipeline (IT002) used C3' by default.
- **P (Phosphorus)**: Part of the phosphodiester backbone. Connects adjacent nucleotides.
- **Critical fix in SUB001**: Changed atom preference from [C3', C1', P] to [C1', C3', P] to match what the competition actually scores.

## Backbone Representation [IT002]

- For each residue, a single representative atom (C1' preferred) gives one (x, y, z) coordinate.
- An RNA of length L is represented as an (L, 3) coordinate array.
- Inter-residue C1'-C1' distances are typically 5-7 Angstroms for adjacent residues.
- C3'-C3' distances are similar but not identical due to different positions in the sugar ring.

## Structural Homology and Template-Based Prediction [IT002]

- **Principle**: Homologous RNA sequences (sharing evolutionary ancestry) tend to adopt similar 3D structures.
- **Sequence identity thresholds**:
  - >50%: Very likely to share the same fold. High-confidence template predictions.
  - 30-50%: Probably similar fold but local differences. Moderate confidence.
  - 20-30%: Possible structural similarity. Low confidence, needs careful alignment.
  - <20%: Unlikely to share fold. Template prediction unreliable.
- **Template coverage**: Not all RNA sequences have structural homologs in PDB. Novel folds require ab initio methods.

## Multiple Sequence Alignments (MSA) [IT001, IT002]

- **What**: Alignment of multiple related RNA sequences from different organisms.
- **Information content**: Reveals conserved positions (structurally/functionally important) and co-evolving positions (likely in spatial contact).
- **Competition data**: MSA files provided as FASTA for each target (e.g., MSA/1A4D.MSA.fasta).
- **Co-evolution signals**: Pairs of positions that mutate together suggest structural contacts. Used in contact prediction (DCA, plmDCA). Not yet exploited in our pipeline.
- **Conservation scores**: Highly conserved positions are often in the structural core. Could be used as features for ML models.
