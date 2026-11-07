# Source inventory and inconsistency register

Inventory date: 2026-11-07. Historical files were read from `/home/henric/Projekte/ITP_2023` and left unchanged. Working copies of the three CSVs, `input_data.py`, `ML_model.py`, and the DOCX are under `data/original/`.

## Files and checksums

| File | SHA-256 | Finding |
|---|---|---|
| `building_data.csv` | `7c4168896bbcf7d62554244754ee7fc8e3829d195e2a9c197badb2114aa79895` | 30 rows, 10 numeric input columns |
| `processed_data.csv` | `7c4168896bbcf7d62554244754ee7fc8e3829d195e2a9c197badb2114aa79895` | byte-identical to `building_data.csv`; no processing is visible |
| `output_values.csv` | `f77ec63253a88a9e2db80851125181171f81a1431bf9427aa78c81fc3ce8bf03` | 30 rows, 4 numeric output columns |
| `input_data.py` | `40a0cc4c4737c4640ce104d7951c09aa3b06e50ef9a0807c1fe2cfea6274e453` | hard-coded arrays exactly reproduce both CSV sequences |
| `ML_model.py` | `879691948ebff13c1909edd214bd6237c4d6fcd01e0872a086f9c37c54c54820` | later ML reference; calls ordered input/output frames |
| report DOCX | `3ac1a3d8d57797ba56283cf5d3d9222af25875d76a114e5711f9e01b99e63901` | report catalog, 30 scenarios, outputs, and optimization constraints |

There are no missing values or exact duplicate rows in the three CSVs. No CSV has a record ID. The Python arrays establish the intended **later-code** positional pairing. They do not resolve conflict with the report's physical scenario table.

## Catalog documented in report VIII.1

- Slabs: 130, 150, 200 mm.
- Ceilings: 11, 14, 16.5 mm (titles `Panels_10`, `Panels_13`, `Panels_15`).
- External and internal walls: 100, 150, 200, 250 mm.
- Windows: 1.5, 1.8, 2.1 m², each with one or two glass layers (six named variants).
- Primary doors: 3.52, 3.96, 4.4 m².
- Secondary doors: 1.26, 1.68 m².

The resulting independent product has 5,184 combinations.

## Report versus CSV inputs

The report's scenario-index table agrees with its numerical x1–x8 table. The CSV/code disagree with that report table in rows **9 and 15–30** (row 14 agrees). Affected fields by row are:

| Row | Conflicting fields |
|---:|---|
| 9 | x6 |
| 15 | x6 |
| 16 | x5 |
| 17 | x3, x4, x6 |
| 18 | x3, x4, x5, x6, x8 |
| 19 | x7, x8 |
| 20 | x1, x5, x6 |
| 21 | x8 |
| 22 | x6, x8 |
| 23 | x5, x6, x7, x8 |
| 24 | x5, x7, x8 |
| 25 | x8 |
| 26 | x4, x6, x7 |
| 27 | x3, x4, x5, x6, x7, x8 |
| 28 | x4, x5 |
| 29 | x2, x7 |
| 30 | x8 |

The output CSV sequence matches the output values shown in the report. Therefore the minimum output row is known, but rows 9 and 15–30 do not have an unambiguous physical input configuration across sources.

## Additional window properties

The report scenario table contains only window area and layer count. CSV/code add `window_g_value` and `window_u_value`. In observed CSV rows, `(g, U)` is either `(0.70, 2.80)` or `(0.87, 3.01)`. Both pairs occur with both one and two layers. Thus these properties are **not a function of glass-layer count alone** in the supplied data. No source maps either pair to the six named report window variants.

## Constraints transcribed from report X.1

With `H_story=3600 mm`, `L3=66950 mm`, `L4=47950 mm`, and `A_floor=140.53×10^6 mm²`:

1. `H_story / 16 <= x3`.
2. `H_story / 32 <= x4`.
3. `(x3*L3 + x4*L4) / A_floor <= 0.15`.
4. `sum(x5) / A_floor <= 1/4` (the report does not provide enough opening-instance information to evaluate `sum(x5)` from one catalog window choice).

Under the current transcription, the discrete report catalog is empty. The minimal catalog-relative contradiction is already `{exterior-wall minimum, wall-area ratio}`: x3 must be 250 mm, but even the smallest x4=100 mm gives ratio 0.1532235 > 0.15. This explains the program status of all 5,184 candidates. It does **not** establish physical impossibility: formula semantics, reference planes, and nominal versus structural thickness require independent confirmation.

The report's PSO used continuous bounds x3 `[100,400]`, x4 `[100,300]`, x5 `[1.2,2.2]`, with x1, x2, x6, x7, x8 fixed. At the published rounded result `(291.5,112.4,1.2)`, constraints 2 and 3 fail under the transcription. The squared wall-ratio violation `0.00074123` reproduces the displayed report penalty `7.42×10^-4`, confirming that this was a penalized—not strictly feasible—result. It is not a discrete-catalog result or direct physical simulation.
