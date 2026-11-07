# Phase A.3 – Independent PSO Penalty Reconstruction

## Review scope

This review independently recomputes the penalty terms printed in the 2023 source report. It uses Python's `decimal.Decimal` with 50-digit working precision. It does not train a model, execute PSO, infer EnergyPlus results, or claim access to the optimizer's internal coordinates.

The source report is the primary evidence for formulas and printed numbers. The DeepSeek observation supplied in the work order is treated as a hypothesis to test, not as evidence.

## Inputs and provenance

| Quantity | Printed value | Status |
|---|---:|---|
| `H` | 3600 mm | source-reported |
| `L3` | 66950 mm | source-reported |
| `L4` | 47950 mm | source-reported |
| `A` | 140530000 mm² | source-reported |
| `x3` | 291.5 mm | rounded published PSO coordinate |
| `x4` | 112.4 mm | rounded published PSO coordinate |
| `x5` | 1.2 m² | rounded published PSO coordinate |
| `p2` | `2.42e-7` | rounded published penalty component |
| `p3` | `7.42e-4` | rounded published penalty component |
| total penalty | 742.210 | rounded published run-1 result |

The report's normalized squared penalty branches are reconstructed as

```text
p1 = max(0, H/(16*x3) - 1)^2
p2 = max(0, H/(32*x4) - 1)^2
p3 = max(0, (L3*x3 + L4*x4)/A - 0.15)^2
P  = 10^6 * (p1 + p2 + p3 + p4)
```

The fourth term cannot be reconstructed reliably.

## A. Minimal infeasible catalog subset — CONFIRMED

Complete enumeration of all 16 `(x3,x4)` wall pairs gives:

| Constraint subset | Feasible wall pairs |
|---|---:|
| none | 16 |
| `{c1}` | 4 |
| `{c2}` | 12 |
| `{c3}` | 9 |
| `{c1,c2}` | 3 |
| `{c1,c3}` | 0 |
| `{c2,c3}` | 6 |
| `{c1,c2,c3}` | 0 |

Therefore the unique inclusion-minimal infeasible subset is `{c1,c3}`.

An independent elementary proof reaches the same result. In the wall catalog `{100,150,200,250}`, `c1` forces `x3=250`. For fixed `x3=250`, the left side of `c3` is minimized by catalog minimum `x4=100`, yet

```text
(66950*250 + 47950*100) / 140530000
  = 0.1532235109940938... > 0.15.
```

Every proper subset is feasible: `(250,100)` witnesses `{c1}`, `(100,100)` witnesses `{c3}`, and any catalog pair witnesses the empty subset. The other two-constraint subsets are also feasible, so no second MUS exists.

This is a statement about the documented discrete wall catalog only. Multiplication by the remaining 324 independent catalog choices explains the 5,184-building result, but does not add another wall contradiction.

## B. Continuous feasible region — CONFIRMED

Within `[100,400] × [100,300]`, constraints `c1`–`c3` define a nonempty triangle. Its analytically derived vertices are:

```text
(225, 112.5)
(225, 125.4588112617309697601668404588...)
(234.2811799850634802091112770724..., 112.5)
```

A separate Sutherland–Hodgman half-plane clipping calculation recovers the same three vertices. All satisfy `c1`–`c3` within Decimal precision.

This proves only continuous feasibility for the three wall conditions. It does not establish discrete catalog feasibility or full building admissibility; in particular, the window condition remains unresolved.

## C. Interior-wall penalty — CORRECTED / CONDITIONAL

Using the printed coordinate exactly:

```text
p2(112.4) = (112.5/112.4 - 1)^2
           = 7.915299958207216...e-7.
```

It does not equal the reported `2.42e-7`. The discrepancy confirms the issue raised by DeepSeek independently.

On the violated branch, solving for `x4` gives

```text
x4 = 112.5 / (1 + sqrt(p2)).
```

For printed `p2=2.42e-7`:

```text
x4 = 112.444684529170536...
112.5 - x4 = 0.055315470829464... mm.
```

