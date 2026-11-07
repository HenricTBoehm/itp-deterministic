# Published 2026 article: independent feasibility and numerical audit

## Scope and provenance

This Phase A.4 audit treats the published article as a new source and does not carry the
2023 constants or conclusions into the calculation. The primary source is the complete
31-page PDF at `docs/A methodological approach to energy optimization for buildings by
utilizing machine learning-based surrogate model and an optimization technique.pdf`.

- Article: Le Quang Huy and Hoang Quynh Anh, *A methodological approach to energy
  optimization for buildings by utilizing machine learning-based surrogate model and an
  optimization technique*.
- DOI: `10.46223/HCMCOUJS.acs.en.16.1.84.2026`.
- Source identifier: HCMCOUJS-Advances in Computational Structures 16(1), 30–60.
- PDF SHA-256: `49a72ad4f46f58ff4257714e075e54926ffa039b1878c3fecd7dacff57ec174b`.
- Extraction: Poppler `pdftotext -layout`; formulas were checked against the rendered pages.
- Principal journal pages: 42–45, 51, 53–54, 55, and 56–57.

The PDF is an existing tracked source and was not modified or re-added by this review.

## Independent feasibility proof

The article gives

\[
H=3600,\quad L_3=99000,\quad L_4=45920,\quad
A=139880000,\quad\tau=0.15.
\]

Thus `c1` and `c2` require \(x_3\ge225\) and \(x_4\ge112.5\). Since both length
coefficients are positive, the smallest possible numerator under those two constraints is

\[
99000(225)+45920(112.5)=27{,}441{,}000.
\]

But \(\tau A=20{,}982{,}000\). Therefore all three wall constraints are infeasible even
over unrestricted \(\mathbb R^2\). There is no feasible continuous wall region under the
published constraints, and consequently none in the documented catalog.

### Mandatory adversarial domain check

`{c1,c3}` alone is **not** universally contradictory. At the `c1` boundary, `c3` is
equivalent to

\[
x_4\le\frac{0.15(139880000)-99000(225)}{45920}
=-28.15766550522648\ldots.
\]

Hence `(225, -28.1576655...)` is a witness over \(\mathbb R^2\). In contrast, `{c1,c3}`
is infeasible whenever \(x_4\ge0\), because `c1` alone contributes
\(99000(225)=22{,}275{,}000>\tau A\). This includes the documented physical wall catalog
`{100,150,200,250}`. The conclusion is domain-specific; it is not a claim that the actual
building is physically impossible.

### Area and threshold sensitivity

Let

\[
N=L_3H/16+L_4H/32=27{,}441{,}000.
\]

The full system is feasible exactly when \(\tau A\ge N\). Its boundary values are

\[
\tau_{\min}=N/A=0.1961752931083786\ldots,
\qquad A_{\min}=N/\tau=182{,}940{,}000\;\mathrm{mm}^2.
\]

The reported pair is short of the boundary by \(\tau A-N=-6{,}459{,}000\;\mathrm{mm}^2\).
Analytically,

\[
\frac{d\tau_{\min}}{dA}=-N/A^2,\quad
\frac{dA_{\min}}{d\tau}=-N/\tau^2,
\]

and for the margin \(M=\tau A-N\), \(\partial M/\partial A=\tau\) and
\(\partial M/\partial\tau=A\). Derivatives with respect to `H`, `L3`, and `L4` are included
in `results/published_2026_audit.json`.

## Printed CPSO candidate

For `(x3,x4,x5)=(223.7,112.4,1.9)`, 60-digit `Decimal` arithmetic gives:

| Quantity | Exact substitution |
|---|---:|
| `c1` normalized residual | `0.005811354492624050067...` |
| `c2` normalized residual | `0.000889679715302491103...` |
| `c3` normalized residual | `0.045222390620531884472...` |
| `p1` | `0.000033771841038941730...` |
| `p2` | `0.0000007915299958207216...` |
| `p3` | `0.002045064613435970159...` |
| `10^6(p1+p2+p3)` | `2079.627984470732611...` |
| `p4` | `NON_EVALUABLE` |

All three reconstructable constraints are violated. They remain violated throughout the
ordinary one-decimal boxes `x3 in [223.65,223.75)` and `x4 in [112.35,112.45)`; the
minimum wall ratio on the closed box is `0.195170589076351... > 0.15`.

Exact substitution does not reproduce any run's three printed non-window penalty
components (`CORRECTED`). Nevertheless, each displayed component interval intersects the
range generated over the coordinate-rounding box (`CONDITIONAL`). This is compatible with
unprinted internal coordinates but does not recover them. The window term remains
`NON_EVALUABLE`: opening multiplicity, aggregation and the m²/mm² mapping are unresolved.

## Table 14 arithmetic

| Run | Printed `Phi+P` | Printed `F` | Difference `F-(Phi+P)` | Classification |
|---:|---:|---:|---:|---|
| 1 | 16319.519 | 16319.609 | +0.090 | `CONFIRMED` inconsistency |
| 2 | 16319.608 | 16319.607 | -0.001 | `CONDITIONAL` on hidden digits |
| 3 | 16319.608 | 16319.607 | -0.001 | `CONDITIONAL` on hidden digits |

For run 1, ordinary nearest rounding to three decimals permits `Phi+P` only in
`[16319.5180,16319.5200)`, while the displayed `F` represents
`[16319.6085,16319.6095)`. The intervals are disjoint. Runs 2 and 3 have overlapping
intervals, so their one-unit-last-place differences can arise from hidden digits.

The printed non-window component sums times \(10^6\) are `2076.81`, `2077.07`, and
`2077.15`, not the displayed penalties. However, `p3=2.04e-3` has only three significant
digits and alone permits about ±5 after weighting. All three displayed `P` values therefore
fall inside the component rounding intervals (`CONDITIONAL`). Table 14 also labels the
third component row “run 1”; its position suggests run 3, but that intended correction is
`NOT_VERIFIABLE`. These are documentary findings, not proof of an implementation error.

## Scientific boundary

This audit does not reproduce ANN training or CPSO, verify optimality, validate PADC/DEA,
claim physical impossibility, compare methodological superiority, or allege misconduct.
The publication decision remains `HOLD`.
