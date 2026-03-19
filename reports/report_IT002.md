# Report — IT002: Template-Based Pipeline Implementation

## Iteration ID
IT002

## Title
Template-based RNA 3D structure prediction pipeline

## Target Module(s)
data_processor, inferencer

## Files Changed

### Created
- `data_processor/template_db.py` — `PDBRNADatabase`, `needleman_wunsch`, `sequence_identity`, `_kmer_set`
- `inferencer/template_model.py` — `TemplateModel`, `TemplateEnsemble`, `transfer_coordinates`, `generate_helix_coords`, `kabsch_rmsd`
- `scripts/download_pdb_rna.py` — PDB RNA structure download script
- `scripts/build_template_db.py` — Database build and verification script

### Modified
- `plans/plan_IT002.md` — augmented with practical dependency and API approach notes
- `data_processor/README.md` — added IT002 to iteration history
- `inferencer/README.md` — added IT002 to iteration history
- `research/README.md` — added research_IT002 entry
- `plans/README.md` — added plan_IT002 entry
- `reports/README.md` — added report_IT002 entry
- `iteration_registry.md` — added IT002 entry

## Functions / Features Changed

### data_processor/template_db.py
- `PDBRNADatabase.search_rna_entries()` — queries RCSB PDB REST API for RNA-containing structures
- `PDBRNADatabase.download_entry()` — downloads and parses PDB text for a single entry, caches as JSON
- `PDBRNADatabase._parse_pdb_text()` — extracts RNA chain sequences and C3' backbone coordinates from PDB format
- `PDBRNADatabase.build_database()` — orchestrates full download and index construction
- `PDBRNADatabase.search_templates()` — k-mer pre-filter then full alignment scoring
- `needleman_wunsch()` — global pairwise alignment in pure numpy, returns alignment map
- `sequence_identity()` — computes identity from alignment

### inferencer/template_model.py
- `TemplateModel.predict()` — main entry: search templates, align, transfer coords, ensemble
- `TemplateModel._weighted_ensemble()` — identity-weighted average of template predictions
- `transfer_coordinates()` — maps template coords to query via alignment, interpolates gaps
- `generate_helix_coords()` — A-form RNA helix fallback geometry
- `kabsch_rmsd()` — Kabsch algorithm for optimal superposition and RMSD
- `TemplateEnsemble.predict()` — multi-model confidence-weighted ensemble

## Experiment Setup
Core logic unit tested locally (no GPU or competition data needed):
- Self-alignment identity: 1.000 (correct)
- Partial alignment: 5/8 matches for mismatched sequences (correct)
- Helix fallback produces reasonable inter-residue distances (~6.0 Å)
- Coordinate transfer from identical template is exact (np.allclose = True)

## Validation Setting
Unit tests only — full validation against competition data requires running `download_pdb_rna.py` first.

## Metrics
- **Alignment correctness**: verified on synthetic test cases
- **Coordinate transfer fidelity**: exact for identical sequences
- **Helix geometry**: inter-residue distance ~6.0 Å (reasonable for backbone C3')

## Comparison vs Previous Baseline
IT001 had no prediction capability. IT002 establishes the first working prediction pipeline.

## Outcome
**PROMOTED** — core template pipeline implemented and verified. Ready for database download and end-to-end testing.

## Decision
PROMOTED

## Follow-up Recommendation
- **Immediate**: Run `python3 scripts/download_pdb_rna.py` to populate the template database
- **IT003**: Test full pipeline end-to-end with competition data; generate first submission
- **IT004**: Add MSA-derived features (co-evolution, conservation) to improve template search
- **IT005**: Deep learning model for template-free cases
