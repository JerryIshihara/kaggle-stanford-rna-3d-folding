"""
Local test for SUB015 notebook logic.
Runs TBM pipeline (NO Protenix, NO GPU) on 3 mock RNA sequences.
Validates the submission CSV output.
"""
import json
import os
import sys
import tempfile
import textwrap

# ── Create temp workspace ────────────────────────────────────────────────────
TMP = tempfile.mkdtemp(prefix="sub015_test_")
print(f"Workspace: {TMP}")

# ── Create mock competition data ─────────────────────────────────────────────
import numpy as np
import pandas as pd

np.random.seed(42)

TRAIN_SEQS = [
    ("R001", "AUGCAUGCAUGCAUGCAUGC"),
    ("R002", "GCGCGCGCGCGCGCGCGCGC"),
    ("R003", "UUUAAAAGGGGCCCCUUUAAA"),
    ("R004", "AUGCUAGCUAGCUAGCUAGCU"),
    ("R005", "GCAUGCAUGCAUGCAUGCAUG"),
]

TEST_SEQS = [
    ("T001", "AUGCAUGCAUGCAUGCAUGG"),   # similar to R001 → should get template
    ("T002", "GCGCGCGCGCGCGCGCGCGG"),   # similar to R002 → should get template
    ("T003", "AAAAAAAAAAAAAAAAAAAAAA"),  # dissimilar → fallback
]

# Train sequences CSV
train_seq_df = pd.DataFrame(TRAIN_SEQS, columns=["target_id", "sequence"])
train_seq_path = f"{TMP}/train_sequences.csv"
train_seq_df.to_csv(train_seq_path, index=False)

# Train labels CSV — real competition format: one row per residue,
# columns x_1,y_1,z_1 (sample 1 coords). ID = "{target_id}_{resid}"
label_rows = []
N_SAMPLE = 5
for tid, seq in TRAIN_SEQS:
    seq_len = len(seq)
    coords_s1 = np.random.randn(seq_len, 3) * 10  # only sample 1 needed for TBM
    for res_idx in range(seq_len):
        row = {
            "ID": f"{tid}_{res_idx+1}",
            "resid": res_idx + 1,
            "resname": seq[res_idx],
        }
        # Add all N_SAMPLE coord columns
        for s in range(1, N_SAMPLE + 1):
            c = np.random.randn(3) * 10
            row[f"x_{s}"] = c[0]
            row[f"y_{s}"] = c[1]
            row[f"z_{s}"] = c[2]
        label_rows.append(row)

train_lbl_df = pd.DataFrame(label_rows)
train_lbl_path = f"{TMP}/train_labels.csv"
train_lbl_df.to_csv(train_lbl_path, index=False)

# Test sequences CSV
test_seq_df = pd.DataFrame(TEST_SEQS, columns=["target_id", "sequence"])
test_seq_path = f"{TMP}/test_sequences.csv"
test_seq_df.to_csv(test_seq_path, index=False)

output_path = f"{TMP}/submission.csv"

# Validation data (small, different sequences)
VAL_SEQS = [
    ("V001", "AUGCAUGCAUGCAUGCAUGCAA"),
    ("V002", "GCGCGCGCGCGCGCGCGCGCCC"),
]
val_seq_df = pd.DataFrame(VAL_SEQS, columns=["target_id", "sequence"])
val_seq_path = f"{TMP}/validation_sequences.csv"
val_seq_df.to_csv(val_seq_path, index=False)

val_label_rows = []
for tid, seq in VAL_SEQS:
    seq_len = len(seq)
    for res_idx in range(seq_len):
        row = {
            "ID": f"{tid}_{res_idx+1}",
            "resid": res_idx + 1,
            "resname": seq[res_idx],
        }
        for s in range(1, N_SAMPLE + 1):
            c = np.random.randn(3) * 10
            row[f"x_{s}"] = c[0]
            row[f"y_{s}"] = c[1]
            row[f"z_{s}"] = c[2]
        val_label_rows.append(row)
val_lbl_df = pd.DataFrame(val_label_rows)
val_lbl_path = f"{TMP}/validation_labels.csv"
val_lbl_df.to_csv(val_lbl_path, index=False)

print(f"Created mock data: {len(TRAIN_SEQS)} train, {len(VAL_SEQS)} val, {len(TEST_SEQS)} test sequences")
print(f"Train labels: {len(train_lbl_df)} rows")

# ── Set env vars to override paths and disable Protenix ─────────────────────
os.environ["TEST_CSV"]        = test_seq_path
os.environ["TRAIN_CSV"]       = train_seq_path
os.environ["TRAIN_LABELS"]    = train_lbl_path
os.environ["VAL_CSV"]         = val_seq_path
os.environ["VAL_LABELS"]      = val_lbl_path
os.environ["SUBMISSION_CSV"]  = output_path
os.environ["LAYERNORM_TYPE"]  = "torch"
os.environ["RNA_MSA_DEPTH_LIMIT"] = "512"
os.environ["PROTENIX_DISABLE_CUSTOM_OPS"] = "1"
os.environ["NO_FLASH_ATTN"]   = "1"

