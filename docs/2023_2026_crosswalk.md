# Source-grounded 2023–2026 crosswalk

This comparison separates changes in the published research model from unresolved source
version differences. The 2023 source is the historical report DOCX (SHA-256
`3ac1a3d8d57797ba56283cf5d3d9222af25875d76a114e5711f9e01b99e63901`), extracted to
plain text with LibreOffice without modifying it. The 2026 source is the published PDF
(SHA-256 `49a72ad4...174b`), extracted with `pdftotext -layout` and visually checked.

| Topic | 2023 report | Published 2026 article | Assessment |
|---|---|---|---|
| Simulation scenarios | 30 rows are listed in the report; historical CSVs also contain 30 rows. | Reports 170 scenarios. Tables 7, 8 and 10 show only scenarios 1–20 and 161–170. | Dataset size changed. The 30 displayed 2026 rows are selected excerpts, **not** the full 170-row dataset. The unavailable middle 140 rows prevent complete row-level verification. |
| ANN architecture | One hidden layer, 50 nodes, LeakyReLU, Adamax learning rate 0.002, batch 2, 24/6 train/test; two stated splits. | One hidden layer, 100 nodes, ReLU, Adamax learning rate 0.002, batch 34; standardization and early stopping; two distinct random 136/34 splits; 10,000 epochs reported. | Material model/training change. Neither training was reproduced here; seeds, complete 2026 data and trained artifacts are unavailable. |
| Building/floor area | Building-description total 113 m²; optimization formula uses `A=140.53e6 mm²`. | Optimization formula uses `A=139.88e6 mm²`; calls it total floor area. | Geometry constant changed, while the relation between descriptive and formula areas remains unresolved. |
| Wall geometry | `L3=66950 mm`, `L4=47950 mm`, `H=3600 mm`. | `L3=99000 mm`, `L4=45920 mm`, `H=3600 mm`. | Research-model geometry changed. Source files do not establish whether this reflects a revised model, measurement convention, or source version. |
| Constraints | Same four printed forms: two thickness minima, wall-thickness/area ratio ≤0.15, window-area/floor-area ≤1/4. | Equations 9–12 print the same forms with new geometry constants. | Form retained; constants changed. Window multiplicity and unit mapping remain unresolved in both sources. |
| Penalty | Four normalized squared positive parts, multiplier `r=1e6`, and `F=Phi+P`. | Equations 13–15 print the same structure and `r=1e6`. | Definition appears retained. This audit does not establish implementation identity. |
| Catalogs | Slabs 130/150/200; ceilings 11/14/16.5; both wall types 100/150/200/250; windows 1.5/1.8/2.1 m² with one/two layers; doors 3.52/3.96/4.4 and 1.26/1.68 m². | Tables 1–6 print the same values (window table separates area and thickness/layers). | Catalog values substantially retained. |
| Continuous bounds | Explicit PSO bounds: `x3=[100,400]`, `x4=[100,300]`, `x5=[1.2,2.2]`. | No corresponding numerical continuous-bound table was found in the PDF. The optimized coordinates are continuous and need not be catalog values. | 2026 optimization bounds are `NOT_VERIFIABLE` from the article; do not silently import 2023 bounds. |
| Fixed optimization variables | `[x1,x2,x6,x7,x8]=[150,11,2,3.96,1.68]`. | Same fixed vector on journal page 53. | Retained as printed. |
| Printed optimum | Runs near `(291.5,112.4,1.2)`; `F≈21368.21`, `Phi≈20626`, `P≈742`. | All rows print `(223.7,112.4,1.9)`; `F≈16319.607–.609`, `Phi≈14240.621–.688`, `P≈2078.898–.923`. | Material change in reported result and objective scale. Neither optimizer run was reproduced. |
| Simulation software | TerMus-Plus; report describes it as BIM dynamic simulation using EnergyPlus. No exact version is supplied. | TerMus PLUS by ACCA; no exact version or executable model archive is supplied. | Same named front end, but executable/version/model identity is unresolved. |
| Climate data | Says An Giang weather recorded in 2018 was imported; no bibliographic provenance is stated in the extracted section. | Says 2018 An Giang data came from the *Statistical Yearbook of Vietnam 2022*, GSO (2022), described as official. | 2026 adds documentary provenance, but the actual weather input file and transformation are unavailable. |

Differences in this table are not labeled errors, misconduct, or undocumented corrections.
They may represent legitimate revisions, changed geometry, or source-version differences.
