# AGENTS.md

## Cursor Cloud specific instructions

This is a Python-based Kaggle competition pipeline (Stanford RNA 3D Folding 2) for predicting 3D atomic coordinates of RNA molecules.

### Running the pipeline

The single entry point is `scripts/run_pipeline.py` with subcommands: `train`, `validate`, `predict`, `submit`. See `README.md` for project structure and `configs/` for YAML config files.

```bash
python scripts/run_pipeline.py train --config configs/train_config.yaml
```

Without real Kaggle competition data in `data/raw/`, the training pipeline automatically falls back to dummy/random data, which is sufficient for validating pipeline mechanics end-to-end.

### Key caveats

- **No GPU on Cloud VMs**: PyTorch runs on CPU. Training with dummy data completes in seconds; real data training will be slow.
- **No automated tests or linting config**: The repository has no `pytest`, `flake8`, `ruff`, or `pyproject.toml` configured. Use `python -c "import <module>"` to verify module health, or run the pipeline itself as a smoke test.
- **No external services required**: This is a self-contained ML pipeline. No databases, Docker, or API services are needed.
- **Data directories**: `data/{raw,processed,external}` must exist. The update script creates them if missing.
- **Iteration protocol**: Follow `.cursor/rules/kaggle-iteration.mdc` for the 6-phase iteration cycle when making pipeline changes.