# ── Extract notebook cells ────────────────────────────────────────────────────
NB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "submissions", "submission_SUB017.ipynb"
)
with open(NB_PATH) as f:
    nb = json.load(f)

def get_cell_src(idx):
    return "".join(nb["cells"][idx]["source"])

# ── Monkey-patch env so IS_KAGGLE=False and USE_PROTENIX=False ───────────────
# Cell 2 has: IS_KAGGLE = True (hardcoded)
# We'll override after executing
exec_globals = {}

# Cell 2 — mode detection (patch IS_KAGGLE to False)
cell2 = get_cell_src(2).replace(
    "IS_KAGGLE = True #bool(os.environ.get(\"KAGGLE_IS_COMPETITION_RERUN\", \"\"))",
    "IS_KAGGLE = False"
).replace(
    "LOCAL_N_SAMPLES = None",
    "LOCAL_N_SAMPLES = 3"
)
print("\n--- Executing Cell 2 (mode detection) ---")
exec(compile(cell2, "<cell2>", "exec"), exec_globals)

# Cell 3 — imports & env
cell3 = get_cell_src(3)
print("--- Executing Cell 3 (imports) ---")
exec(compile(cell3, "<cell3>", "exec"), exec_globals)

# Cell 4 — get_c1_mask function
cell4 = get_cell_src(4)
print("--- Executing Cell 4 (get_c1_mask) ---")
exec(compile(cell4, "<cell4>", "exec"), exec_globals)

# Cell 6 — main cell: override constants and patch ensure_required_files + USE_PROTENIX
cell6 = get_cell_src(5)  # Cell index 5 is the 6th cell (0-based)

# Actually let me check which index has the main code
# Based on earlier analysis, cell index 6 has the main code
cell6 = get_cell_src(6)

# Patch DEFAULT paths to use our temp data
cell6 = cell6.replace(
    'DATA_BASE              = "/kaggle/input/competitions/stanford-rna-3d-folding-2"',
    f'DATA_BASE              = "{TMP}"'
)
cell6 = cell6.replace(
    'DEFAULT_OUTPUT         = "/kaggle/working/submission.csv"',
    f'DEFAULT_OUTPUT         = "{output_path}"'
)
# Patch ensure_required_files to be a no-op (no Protenix checkpoint locally)
cell6 = cell6.replace(
    "def ensure_required_files(root_dir: str) -> None:",
    "def ensure_required_files(root_dir: str) -> None:\n    return  # LOCAL TEST: skip"
)
# Disable Protenix
cell6 = cell6.replace(
    "USE_PROTENIX = True",
    "USE_PROTENIX = False  # LOCAL TEST"
)
# Rename DEFAULT_TRAIN_CSV, DEFAULT_TRAIN_LBLS to match our paths
cell6 = cell6.replace(
    'DEFAULT_TRAIN_CSV      = f"{DATA_BASE}/train_sequences.csv"',
    f'DEFAULT_TRAIN_CSV      = "{train_seq_path}"'
)
cell6 = cell6.replace(
    'DEFAULT_TRAIN_LBLS     = f"{DATA_BASE}/train_labels.csv"',
    f'DEFAULT_TRAIN_LBLS     = "{train_lbl_path}"'
)
cell6 = cell6.replace(
    'DEFAULT_TEST_CSV       = f"{DATA_BASE}/test_sequences.csv"',
    f'DEFAULT_TEST_CSV       = "{test_seq_path}"'
)
cell6 = cell6.replace(
    'DEFAULT_VAL_CSV        = f"{DATA_BASE}/validation_sequences.csv"',
    f'DEFAULT_VAL_CSV        = "{val_seq_path}"'
)
cell6 = cell6.replace(
    'DEFAULT_VAL_LBLS       = f"{DATA_BASE}/validation_labels.csv"',
    f'DEFAULT_VAL_LBLS       = "{val_lbl_path}"'
)

print("--- Executing Cell 6 (main logic) ---")
exec(compile(cell6, "<cell6>", "exec"), exec_globals)

# ── Run main() ───────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("RUNNING main()")
print("="*60)
exec_globals["main"]()

# ── Run sanity check (Cell 9) ────────────────────────────────────────────────
print("\n" + "="*60)
print("RUNNING SANITY CHECK (Cell 9)")
print("="*60)
cell9 = get_cell_src(9).replace(
    'OUTPUT_CSV = "/kaggle/working/submission.csv"',
    f'OUTPUT_CSV = "{output_path}"'
)
exec(compile(cell9, "<cell9>", "exec"), exec_globals)

print("\n" + "="*60)
print("ALL LOCAL TESTS PASSED")
print("="*60)