This value rounds to `112.4` at one decimal place. It is **inferred**, not a recovered original coordinate.

Conditionally assuming `2.42e-7` was rounded to three significant digits, its interval `[2.415e-7,2.425e-7)` maps approximately to:

```text
x4 in (112.444627442687..., 112.444741674716...]
```

The corresponding violation is approximately 0.055258–0.055373 mm. This interval accounts only for print rounding, not formula, transcription, floating-point, or optimizer-state uncertainty.

## D. Wall-area penalty — CONFIRMED and robust

With both printed coordinates:

```text
p3(291.5,112.4) = 7.412299755182636...e-4.
```

With printed `x3=291.5` and the `p2`-inferred `x4`:

```text
p3 = 7.420604089466379...e-4.
```

Both are positive and confirm violation of `c3`. Moreover, the smallest wall ratio throughout the conventional one-decimal rounding box `x3∈[291.45,291.55)`, `x4∈[112.35,112.45)` remains above 0.15. The infeasibility conclusion is therefore insensitive to the displayed-coordinate rounding.

The second value rounds to the report's displayed `7.42e-4`; the first would normally round to `7.41e-4` at three significant digits. This supports, but does not prove, hidden coordinate precision.

## E. Total penalty — CONDITIONAL

Assuming `p4=0`:

| Coordinate interpretation | Reconstructed total |
|---|---:|
| printed `x3=291.5`, `x4=112.4` | 742.021505514084... |
| printed `x3=291.5`, `p2`-inferred `x4` | 742.302408946638... |
| reported | 742.210 |

Neither partial reconstruction equals the reported total. If one additionally assumes the reported total and `p2` center are exact, `p1=p4=0`, and the same formulas/factor, joint inversion gives:

```text
x3 = 291.496439619779...
x4 = 112.444684529171...
```

Both round to the printed coordinates and reproduce 742.210 at Decimal precision. This is merely one conditionally compatible pair, not recovery of the actual PSO state.

The printed component intervals are broad enough to include the printed total: under nearest rounding, `p2+p3` permits a scaled sum from approximately 741.7415 to 742.7425. Numerical agreement within those print intervals cannot identify internal coordinates.

## F. Window condition — NOT_VERIFIABLE

The number of windows, assignment of the selected window area to openings, meaning of `sum(x5)`, and conversion between x5 in m² and floor area in mm² are not documented sufficiently. The condition remains `NON_EVALUABLE`. A printed penalty component of zero reports optimizer behavior; it is not independent evidence that the physical or mathematical condition was correctly evaluated.

## Claim register

| Claim | Result | Reason |
|---|---|---|
| 17 report/code input conflicts | CONFIRMED | Existing row-level reconciliation; unchanged by this review |
| 5,184 deterministic catalog configurations | CONFIRMED | Exact finite product and enumeration |
| Unique catalog MUS `{c1,c3}` | CONFIRMED | Complete subset enumeration plus elementary proof |
| Continuous `c1`–`c3` region is nonempty | CONFIRMED | Analytic triangle and independent clipping |
| Printed `x4=112.4` produces printed `p2` | CORRECTED | Exact recomputation disagrees |
| `x4≈112.444685` is compatible with printed `p2` | CONDITIONAL | Depends on formula branch and print-rounding assumptions |
| `x4≈112.444685` is the original PSO coordinate | NOT_VERIFIABLE | Internal optimizer precision/state unavailable |
| Published point violates `c3` | CONFIRMED | Robust under printed-coordinate rounding |
| Printed penalty values uniquely recover internal coordinates | NOT_VERIFIABLE | Rounded values admit intervals and multiple compatible states |
| Window constraint was fulfilled | NOT_VERIFIABLE | Required source information is missing |

## Reproduction

```bash
python3 scripts/verify_pso_penalties.py
pytest tests/test_pso_penalty_reconstruction.py
```

Machine-readable values are written to `results/pso_penalty_reconstruction.json`.
