# Methodology and open assumptions

## Mathematical statement

The target problem is

\[
\min_{x \in X_{\mathrm{adm}}} E(x),
\]

where `E` must come from an exact observed simulation or a successfully executed, verified physical simulator. Enumeration without such evaluation is not optimization.

## Variable classification

The report describes `x1`–`x8` and provides named catalog variants and their dimensions. The implementation stores both identifiers and physical values. It does not silently turn the discrete catalog into the separate continuous bounds used by the report's PSO. `window_g_value` and `window_u_value` are physical properties; the validator finds that their observed pairs are not a function of glass-layer count alone.

| Variables | Provisional class | Unresolved evidence |
|---|---|---|
| floor, ceiling, wall, window, doors | discrete report catalog | documented identifiers and dimensions |
| x3, x4, x5 in historical PSO | separate continuous problem | physical constructability/precision |
| g-value, U-value | window physical properties | mapping to named window/glazing type |
| other building/model fields | invariant | model and weather files absent |

## Admissibility

Mandatory constraints use three states: `ADMISSIBLE`, `INADMISSIBLE`, and `NON_EVALUABLE`. Three wall constraints were verified from rendered report page 46 and implemented. The fourth uses `sum(x5)`, but window-instance counts are unavailable, so that check is `NON_EVALUABLE`. An already violated mandatory condition makes the overall status `INADMISSIBLE`; otherwise any unresolved mandatory condition prevents an admissibility claim.

## Determinism

Catalog products use fixed field and catalog order. Equal objective values are resolved by a canonical lexicographic configuration key. Grid endpoints and steps are explicit. No random generator, ML library, PSO, genetic algorithm, or surrogate model is used.

## EnergyPlus boundary

Presence of an executable, model, and weather file is necessary but insufficient. A run remains disabled until each configuration field has a reviewed mapping to concrete EnergyPlus objects and output meters/units. This prevents a mock or unchanged base model from being presented as physical optimization.

## Evidence needed next

1. Original DOCX and archive, including historical code and all CSV files.
2. Verified units and a row-level input/output key.
3. Architectural formulas and a decision about which are mandatory.
4. Complete catalog values and compatibility rules.
5. EnergyPlus IDF/epJSON, EPW, simulator version, output meters, and a reference result.
