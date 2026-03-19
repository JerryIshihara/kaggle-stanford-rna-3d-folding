# Kaggle Pipeline Agent Iteration Protocol

This file defines the rules for an AI agent operating on the Stanford RNA 3D Folding 2
competition pipeline. Follow this protocol exactly for every iteration.

## Competition Context

- **Competition**: Stanford RNA 3D Folding 2
- **URL**: https://www.kaggle.com/competitions/stanford-rna-3d-folding-2
- **Metric**: RMSD (lower is better)
- **Deadline**: March 25, 2026

## Session Startup

At the beginning of every session:

1. Read `iteration_registry.md` to understand current state.
2. Read `submissions/scoreboard.md` to know the current best score.
3. Identify the next iteration ID (increment from the last entry).
4. Determine the highest-value next action using the priority order below.

## Iteration ID Format

- IT001, IT002, IT003, ...
- Always zero-pad to three digits.

## 6-Phase Iteration Cycle

Every iteration MUST follow these phases in order. No implementation before Phase 1 and 2 are complete.

### Phase 1 — Research

Create `research/research_<ID>.md` containing:
- Iteration ID
- Title
- Target module(s)
- Research question
- Background / context
- Findings (from Kaggle discussions, notebooks, papers, GitHub, docs)
- Candidate ideas generated
- Expected impact
- Risks / assumptions
- Source links (title, URL, relevance note for each)
- Recommended next action

Research sources to check:
- Kaggle discussion threads and public notebooks
- Kaggle solution writeups from similar competitions
- Academic papers
- GitHub repositories
- Official documentation
- High-quality blog posts

### Phase 2 — Plan

Create `plans/plan_<ID>.md` containing:
- Iteration ID
- Title
- Target module(s)
- Hypothesis
- Files to create/modify
- Exact functions/features to add or modify
- Expected metric impact
- Evaluation plan
- Rollback plan
- Linked research file

Prefer small, high-signal changes over large ambiguous refactors.

### Phase 3 — Implement

- Use the iteration ID in new filenames when practical (e.g. `data_processor/features_IT021.py`).
- If modifying existing files, record exact file path, function names, and change summary.
- Every change must record: what, where, why, source, how tested, outcome, next steps.

### Phase 4 — Evaluate

Run the pipeline and evaluate:
- Local CV score (use `scripts/run_pipeline.py` or module code directly)
- Fold-by-fold performance
- Variance / stability
- Comparison with prior best
- Ablation results if applicable

### Phase 5 — Document

Create `reports/report_<ID>.md` containing:
- Iteration ID, title, target module(s)
- Files changed, functions/features changed
- Experiment setup, validation setting
- Metrics and comparison vs previous baseline
- Outcome classification (see below)
- Decision and follow-up recommendation

Then update ALL of the following:
- `iteration_registry.md` — add the new entry
- Relevant module README(s) — add to iteration history table
- `research/README.md` — add research file entry
- `plans/README.md` — add plan file entry
- `reports/README.md` — add report file entry
- `checkpoints/README.md` — if checkpoints were saved
- Root `README.md` — update best score if improved
- `learning/` — sync domain knowledge (see Learning Knowledge Base section below)

### Phase 6 — Submission Assembly (when applicable)

When a validated improvement is ready for Kaggle submission:

1. Create submission ID: SUB001, SUB002, ...
2. Create `submissions/submission_<SUB_ID>.py` (or .ipynb) combining selected module versions.
3. Create `submissions/submission_<SUB_ID>.md` with full traceability metadata.
4. Update `submissions/README.md` and `submissions/scoreboard.md`.

Submission metadata must include:
- Submission ID
- Selected version from each module (data_processor, inferencer, optimizer, validator)
- Related checkpoints
- Expected local validation score
- Status (DRAFT / READY / SUBMITTED / BEST_CURRENT / SUPERSEDED / ARCHIVED)

## Outcome Classification

Every report MUST classify the result as one of:

- **PROMOTED**: Validated improvement — keep and integrate.
- **REJECTED**: No improvement or harmful — revert or discard.
- **PARKED**: Interesting but not production-ready — save for later.
- **NEEDS_FOLLOWUP**: Inconclusive — requires more testing.

Never silently keep or discard changes.

## Priority Order for Selecting Next Work

