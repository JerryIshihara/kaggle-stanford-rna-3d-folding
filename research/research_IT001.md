# Research — IT001: Pipeline Bootstrap and Competition Analysis

## Iteration ID
IT001

## Title
Pipeline bootstrap — competition analysis and initial architecture survey

## Target Module(s)
All modules (data_processor, inferencer, optimizer, validator) — structural bootstrap

## Research Question
What is the competition format, evaluation metric, data structure, and what are the leading approaches for RNA 3D structure prediction that should inform our baseline?

## Background / Context
Stanford RNA 3D Folding 2 is a Kaggle competition with a $75,000 prize pool (deadline March 25, 2026). The task is to predict 3D atomic coordinates of RNA molecules from nucleotide sequences. The evaluation metric is RMSD between predicted and ground-truth coordinates (lower is better). Training data includes RNA sequences, MSA (Multiple Sequence Alignment) files, and ground-truth 3D structures.

## Findings

### Competition Structure
- Input: RNA nucleotide sequences + MSA evolutionary information
- Output: per-residue 3D coordinates (x, y, z)
- Metric: RMSD
- Data includes MSA files (.fasta) providing evolutionary co-variation signals

### Leading Approaches in RNA 3D Prediction
1. **Deep learning on sequences**: RNNs, CNNs, Transformers that directly map sequences to coordinates. Simple but limited without structural priors.
2. **Graph Neural Networks**: Treat RNA as a graph (nodes = nucleotides, edges = bonds/contacts). Libraries like PyTorch Geometric support this. Strong for capturing local structure.
3. **Template-based methods**: Align query RNA to known structures in PDB. High accuracy when good templates exist, poor otherwise.
4. **Physics-based / energy minimization**: Rosetta/ViennaRNA for secondary structure → 3D folding. Computationally expensive but grounded in biophysics.
5. **Hybrid approaches**: Combine learned features with physics constraints (e.g. bond length regularization, secondary structure as auxiliary loss).
6. **AlphaFold-inspired**: Evoformer-style attention over MSA + pair representations, adapted for RNA.

### Key Signals Available
- MSA co-evolution (correlated mutations indicate spatial proximity)
- Secondary structure (base pairing patterns)
- Sequence length and composition
- Homologous structure templates from PDB

## Candidate Ideas Generated
1. Start with a simple RNN/CNN baseline to establish a working end-to-end pipeline
2. Add MSA-derived features (co-variation, conservation scores) to the data processor
3. Implement GNN-based model using contact maps
4. Add secondary structure prediction as auxiliary task
5. Use template alignment features from PDB
6. Physics-informed loss (bond length constraints)

## Expected Impact
IT001 is structural — no score impact. Establishes the pipeline for all future iterations.

## Risks / Assumptions
- The exact competition data format may require adjustments to the loader once data is downloaded
- Baseline models (RNN/CNN) will likely score poorly compared to competition leaders; they exist to validate the pipeline

## Source Links
- https://www.kaggle.com/competitions/stanford-rna-3d-folding-2 — Competition page
- https://www.nature.com/articles/s41576-019-0203-6 — RNA 3D structure prediction review
- https://www.rosettacommons.org/docs/latest/application_documentation/rna/rosetta-rna — RosettaRNA documentation
- https://pytorch-geometric.readthedocs.io/ — PyTorch Geometric for GNN approaches
- https://www.tbi.univie.ac.at/RNA/ — ViennaRNA for secondary structure

## Recommended Next Action
Complete pipeline bootstrap (IT001), then proceed to IT002: download data, validate the loader against real competition files, and run the baseline end-to-end.
