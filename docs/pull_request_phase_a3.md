# Phase A.3: Reconstruct PSO penalty rounding

## Summary

- independently reconstructs the report's PSO penalty terms with `decimal.Decimal`;
- confirms the unique catalog-relative MUS `{c1,c3}` by enumeration and elementary inequalities;
- confirms a nonempty continuous `c1`–`c3` triangle analytically and by independent polygon clipping;
- corrects the claim that printed `x4=112.4` reproduces reported `p2=2.42e-7`;
- labels inverse coordinates as conditional, not recovered optimizer state;
- confirms robust c3 violation across the printed-coordinate rounding box;
- preserves `NON_EVALUABLE` for the window condition;
- records that the requested v0.2 LaTeX manuscript and complete MPRS catalog are unavailable;
- retains the MPRS decision `HOLD`.

## Key numbers

- `p2(112.4) = 7.9152999582e-7`
- conditionally inferred `x4 = 112.4446845292 mm`
- `p3(291.5,112.4) = 7.4122997552e-4`
- `p3(291.5,inferred x4) = 7.4206040895e-4`
- conditionally joint-compatible `x3 = 291.4964396198 mm`

The inferred coordinates are not claimed as historical internal PSO coordinates.

## Tests

- Phase A/A.1 baseline: 14 passed
- Complete suite: 23 passed
- New Phase A.3 tests: 9
- Failures: 0

## Manuscript and review status

`ITP_Feasibility_Audit_v0.2.tex` was not found under `/home/henric`. No incomplete v0.2.1 or PDF was fabricated. Publication rights, authorship approval, engineering interpretation, and independent peer review remain unresolved; release status stays `HOLD`.