1. Validation correctness, leakage prevention, reproducibility
2. Strong evidence-backed improvements from research
3. Bottleneck module improvements (highest expected value)
4. Optimization and ensembling (only after stable validation exists)
5. Structural improvements that increase future iteration speed

Always ask:
- What is the current bottleneck?
- Which module has the highest expected value of improvement?
- What is the cheapest high-signal experiment?
- What research-backed idea has not been tested?
- What structural weakness is slowing future iteration?

## Module Responsibilities

### data_processor/
Data loading, cleaning, transformation, feature engineering, fold preparation,
template building, augmentation, graph/tensor construction, caching.

### inferencer/
Model architecture, forward/inference logic, decoding, post-processing,
ensembling, confidence estimation.

### optimizer/
Training loop, loss functions, optimizer/scheduler logic, checkpoint saving,
fine-tuning, pseudo-labeling, curriculum learning, augmentation policy.

### validator/
Cross-validation, leakage prevention, split generation, metric computation,
local leaderboard estimation, ablation support, model comparison.

### checkpoints/
Saved weights, training states, ensemble artifacts — each traceable to
an iteration ID and report.

## File Naming Conventions

| Artifact | Pattern |
|----------|---------|
| Research | `research/research_<ID>.md` |
| Plan | `plans/plan_<ID>.md` |
| Report | `reports/report_<ID>.md` |
| Module code | `<module>/<descriptive_name>_<ID>.py` |
| Checkpoint | `checkpoints/<ID>_<description>.pt` |
| Submission notebook | `submissions/submission_<SUB_ID>.ipynb` |
| Submission script | `submissions/submission_<SUB_ID>.py` |
| Submission docs | `submissions/submission_<SUB_ID>.md` |

## Learning Knowledge Base

Every iteration MUST sync domain knowledge to `learning/`. This is a persistent,
accumulating knowledge base that grows with each iteration. It ensures that insights,
algorithms, biology concepts, and references are never lost between sessions.

### Folder Structure

```
learning/
├── README.md           # Index and overview
├── cs/                 # Computer science: algorithms, data structures, complexity
│   └── *.md            # One file per topic cluster
├── ml/                 # Machine learning: architectures, losses, training, evaluation
│   └── *.md            # One file per topic cluster
├── bio/                # Biology & bioinformatics: RNA, proteins, PDB, structural biology
│   └── *.md            # One file per topic cluster
└── sources.md          # Master bibliography — every URL, paper, notebook referenced
```

### What to Sync

After each iteration, extract and append any NEW domain knowledge to the appropriate file:

| Category | Examples |
|----------|----------|
| `cs/` | Sequence alignment algorithms, dynamic programming, graph algorithms, k-mer indexing, SVD/eigenvalue decomposition, coordinate geometry |
| `ml/` | Model architectures (CNN, RNN, Transformer, GNN), loss functions, optimizers, schedulers, regularization, ensembling, MC-dropout, TM-score vs RMSD |
| `bio/` | RNA structure (primary/secondary/tertiary), A-form helix geometry, nucleotide chemistry, PDB format, C1'/C3'/P atoms, backbone torsion angles, base pairing, MSA, co-evolution |
| `sources.md` | Every paper, URL, Kaggle notebook, GitHub repo, or blog post encountered — with title, URL, date accessed, relevance note, and the iteration ID that introduced it |

### Rules

1. **Append, never overwrite.** Add new knowledge; do not remove or rewrite existing entries.
2. **Tag with iteration ID.** Every new entry must note which iteration produced it (e.g. `[IT002]`).
3. **Include source.** Every factual claim must have a source URL or citation.
4. **Keep it concise.** Bullet points and short paragraphs, not essays.
5. **Cross-link.** Reference related entries in other learning files when relevant.

### Sync Checklist (add to Phase 5)

- [ ] Any new algorithm or CS concept? → `learning/cs/`
- [ ] Any new ML technique, architecture, or training insight? → `learning/ml/`
- [ ] Any new biology or bioinformatics concept? → `learning/bio/`
- [ ] Any new source URL or publication? → `learning/sources.md`

## Validity Rules

No implementation is valid unless:
- It has an iteration ID
- It has a research artifact
- It has a plan artifact
- It has a report artifact
- It is linked from the relevant module README
- It is linked from `iteration_registry.md`

No submission is valid unless:
- It has a submission ID
- It states the selected version from each module
- It is recorded in `submissions/README.md` and `submissions/scoreboard.md`
- It links back to relevant iteration artifacts
