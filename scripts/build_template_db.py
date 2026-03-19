#!/usr/bin/env python3
"""
Build the template database index and run a quick sanity check.

Usage (from project root):
    python3 scripts/build_template_db.py [--db-dir data/template_db]

Assumes download_pdb_rna.py has already been run.
"""

import argparse
import sys
import json
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data_processor.template_db import PDBRNADatabase
from inferencer.template_model import TemplateModel, generate_helix_coords


def main():
    parser = argparse.ArgumentParser(description="Build and verify template database")
    parser.add_argument("--db-dir", type=str, default="data/template_db",
                        help="Directory containing downloaded PDB data")
    parser.add_argument("--test-sequence", type=str, default=None,
                        help="Optional test RNA sequence for sanity check")
    args = parser.parse_args()

    db = PDBRNADatabase(db_dir=args.db_dir)

    print(f"=== Template Database Status ===")
    print(f"  Database dir    : {args.db_dir}")
    print(f"  Chains indexed  : {len(db.index)}")

    if not db.index:
        print("\n  WARNING: Database is empty. Run download_pdb_rna.py first.")
        return

    # Summary statistics
    lengths = [entry["length"] for entry in db.index.values()]
    print(f"  Min chain length: {min(lengths)}")
    print(f"  Max chain length: {max(lengths)}")
    print(f"  Mean chain length: {np.mean(lengths):.1f}")
    print(f"  Unique PDB IDs  : {len(set(e['pdb_id'] for e in db.index.values()))}")

    # Sanity check with a test query
    test_seq = args.test_sequence or _pick_test_sequence(db)
    if test_seq:
        print(f"\n=== Template Search Test ===")
        print(f"  Query length: {len(test_seq)}")
        print(f"  Query (first 50): {test_seq[:50]}...")

        model = TemplateModel(database=db, top_k=3, min_identity=0.2)
        result = model.predict(test_seq)

        print(f"  Method       : {result['method']}")
        print(f"  Confidence   : {result['confidence']:.3f}")
        print(f"  Coords shape : {result['coords'].shape}")
        print(f"  Templates    : {len(result['templates_used'])}")
        for t in result["templates_used"]:
            print(f"    - {t['pdb_id']}:{t['chain_id']} (identity={t['identity']:.3f})")

    # Fallback sanity check
    print(f"\n=== Helix Fallback Test ===")
    helix = generate_helix_coords(20)
    print(f"  Generated helix for length 20: shape={helix.shape}")
    dists = np.linalg.norm(np.diff(helix, axis=0), axis=1)
    print(f"  Mean inter-residue distance: {dists.mean():.2f} Å")

    print(f"\n=== Database Ready ===")


def _pick_test_sequence(db: PDBRNADatabase) -> str:
    """Pick a random sequence from the database for testing."""
    entries = list(db.index.values())
    if not entries:
        return ""
    idx = np.random.randint(len(entries))
    return entries[idx]["sequence"]


if __name__ == "__main__":
    main()
