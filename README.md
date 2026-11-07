# ITP 2023 – Deterministic Building Energy Optimization

Reproducible Python 3.11+ baseline without machine learning or randomized search.

## About

This research software investigates whether the ITP 2023 building-energy optimization problem can be solved transparently with deterministic methods and direct physical simulation instead of machine-learning surrogate models and randomized optimization.

It provides auditable source-data validation, explicit three-state admissibility checks, deterministic catalog enumeration, exact evaluation of observed simulations, constraint and source reconciliation, reproducible command-line workflows, and a guarded EnergyPlus interface. The current result is deliberately inconclusive: Phase A and A.1 are implemented, while physical optimization remains blocked by conflicting historical inputs, an unresolved constraint interpretation, and missing verified EnergyPlus model and weather files.

The project does not claim that deterministic optimization is superior to machine learning. It establishes a reproducible framework for testing that hypothesis against the same physical reference, constraints, and computational budget.

## Current evidence status

The historical sources were found in `/home/henric/Projekte/ITP_2023` and copied unchanged into `data/original/`. The original directory was not modified. The later Python arrays verify the intended CSV row order, but the report input table conflicts with CSV rows 9 and 15–30. See `docs/source_inventory.md`.

## Install and run

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'
.venv/bin/pytest
.venv/bin/itp-opt validate
.venv/bin/itp-opt analyze
.venv/bin/itp-opt enumerate
.venv/bin/itp-opt reconcile
.venv/bin/itp-opt optimize --backend observed
.venv/bin/itp-opt verify --config config/example.yaml
```

Global options such as `--data-dir` and `--results-dir` precede the command. Exit codes are `0` for success, `2` for invalid/unverified data, `3` for missing EnergyPlus prerequisites, and `4` for a non-evaluable optimization or unverified model mapping.

## Scientific scope

- `analyze` describes only observed rows and does not predict unknown configurations.
- `enumerate` deterministically creates the documented `3×3×4×4×6×3×2 = 5184` combinations. Under the current transcription all violate at least one checkable report wall constraint; this is not treated as proof of physical impossibility. The total-window-area constraint is additionally unresolved.
- `ObservedDataEvaluator` performs exact lookups only and rejects unknown or conflicting configurations.
- `EnergyPlusEvaluator` verifies prerequisites but intentionally refuses to claim simulation until configuration-to-model mappings are verified.
- A minimum over observed cases is not a global optimum over the building design space.

See `docs/methodology.md` and `results/research_report.md`.

If Debian's `venv`/`pip` packages are unavailable, `scripts/bootstrap_pytest.sh` creates an isolated test environment under `/tmp/opencode` without modifying system packages.
