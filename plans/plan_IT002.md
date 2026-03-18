# Plan — IT002: Template-Based Pipeline Implementation

## Iteration ID
IT002

## Title
Implement template-based RNA 3D structure prediction pipeline

## Target Module(s)
data_processor, inferencer, optimizer, validator

## Hypothesis
Template-based methods will provide the quickest score improvement, as evidenced by the current leader "best_template_oracle" (0.554 RMSD).

## Files to Create / Modify

### New files
- `data_processor/template_db.py` — PDB RNA structure database and alignment
- `inferencer/template_model.py` — Template-based prediction model
- `scripts/download_pdb_rna.py` — Download RNA structures from PDB
- `scripts/build_template_db.py` — Build and index template database

### Modified files
- `data_processor/loader.py` — Add template loading functionality
- `inferencer/__init__.py` — Register template model
- `scripts/run_pipeline.py` — Add template pipeline option

## Exact Functions / Features to Add

### 1. Template Database Module (`data_processor/template_db.py`)
- `PDBRNADatabase` class:
  - `download_rna_structures()`: Fetch RNA structures from PDB
  - `build_database()`: Process and index structures
  - `search_templates(sequence)`: Find best templates for query
  - `align_template(query_seq, template_id)`: Perform sequence-structure alignment
  
- `RNAStructureAligner` class:
  - `calculate_tm_score()`: TM-score for RNA structure comparison
  - `structural_alignment()`: Align 3D coordinates
  - `sequence_identity()`: Calculate sequence similarity

### 2. Template Model (`inferencer/template_model.py`)
- `TemplateModel` class:
  - `__init__(database_path)`: Load template database
  - `predict(sequence)`: Main prediction method
  - `ensemble_predict(sequences)`: Batch prediction
  
- `TemplateEnsemble` class:
  - `weighted_average()`: Combine multiple template predictions
  - `consensus_structure()`: Generate consensus from top templates

### 3. Download Scripts
- `download_pdb_rna.py`:
  - Download all RNA-containing structures from PDB
  - Filter by resolution, completeness
  - Save in standardized format
  
- `build_template_db.py`:
  - Process downloaded structures
  - Extract sequences and coordinates
  - Build search index (FASTA, MMseqs2, or custom)

### 4. Enhanced Loader (`data_processor/loader.py`)
- Add `load_template_database()` method
- Add `get_template_predictions()` method
- Integrate with existing data loading pipeline

## Evaluation Plan

### Success Criteria:
1. **Functional pipeline**: Template database can be built and queried
2. **Prediction generation**: Can produce coordinate predictions for test sequences
3. **Submission ready**: Output in correct Kaggle format
4. **Score improvement**: Better than random/geometric baselines

### Validation:
- **Cross-validation**: Leave-one-out on available training data (if any)
- **Template coverage**: Percentage of test sequences with good templates
- **Runtime**: Acceptable for competition timeline

### Metrics:
- **Primary**: RMSD score on validation set
- **Secondary**: Template hit rate (sequence identity > 30%)
- **Tertiary**: Prediction time per sequence

## Rollback Plan
If template approach fails:
1. Revert to geometric baseline
2. Focus on deep learning approach (IT005)
3. Document lessons learned for future iterations

## Implementation Timeline

### Day 1 (March 18-19):
- [ ] Download PDB RNA structures
- [ ] Build template database
- [ ] Implement basic template search

### Day 2 (March 19-20):
- [ ] Implement structure alignment
- [ ] Generate first template predictions
- [ ] Test submission format

### Day 3 (March 20-21):
- [ ] Optimize template selection
- [ ] Implement ensemble methods
- [ ] Validate on available data

### Day 4 (March 21-22):
- [ ] Finalize template pipeline
- [ ] Generate competition submission
- [ ] Evaluate leaderboard score

## Dependencies

### External Tools:
- **BioPython**: PDB parsing and sequence handling
- **MMseqs2** (optional): Fast sequence searching
- **ViennaRNA**: Secondary structure comparison

### Data Requirements:
- **PDB RNA structures**: ~5,000 structures expected
- **Disk space**: ~10-20GB for full database
- **Memory**: Sufficient for search index

## Risk Assessment

### High Risk:
- **Template coverage**: Some RNAs may have no good templates
- **Alignment accuracy**: RNA structure alignment is challenging
- **Time constraints**: 7 days until deadline

### Mitigation Strategies:
1. **Hybrid approach**: Combine with deep learning for template-free cases
2. **Fallback models**: Geometric baseline for uncovered sequences
3. **Parallel development**: Work on multiple approaches simultaneously

## Linked Research File
[research/research_IT002.md](../research/research_IT002.md)

## Next Iterations
- **IT003**: MSA feature engineering and co-evolution analysis
- **IT004**: Deep learning baseline implementation
- **IT005**: Ensemble methods and optimization

---

*Plan created: March 18, 2026*  
*Execution window: March 18-22, 2026*  
*Competition deadline: March 25, 2026*