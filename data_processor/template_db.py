"""
PDB RNA template database for structure prediction.

Uses the RCSB PDB REST API to search, download, and index RNA structures.
No biopython dependency — parses PDB/mmCIF coordinate data directly.
"""

import json
import pickle
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import requests
from tqdm import tqdm

RCSB_SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2/query"
RCSB_DATA_URL = "https://data.rcsb.org/rest/v1/core/entry"
RCSB_FASTA_URL = "https://www.rcsb.org/fasta/entry"
RCSB_COORD_URL = "https://files.rcsb.org/download"

RNA_RESIDUES = {"A", "C", "G", "U", "ADE", "CYT", "GUA", "URA",
                "DA", "DC", "DG", "DT",
                "RA", "RC", "RG", "RU"}

THREE_TO_ONE = {
    "A": "A", "ADE": "A", "RA": "A",
    "C": "C", "CYT": "C", "RC": "C",
    "G": "G", "GUA": "G", "RG": "G",
    "U": "U", "URA": "U", "RU": "U",
    "DA": "A", "DC": "C", "DG": "G", "DT": "U",
}


class PDBRNADatabase:
    """Searchable database of RNA 3D structures from the PDB.

    Parameters
    ----------
    db_dir : directory to cache downloaded structures and the index.
    """

    def __init__(self, db_dir: str = "data/template_db"):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.db_dir / "template_index.pkl"
        self.index: Dict[str, dict] = {}
        if self.index_path.exists():
            with open(self.index_path, "rb") as f:
                self.index = pickle.load(f)

    # ------------------------------------------------------------------
    # Search RCSB for RNA-containing entries
    # ------------------------------------------------------------------

    def search_rna_entries(
        self,
        max_results: int = 5000,
        min_resolution: float = 0.0,
        max_resolution: float = 4.0,
    ) -> List[str]:
        """Query RCSB for PDB IDs that contain RNA polymers.

        Returns a list of PDB IDs.
        """
        query = {
            "query": {
                "type": "group",
                "logical_operator": "and",
                "nodes": [
                    {
                        "type": "terminal",
                        "service": "text",
                        "parameters": {
                            "attribute": "entity_poly.rcsb_entity_polymer_type",
                            "operator": "exact_match",
                            "value": "RNA",
                        },
                    },
                    {
                        "type": "terminal",
                        "service": "text",
                        "parameters": {
                            "attribute": "rcsb_entry_info.resolution_combined",
                            "operator": "range",
                            "value": {
                                "from": min_resolution,
                                "to": max_resolution,
                                "include_lower": True,
                                "include_upper": True,
                            },
                        },
                    },
                ],
            },
            "return_type": "entry",
            "request_options": {
                "paginate": {"start": 0, "rows": max_results},
                "sort": [{"sort_by": "score", "direction": "desc"}],
            },
        }

        resp = requests.post(RCSB_SEARCH_URL, json=query, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return [hit["identifier"] for hit in data.get("result_set", [])]

    # ------------------------------------------------------------------
    # Download and parse a single PDB entry
    # ------------------------------------------------------------------

    def download_entry(self, pdb_id: str) -> Optional[dict]:
        """Download and parse an RNA entry from RCSB.

        Returns a dict with keys: pdb_id, chains (list of dicts with
        chain_id, sequence, coords).  Returns None on failure.
        """
        cache_path = self.db_dir / f"{pdb_id.lower()}.json"
        if cache_path.exists():
            with open(cache_path) as f:
                return json.load(f)

        pdb_url = f"{RCSB_COORD_URL}/{pdb_id.upper()}.pdb"
        try:
            resp = requests.get(pdb_url, timeout=30)
            resp.raise_for_status()
        except Exception:
            return None

        entry = self._parse_pdb_text(pdb_id, resp.text)
        if entry and entry["chains"]:
            with open(cache_path, "w") as f:
                json.dump(entry, f)
        return entry

    def _parse_pdb_text(self, pdb_id: str, pdb_text: str) -> dict:
        """Extract RNA chain sequences and C3' atom coordinates from PDB text."""
        chains: Dict[str, dict] = {}

        for line in pdb_text.splitlines():
            if not (line.startswith("ATOM") or line.startswith("HETATM")):
                continue

            atom_name = line[12:16].strip()
            resname = line[17:20].strip()
            chain_id = line[21]
            resid_str = line[22:26].strip()

            if resname not in RNA_RESIDUES:
                continue

            if chain_id not in chains:
                chains[chain_id] = {"residues": {}, "chain_id": chain_id}

            resid = int(resid_str) if resid_str.lstrip("-").isdigit() else 0

            if resid not in chains[chain_id]["residues"]:
                chains[chain_id]["residues"][resid] = {
                    "resname": resname,
                    "atoms": {},
                }

            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                chains[chain_id]["residues"][resid]["atoms"][atom_name] = [x, y, z]
            except ValueError:
                continue

        result_chains = []
        for cid, cdata in chains.items():
            sorted_resids = sorted(cdata["residues"].keys())
            sequence = ""
            coords = []
            for rid in sorted_resids:
                res = cdata["residues"][rid]
                one_letter = THREE_TO_ONE.get(res["resname"], "N")
                sequence += one_letter

                # Prefer C3' (backbone), fallback to C1', then P
                atom_coord = None
                for preferred in ["C3'", "C1'", "P"]:
                    if preferred in res["atoms"]:
                        atom_coord = res["atoms"][preferred]
                        break
                if atom_coord is None and res["atoms"]:
                    atom_coord = next(iter(res["atoms"].values()))
                if atom_coord is None:
                    atom_coord = [0.0, 0.0, 0.0]
                coords.append(atom_coord)

            if len(sequence) >= 5:
                result_chains.append({
                    "chain_id": cid,
                    "sequence": sequence,
                    "coords": coords,
                })

        return {"pdb_id": pdb_id.upper(), "chains": result_chains}

    # ------------------------------------------------------------------
    # Build the full template database
    # ------------------------------------------------------------------

    def build_database(
        self,
        max_entries: int = 2000,
        max_resolution: float = 4.0,
        delay: float = 0.1,
    ) -> int:
        """Download RNA structures from PDB and build the local index.

        Returns the number of chains indexed.
        """
        print("Searching RCSB for RNA structures...")
        pdb_ids = self.search_rna_entries(
            max_results=max_entries, max_resolution=max_resolution
        )
        print(f"Found {len(pdb_ids)} RNA entries.")

        new_chains = 0
        for pdb_id in tqdm(pdb_ids, desc="Downloading"):
            if pdb_id in self.index:
                continue
            entry = self.download_entry(pdb_id)
            if entry is None:
                continue

            for chain in entry["chains"]:
                key = f"{pdb_id}_{chain['chain_id']}"
                self.index[key] = {
                    "pdb_id": pdb_id,
                    "chain_id": chain["chain_id"],
                    "sequence": chain["sequence"],
                    "length": len(chain["sequence"]),
                    "coords": chain["coords"],
                }
                new_chains += 1

            if delay > 0:
                time.sleep(delay)

        self._save_index()
        print(f"Database built: {len(self.index)} chains total ({new_chains} new).")
        return len(self.index)

    def _save_index(self):
        with open(self.index_path, "wb") as f:
            pickle.dump(self.index, f)

    # ------------------------------------------------------------------
    # Template search
    # ------------------------------------------------------------------

    def search_templates(
        self,
        query_sequence: str,
        top_k: int = 5,
        min_identity: float = 0.2,
    ) -> List[dict]:
        """Find the best matching templates for a query RNA sequence.

        Uses a fast k-mer identity pre-filter then ranks by full alignment.
        Returns a list of match dicts sorted by identity (descending).
        """
        query_upper = query_sequence.upper()
        query_kmers = _kmer_set(query_upper, k=4)

        candidates = []
        for key, entry in self.index.items():
            tpl_kmers = _kmer_set(entry["sequence"], k=4)
            if not query_kmers or not tpl_kmers:
                continue
            jaccard = len(query_kmers & tpl_kmers) / len(query_kmers | tpl_kmers)
            if jaccard >= min_identity * 0.3:
                candidates.append((key, entry, jaccard))

        candidates.sort(key=lambda x: -x[2])
        candidates = candidates[:top_k * 5]

        results = []
        for key, entry, _ in candidates:
            identity = sequence_identity(query_upper, entry["sequence"])
            if identity >= min_identity:
                results.append({
                    "key": key,
                    "pdb_id": entry["pdb_id"],
                    "chain_id": entry["chain_id"],
                    "template_sequence": entry["sequence"],
                    "template_length": entry["length"],
                    "identity": identity,
                    "coords": entry["coords"],
                })

        results.sort(key=lambda x: -x["identity"])
        return results[:top_k]


# ======================================================================
# Alignment utilities (pure numpy, no external deps)
# ======================================================================

def _kmer_set(seq: str, k: int = 4) -> set:
    return {seq[i:i + k] for i in range(len(seq) - k + 1)} if len(seq) >= k else set()


def sequence_identity(seq_a: str, seq_b: str) -> float:
    """Compute sequence identity via Needleman-Wunsch global alignment.

    Returns the fraction of aligned positions that match.
    """
    alignment = needleman_wunsch(seq_a, seq_b)
    if alignment["aligned_length"] == 0:
        return 0.0
    return alignment["matches"] / alignment["aligned_length"]


def needleman_wunsch(
    seq_a: str,
    seq_b: str,
    match_score: int = 2,
    mismatch_score: int = -1,
    gap_penalty: int = -2,
) -> dict:
    """Global pairwise alignment via Needleman-Wunsch.

    Returns dict with keys: aligned_a, aligned_b, matches, aligned_length,
    alignment_map_a_to_b (maps positions in seq_a to positions in seq_b, or -1 for gaps).
    """
    n, m = len(seq_a), len(seq_b)
    dp = np.zeros((n + 1, m + 1), dtype=np.int32)
    dp[0, :] = np.arange(m + 1) * gap_penalty
    dp[:, 0] = np.arange(n + 1) * gap_penalty

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = match_score if seq_a[i - 1] == seq_b[j - 1] else mismatch_score
            dp[i, j] = max(
                dp[i - 1, j - 1] + s,
                dp[i - 1, j] + gap_penalty,
                dp[i, j - 1] + gap_penalty,
            )

    # Traceback
    aligned_a, aligned_b = [], []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            s = match_score if seq_a[i - 1] == seq_b[j - 1] else mismatch_score
            if dp[i, j] == dp[i - 1, j - 1] + s:
                aligned_a.append(seq_a[i - 1])
                aligned_b.append(seq_b[j - 1])
                i -= 1
                j -= 1
                continue
        if i > 0 and dp[i, j] == dp[i - 1, j] + gap_penalty:
            aligned_a.append(seq_a[i - 1])
            aligned_b.append("-")
            i -= 1
        else:
            aligned_a.append("-")
            aligned_b.append(seq_b[j - 1])
            j -= 1

    aligned_a.reverse()
    aligned_b.reverse()

    matches = sum(a == b and a != "-" for a, b in zip(aligned_a, aligned_b))
    aligned_length = sum(a != "-" or b != "-" for a, b in zip(aligned_a, aligned_b))

    # Build position mapping: query pos -> template pos (-1 if gapped)
    a_pos, b_pos = -1, -1
    map_a_to_b = {}
    for a_char, b_char in zip(aligned_a, aligned_b):
        if a_char != "-":
            a_pos += 1
        if b_char != "-":
            b_pos += 1
        if a_char != "-" and b_char != "-":
            map_a_to_b[a_pos] = b_pos

    return {
        "aligned_a": "".join(aligned_a),
        "aligned_b": "".join(aligned_b),
        "matches": matches,
        "aligned_length": aligned_length,
        "alignment_map_a_to_b": map_a_to_b,
    }
