# ITP Deterministic – Reproducible Building-Energy Research Audits

Reproducible Python 3.11+ audits of the 2023 research record and the published 2026
journal article, without claiming reproduction of machine learning or randomized search.

## About

This research software independently audits the mathematical, numerical and documentary
consistency of a building-energy optimization research record: the historical ITP 2023
training report and the related journal article published in 2026. The two sources are kept
separate because they report different geometry constants, datasets, neural-network
configurations and optimization results.

The project provides source provenance and checksum records, exact `Decimal` constraint and
penalty calculations, domain-specific feasibility proofs, rounding-aware Table 14 audits,
historical source reconciliation, deterministic catalog enumeration, explicit three-state
admissibility checks, reproducible command-line workflows, and a guarded EnergyPlus
interface.

It does not claim reproduction of ANN training or CPSO runs, verification of optimality,
physical impossibility of the building, superiority over machine learning, or validation of
the original simulation model. Physical optimization remains blocked by missing verified
model/weather artifacts and unresolved source mappings. MPRS publication status remains
`HOLD` pending independent scientific review.

## Current evidence status

The historical sources were found in `/home/henric/Projekte/ITP_2023` and copied unchanged into `data/original/`. The original directory was not modified. The later Python arrays verify the intended CSV row order, but the report input table conflicts with CSV rows 9 and 15–30. See `docs/source_inventory.md`.

Phase A.3 independently reconstructs the published PSO penalty terms. It confirms the discrete catalog MUS `{c1,c3}` and a nonempty continuous `c1`–`c3` region, corrects the penalty obtained from printed `x4=112.4`, and treats inversely calculated coordinates as conditional rather than recovered historical values. See `docs/pso_rounding_analysis.md`.

Phase A.4 separately audits the published 2026 journal article using its new geometry constants. The full 2026 wall-constraint system is infeasible even over the unrestricted continuous domain, while `{c1,c3}` alone is feasible only through negative `x4` and is therefore not universally contradictory. It also audits the printed CPSO candidate and Table 14 arithmetic without reproducing ANN training or CPSO. See `docs/published_2026_feasibility.md`. MPRS remains `HOLD`.

Phase A.4.1 strengthens the Table 14 check by requiring all displayed penalty evidence to arise from one common hidden coordinate pair. It finds run 1 jointly inconsistent as printed, runs 2 and 3 conditionally compatible, and the hypothesized `2078.988` transcription conditionally compatible but unverified. The audit implementation is `READY_FOR_REVIEW`; this does not change the MPRS `HOLD` decision. See `docs/phase_a4_1_joint_penalty_review.md`.

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
python3 scripts/verify_pso_penalties.py
python3 scripts/verify_published_2026.py
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
