# Phase A.1 – Constraint and Source Reconciliation

Status: **Phase A implementation complete / scientific validation pending**.

## Constraint forensics

The formulas were reconstructed from report pages 46–47. Results over 5,184 catalog combinations:

| Condition | ADMISSIBLE | INADMISSIBLE | NON_EVALUABLE |
|---|---:|---:|---:|
| `H_story/16 <= x3` | 1,296 | 3,888 | 0 |
| `H_story/32 <= x4` | 3,888 | 1,296 | 0 |
| `(x3 L3+x4 L4)/A_floor <= 0.15` | 2,916 | 2,268 | 0 |
| `sum(x5)/A_floor <= 1/4` | 0 | 0 | 5,184 |

The unique minimal infeasible subset relative to the discrete catalog is:

`{ exterior-wall minimum, wall-area ratio }`.

The exterior-wall condition forces catalog value x3=250 mm. Even at the smallest catalog x4=100 mm, the wall ratio is 0.1532235 and exceeds 0.15. The interior-wall minimum is not needed to produce the conflict.

This establishes only that the set is empty under the current **catalog, formula, unit, and reference-plane interpretation**. It is not proof that the building is physically impossible. Nominal versus structural thickness and reference geometry remain independent engineering questions.

## Published optimization solution

For report reference `(x3,x4,x5)=(291.5,112.4,1.2)`:

- exterior-wall minimum: pass, margin +66.5 mm;
- interior-wall minimum: fail by 0.1 mm at the rounded published value;
- wall-area ratio: 0.177225539, fail by 0.027225539;
- total-window condition: non-evaluable because `sum(x5)`, opening count, and m²/mm² conversion are underdocumented.

The reconstructed squared wall-ratio violation is `0.00074123`, matching the report's displayed penalty component `7.42×10^-4`. This strongly supports the mathematical transcription of that condition. The reference is a penalized PSO result, not a strictly feasible solution. Its rounded x4 value does not reproduce the displayed second penalty exactly, likely because the optimizer retained undisclosed decimals.

## Source reconciliation

- 13 input rows agree between report and later CSV/Python.
- 17 rows are disputed: row 9 and rows 15–30.
- Report VIII.2 and VIII.3 agree internally.
- `building_data.csv` agrees exactly with the ordered arrays in `input_data.py`.
- Output values agree in sequence across report, CSV, and code, but have no durable record ID.

No source was corrected automatically. Full row-level provenance is in `source_reconciliation.csv` and `source_reconciliation.json`.

## Test environment

An isolated Python 3.11.2 environment was created at `/tmp/opencode/itp-pytest-venv` without changing system Python packages. It contains pytest 9.2.0.

- Original Phase-A suite, unchanged: **11 passed**.
- Complete suite including Phase A.1: **14 passed**.

JUnit evidence is stored in `pytest_phase_a.xml` and `pytest_all.xml`.

## Gate for Phase B

Phase B remains blocked until an authoritative interpretation yields at least one unambiguously specified, admissible configuration and the physical simulation prerequisites exist.
