# Protein Data Bank (PDB)

## Overview [IT002]

- **What**: The worldwide archive of experimentally determined 3D structures of biological macromolecules (proteins, nucleic acids, complexes).
- **URL**: https://www.rcsb.org/
- **Size**: Over 200,000 structures as of 2025. RNA-containing entries: approximately 5,000 with resolution <= 4.0 A.
- **Relevance**: Source of all template structures for template-based RNA 3D prediction.

## PDB File Format [IT002]

- **ATOM records**: One line per atom. Fixed-width columns:
  - Columns 1-6: Record type ("ATOM  " or "HETATM")
  - Columns 13-16: Atom name (e.g., "C1'", "C3'", "P", "N1")
  - Columns 18-20: Residue name (e.g., "A", "C", "G", "U", "ADE", "CYT", "GUA", "URA")
  - Column 22: Chain ID (single character)
  - Columns 23-26: Residue sequence number
  - Columns 31-38: X coordinate (Angstroms)
  - Columns 39-46: Y coordinate
  - Columns 47-54: Z coordinate
- **Parsing approach**: Direct string slicing (no external parser needed). See `_parse_pdb_text()` in template_db.py.

## RNA Residue Names in PDB [IT002]

Three-letter to one-letter mapping:

| 3-letter | 1-letter | Nucleotide |
|----------|----------|------------|
| A, ADE, RA | A | Adenine |
| C, CYT, RC | C | Cytosine |
| G, GUA, RG | G | Guanine |
| U, URA, RU | U | Uracil |
| DA, DC, DG, DT | A, C, G, U | DNA variants (mapped to RNA equivalents) |

## RCSB PDB REST API [IT002]

- **Search endpoint**: `https://search.rcsb.org/rcsbsearch/v2/query` (POST with JSON query)
- **Download endpoint**: `https://files.rcsb.org/download/{PDB_ID}.pdb`
- **Query for RNA structures**: Filter by `entity_poly.rcsb_entity_polymer_type = "RNA"` and `rcsb_entry_info.resolution_combined` range.
- **Rate limiting**: Polite delay of 0.05-0.1 seconds between requests. No authentication needed.
- **Caching strategy**: Download PDB file once, parse to JSON, cache locally. Index stored as pickle file for fast loading.

## Resolution [IT002]

- **What**: Measure of the level of detail in the experimental structure. Lower is better.
- **Units**: Angstroms (A).
- **Thresholds**:
  - < 2.0 A: High resolution. Atomic detail clearly visible.
  - 2.0-3.0 A: Medium resolution. Overall fold reliable, some side-chain ambiguity.
  - 3.0-4.0 A: Low resolution. Backbone trace reliable, detail uncertain.
  - > 4.0 A: Very low resolution. Excluded from template database.
- **Pipeline setting**: max_resolution=4.0 A (includes all usable RNA structures).

## Experimental Methods [IT002]

- **X-ray crystallography**: Most common for high-resolution structures. Requires crystal formation.
- **Cryo-electron microscopy (cryo-EM)**: Growing rapidly. Can handle larger complexes (e.g., ribosome). Typically lower resolution than X-ray.
- **NMR spectroscopy**: For small RNAs in solution. Provides dynamics information but limited size.
