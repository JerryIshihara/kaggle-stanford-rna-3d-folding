#!/usr/bin/env python3
"""
Download RNA structures from the RCSB PDB and build a local template database.

Usage (from project root):
    python3 scripts/download_pdb_rna.py [--max-entries 2000] [--max-resolution 4.0] [--db-dir data/template_db]
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data_processor.template_db import PDBRNADatabase


def main():
    parser = argparse.ArgumentParser(description="Download RNA structures from PDB")
    parser.add_argument("--max-entries", type=int, default=2000,
                        help="Maximum number of PDB entries to download")
    parser.add_argument("--max-resolution", type=float, default=4.0,
                        help="Maximum resolution cutoff in Angstroms")
    parser.add_argument("--db-dir", type=str, default="data/template_db",
                        help="Directory to store the template database")
    parser.add_argument("--delay", type=float, default=0.1,
                        help="Delay between API requests in seconds")
    args = parser.parse_args()

    db = PDBRNADatabase(db_dir=args.db_dir)

    print(f"=== PDB RNA Structure Download ===")
    print(f"  Max entries     : {args.max_entries}")
    print(f"  Max resolution  : {args.max_resolution} Å")
    print(f"  Database dir    : {args.db_dir}")
    print()

    n_chains = db.build_database(
        max_entries=args.max_entries,
        max_resolution=args.max_resolution,
        delay=args.delay,
    )

    print(f"\n=== Download Complete ===")
    print(f"  Total chains indexed: {n_chains}")
    print(f"  Database location   : {args.db_dir}")


if __name__ == "__main__":
    main()
