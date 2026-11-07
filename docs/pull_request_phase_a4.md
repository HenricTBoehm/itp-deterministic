# Phase A.4: audit published 2026 feasibility

## Summary

- Independently reconstruct the constraints in the published 2026 journal article using
  separate constants and 60-digit `Decimal` arithmetic.
- Distinguish unrestricted, nonnegative, and documented catalog domains.
- Audit the printed CPSO candidate, coordinate-rounding robustness, and all Table 14
  decompositions.
- Provide a source-grounded 2023–2026 crosswalk and claim register.
- Add a Phase A.4.1 joint-consistency audit requiring one common hidden coordinate pair for
  all displayed penalty evidence.

## Key findings

- The full 2026 wall-constraint system has no continuous feasible region, even over R².
- `{c1,c3}` alone is feasible over R² only with negative `x4`; it is infeasible for
  nonnegative thicknesses and the catalog.
- All three reconstructable constraints at `(223.7,112.4,1.9)` are violated robustly across
  ordinary rounding intervals.
- Run 1's printed `F=Phi+P` discrepancy is not explainable by ordinary three-decimal
  rounding; runs 2 and 3 remain conditionally compatible with hidden digits.
- Window feasibility remains `NON_EVALUABLE`; ANN training, CPSO and optimality are not
  reproduced.
- Joint interval analysis finds run 1 `CONFIRMED_INCONSISTENCY` as printed, while runs 2
  and 3 are `CONDITIONALLY_COMPATIBLE`. The `2078.988` run-1 transcription hypothesis is
  conditionally compatible but is not adopted as a correction.

## Verification

- Source PDF: 31 pages, SHA-256
  `49a72ad4f46f58ff4257714e075e54926ffa039b1878c3fecd7dacff57ec174b`.
- Original Phase A.4 baseline/final: 23/32 passed.
- Phase A.4.1 baseline/final: 32/41 passed.
- Deterministic JSON verified byte-identical across consecutive runs.

## Decision

Phase A.4.1 is `READY_FOR_REVIEW`. MPRS remains `HOLD` pending independent scientific
review.
