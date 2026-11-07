# Research report – deterministic Phase A

## Executive result

The 30 historical output rows have been imported and analyzed without prediction. The smallest recorded energy requirement is **21,489.245 (source unit unverified), row 30**. This is an empirical row minimum, not a global building optimum. Its physical configuration is disputed:

- CSV/later Python: `[200, 11, 250, 200, 1.5, 1, 3.96, 1.26]`, plus `(g,U)=(0.70,2.80)`;
- 2023 report scenario and numerical tables: `[200, 11, 250, 200, 1.5, 1, 3.96, 1.68]`.

The output sequence agrees across report, CSV, and code, while report and CSV input rows 9 and 15–30 conflict. Accordingly, the output minimum is established but its exact input configuration is not.

## 1. Observed solutions

| Objective | Minimum | Row | CSV/later-code configuration note |
|---|---:|---:|---|
| Energy requirement | 21,489.245 | 30 | x8 conflicts with report |
| Energy losses | 1,220.4 | 29 | x2 and x7 conflict with report |
| Heat gain | 1,372.777 | 29 | x2 and x7 conflict with report |
| CO₂ emission | 232.734 | 30 | x8 conflicts with report |

Means over 30 rows are 23,369.602 energy requirement, 2,097.431 energy losses, 2,633.982 heat gain, and 252.446 CO₂ emission. Units of these outputs are not stated reliably in the supplied CSV/report text and remain unverified.

For all four minimized objectives together, rows 21, 29, and 30 form the observed Pareto front under the later Python/CSV pairing. This is empirical dominance only. Pearson associations are recorded in `observed_summary.json`; because only 30 jointly varied, non-factorial cases exist, they are not causal sensitivities.

## 2. Additional physical evaluations

**Zero.** No IDF/epJSON, EPW, or EnergyPlus executable is present. More importantly, no verified mapping exists from catalog choices to EnergyPlus model objects and output meters. The backend therefore returns `NON_EVALUABLE` rather than presenting a mock as simulation.

## 3. Numerical and temporal effort

- Descriptive analysis of 30 rows: about **0.141 s** in the current Python 3.13.5 environment.
- Generation and validation of 5,184 candidates: about **0.348 s**.
- Physical simulation time: not measurable because prerequisites are absent.

These are single observed wall-clock measurements, not performance guarantees.

## 4. Deterministic reproducibility

Catalog order, constraints, exact lookup, grid order, and lexicographic tie-breaking are deterministic. Input SHA-256 checksums are in `validation_report.json`. Eleven Phase-A tests pass under the dependency-free fallback runner. The host lacks `pytest`, `pip`, and functional `venv` support, so the same pytest-compatible tests could not be invoked through pytest in this environment.

## 5. Search-space constraints

The report specifies:

1. `3600/16 <= x3`;
2. `3600/32 <= x4`;
3. `(66950*x3 + 47950*x4)/(140.53e6) <= 0.15`;
4. `sum(x5)/A_floor <= 1/4`.

Under the current transcription, the discrete report catalog has no configuration satisfying the checkable conditions. The minimal contradiction is already the exterior-wall minimum together with the wall-area ratio: x3 must be 250 mm, but even x4=100 mm gives 0.1532235 > 0.15. All 5,184 combinations are therefore programmatically `INADMISSIBLE`. This is a catalog/formulation conflict, not proof of physical impossibility; engineering semantics, units, and reference planes still require confirmation.

## 6. Justified global claims

No global building optimum is justified. The observed minimum is only over 30 disputed mappings. The finite catalog's admissible subset is empty only under the current documented interpretation, so that formulation has no feasible minimizer. The published continuous PSO point violates the reconstructed interior-wall and wall-ratio conditions and is explicitly penalized; it is neither a feasible discrete-catalog result nor direct physical simulation.

## 7. Missing information

- authoritative correction for report/CSV row conflicts;
- output units and precise output definitions;
- mapping of g/U pairs to named windows (both pairs occur with both layer counts);
- number and area of window instances needed for `sum(x5)`;
- EnergyPlus model, weather file, simulator/version, object mapping, meters, and reference result.

## 8. Is machine learning necessary?

The evidence is currently **insufficient to decide**. ML is unnecessary for finding the minimum among the 30 known outputs, and deterministic enumeration is computationally trivial. But the catalog is infeasible under the stated constraints and no direct simulator is available, so direct deterministic physical optimization cannot yet be compared fairly against the historical surrogate. A valid comparison requires corrected source mappings, a nonempty admissible space, the same physical model, and comparable simulation budgets.

See `docs/source_inventory.md` for the detailed inconsistency register.
