# Post-Mortem: SUB005 and SUB006

## SUB005 (Multi-Template Diverse Prediction)
- **Kernel**: stanford-rna-3d-template-refinement v3
- **Status**: COMPLETE
- **LB Submissions**: 2x PENDING (submitted via UI at 20:17 and 20:38 UTC)
- **Validation**: Mean TM=0.113 (20 targets), Best: 9IWF=0.582, 9E9Q=0.504
- **Template count**: 5716 templates, runtime: 828s
- **Key issue**: Only 2/20 validation targets > 0.3 TM

## SUB006 (Fragment Assembly + Per-Chain)
- **Kernel**: stanford-rna-3d-fragment-assembly
- **Status**: COMPLETE  
- **LB Submissions**: PENDING
- **Validation**: Mean TM=0.1794 (28 targets), Median=0.0631
- **Top scores**: 9G4J=0.7287, 9LJN=0.6637, 9KGG=0.5892, 9IWF=0.5693, 9E9Q=0.5154, 9E75=0.3360
- **Template count**: 5716 templates, runtime: 1236s
- **Key improvement**: 6/28 targets > 0.3 (vs 2/20 for SUB005)

## Comparison
| Metric | SUB005 | SUB006 |
|--------|--------|--------|
| Val Mean TM | 0.113 | 0.179 |
| Targets > 0.3 | 2/20 | 6/28 |
| Best target | 0.582 | 0.729 |
| Runtime | 828s | 1236s |

## Key Observations
1. **Fragment assembly dramatically helps**: SUB006 finds 3 new high-scoring targets (9G4J, 9LJN, 9KGG) that SUB005 missed
2. **Per-chain prediction critical**: Breaking multi-chain complexes into individual chains allows finding better templates
3. **Still bimodal**: Most targets (22/28) still score < 0.1 — no good templates exist for them
4. **Template coverage is the bottleneck**: Adding more templates (from validation set) could help

## Root Causes for Poor Targets
- Very short sequences (L < 40): 9RVP (34), 9I9W (28), 9OD4 (23), 8ZNQ (30)
- No similar sequences in training set
- Unique structural motifs not represented in template library

## Improvement Opportunities
1. Add validation set as templates (~3000 more structures)
2. Secondary structure constraints for de novo/low-template targets
3. Better coordinate refinement with base-pair distance constraints
4. Neural refinement layer (GNN/Transformer already in codebase)
