# Phase A.4 claim register

| Claim or discrepancy | Classification | Basis and limitation |
|---|---|---|
| Complete 2026 source PDF identified | `CONFIRMED` | 31 pages; SHA-256 `49a72ad4...174b`; DOI and journal pagination agree. |
| Full wall system has a feasible continuous region | `CORRECTED` | At lower bounds, numerator `27,441,000` exceeds `tau*A=20,982,000`; no region exists even over R². |
| `{c1,c3}` is contradictory over all R² | `CORRECTED` | Negative `x4` gives witnesses; contradiction requires at least `x4>=0`. |
| `{c1,c3}` infeasible for nonnegative thicknesses/catalog | `CONFIRMED` | `L3*225 > tau*A` before any nonnegative `x4` contribution. |
| Printed candidate satisfies `c1`, `c2`, `c3` | `CORRECTED` | All exact normalized residuals are positive and all violations survive one-decimal coordinate rounding. |
| Printed candidate window condition | `NOT_VERIFIABLE` | Multiplicity, aggregation and unit mapping are unresolved; represented as `NON_EVALUABLE`. |
| Exact printed coordinates reproduce Table 14 components | `CORRECTED` | None of the three exact non-window terms lies in any corresponding displayed component interval. |
| Reported components could arise inside coordinate rounding box | `CONDITIONAL` | Each displayed interval intersects each component range over the box; this does not identify internal coordinates. |
| Run 1 components and printed total arise from one common pair | `CONFIRMED_INCONSISTENCY` | Certified `P_known >= 2078.988216178383`, while printed `P < 2078.8985`; unknown `p4>=0` cannot reduce it. |
| Run 2 joint components, total and `F-Phi` | `CONDITIONALLY_COMPATIBLE` | Common interval `[2078.9225,2078.9230)` exists under stated rounding assumptions and `p4>=0`. |
| Run 3 joint components, total and `F-Phi` | `CONDITIONALLY_COMPATIBLE` | Common interval `[2078.9195,2078.9200)` exists under stated rounding assumptions and `p4>=0`. |
| Run 1 `2078.988` transcription hypothesis | `CONDITIONALLY_COMPATIBLE` | Overlap `[2078.988216178383...,2078.9885)` exists and central addition closes; author intent remains unverified. |
| Run 1 `F=Phi+P` decomposition | `CONFIRMED` inconsistency | `14240.621+2078.898=16319.519`, 0.090 below printed `F`; three-decimal intervals are disjoint. |
| Run 2 decomposition error | `CONDITIONAL` | Printed sum differs by 0.001, but ordinary three-decimal intervals overlap. |
| Run 3 decomposition error | `CONDITIONAL` | Printed sum differs by 0.001, but ordinary three-decimal intervals overlap. |
| Printed weighted component sums equal `P` | `CORRECTED` for central printed values | Central sums are `2076.81`, `2077.07`, `2077.15`. |
| Reported `P` incompatible with component display precision | `CORRECTED` | Coarse precision of `2.04e-3` gives weighted intervals containing every reported `P`; compatibility is conditional. |
| Third component row's “run 1” means run 3 | `NOT_VERIFIABLE` | Positional evidence suggests a label typo, but author intent/internal output is unavailable. |
| Internal CPSO coordinates recovered | `NOT_VERIFIABLE` | Only rounded output is available; no inversion is used as historical recovery. |
| ANN/CPSO/optimality reproduced | `NOT_VERIFIABLE` | Out of scope and required data/artifacts are unavailable. |
| 170-scenario dataset fully audited | `NOT_VERIFIABLE` | The PDF displays only first 20 and last 10 rows. |
| MIT covers the journal PDF and historical sources | `CONFIRMED_INCONSISTENCY` | MIT applies to the audit work; the article states CC BY-NC 4.0, while historical-source redistribution rights remain `NOT_VERIFIABLE`. |
| Publication rights cleared | `NOT_VERIFIABLE` | Historical permissions and intended-use compliance are unresolved; this is a mandatory release gate, not an editorial issue. |
| MPRS publication decision | `CONFIRMED` | Remains `HOLD` by task boundary. |

`CONFIRMED` documentary inconsistencies do not by themselves prove defects in the original
software. `CORRECTED` means the proposition is corrected by exact substitution or domain
analysis, not that the publication record has been altered.
