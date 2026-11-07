# Phase A.4 review record

## Source-control scope

- Base: current `origin/main` at `f63ab6c46967ea5aebd95524f97950f99770aa1e`.
- Review branch: `review/published-2026-feasibility`.
- Existing published PDF retained unchanged; no source data, 2023 result, or ITP working
  paper is changed by this phase.

## Test record

Baseline attempts and result before implementation:

1. `python -m pytest`: command unavailable because `python` is not installed.
2. `python3 -m pytest`: environment lacked `pytest`.
3. `scripts/bootstrap_pytest.sh` created the documented isolated environment under
   `/tmp/opencode`; `/tmp/opencode/itp-pytest-venv/bin/pytest` then passed **23 tests** in
   0.95 s.

Phase A.4 adds **9** independent tests for unrestricted and domain-specific feasibility,
threshold/area boundaries, exact candidate residuals, one-decimal robustness, Table 14
rounding intervals, component precision, constant separation, deterministic JSON and
`NON_EVALUABLE` window semantics. The final complete suite passed **32 tests in 1.01 s**
with no failures. Two consecutive verification-script runs produced byte-identical JSON.

## Reproduction

```bash
/tmp/opencode/itp-pytest-venv/bin/python scripts/verify_published_2026.py
/tmp/opencode/itp-pytest-venv/bin/pytest
```

The script verifies the local PDF SHA-256 before replacing
`results/published_2026_audit.json`. Output contains no timestamps and is byte-reproducible.

## Unresolved questions

- What exact continuous bounds and coordinate precision were used in the 2026 CPSO?
- What opening count, `sum(x5)` mapping and unit conversion define the window condition?
- Why do the geometry lengths and formula floor area differ between source versions and
  from the 2023 descriptive 113 m² area?
- Can the complete 170-row dataset, split seeds, trained ANN artifacts, CPSO logs, TerMus
  PLUS version/model and actual climate input be archived?
- Is Table 14's third penalty-component row intended to say run 3?
- What unrounded values underlie the run-1 `F`, `Phi`, and `P` inconsistency?
- What permission or other reviewed legal basis permits redistribution of each historical
  report, data, and source file?
- Does the intended publication use of the journal PDF and reused article content satisfy
  CC BY-NC 4.0 attribution, notice, change-indication, and noncommercial conditions?

Original Phase A.4 recommendation: `HOLD` until the joint extension; MPRS remains `HOLD`.

## Phase A.4.1 extension

The joint-penalty extension starts from commit
`e2ea81a251e39ce92d18e3bee8fbc3bdfbdc22fc`; its unchanged baseline is **32 passed**.
It adds nine tests covering violated-branch inversion, significant-digit intervals, joint
coordinate intersections, monotonicity-certified bounds, `p3`, nonnegative `p4`, all three
run classifications, the `2078.988` hypothesis and deterministic output. See
`docs/phase_a4_1_joint_penalty_review.md` and
`results/published_2026_joint_penalty.json`.

The final complete suite passed **41 tests in 1.43 s** with no failures. Two consecutive
runs produced byte-identical main and joint JSON outputs.

Phase A.4.1 decision: `READY_FOR_REVIEW`. This does not change the MPRS `HOLD` decision.

Rights clearance remains a separate mandatory publication gate. See
`THIRD_PARTY_MATERIALS.md`; the repository MIT license neither resolves historical-source
permissions nor replaces the article's CC BY-NC 4.0 terms.
