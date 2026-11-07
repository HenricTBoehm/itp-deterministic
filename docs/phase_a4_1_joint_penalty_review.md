# Phase A.4.1 — joint Table 14 penalty consistency

## Question and assumptions

Phase A.4 checked each displayed penalty component separately. This extension asks the
stronger question: can one common hidden `(x3,x4)` pair simultaneously explain `p1`, `p2`,
`p3`, total `P`, and the displayed `F=Phi+P` arithmetic?

The audit assumes conventional nearest rounding: three significant digits for `p1`–`p3`,
one decimal place for `x3,x4`, and three decimal places for `F`, `Phi`, and `P`. It uses the
published 2026 constants and the violated branches

\[
x_3=225/(1+\sqrt{p_1}),\qquad x_4=112.5/(1+\sqrt{p_2}).
\]

The fourth component is `NON_EVALUABLE`; only the published mathematical fact
\(p_4\ge0\) is used. Compatibility means at least one value exists under these assumptions.
It is not reconstruction of historical CPSO state.

## Certified bound method

Let \(r=(L_3x_3+L_4x_4)/A-0.15\). It is positive throughout every run domain. For
\(x(p)=C/(1+\sqrt p)\),

\[
\frac{dx}{dp}=-\frac{C}{2\sqrt p(1+\sqrt p)^2}.
\]

Consequently,

\[
\frac{\partial(P_{known}/10^6)}{\partial p_i}
=1+2r\frac{L_i}{A}\frac{dx_i}{dp_i}.
\]

Both `r` and `|dx_i/dp_i|` decrease as either relevant penalty increases. Therefore each
partial derivative is maximized at the upper-upper penalty endpoint. The computed upper
bounds remain strictly negative for every run. Thus `P_known` is strictly decreasing in
both variables: its minimum is at `(p1_high,p2_high)` and its supremum at
`(p1_low,p2_low)`. This proves the extrema locations without assuming that an arbitrary
four-corner search is sufficient.

Positive rounding intervals use the half-open convention `[lower,upper)`. Accordingly, the
lower `P_known` endpoint is an excluded infimum approached at the excluded upper-upper
penalty endpoint; the upper endpoint is an included maximum at the included lower-lower
endpoint. Endpoint values are enclosed with 80-digit directed interval arithmetic. Each square root
is bracketed by adjacent Decimal values; subsequent operations use directed floor/ceiling
rounding. The reported bounds are rounded outward to 12 decimal places.

## Results

| Run | Certified outward `P_known` enclosure | Printed `P` interval | Joint result |
|---:|---:|---:|---|
| 1 | `[2078.988216178383, 2079.013039049142]`¹ | `[2078.8975,2078.8985)` | `CONFIRMED_INCONSISTENCY` |
| 2 | `[2078.917318430838, 2078.941382970343]`¹ | `[2078.9225,2078.9235)` | `CONDITIONALLY_COMPATIBLE` |
| 3 | `[2078.909674639024, 2078.933702985320]`¹ | `[2078.9195,2078.9205)` | `CONDITIONALLY_COMPATIBLE` |

¹ The exact upper raw endpoint is included and lies below the displayed outward ceiling;
the exact lower raw endpoint is an excluded infimum. The printed decimal pairs are certified
outward enclosures, not assertions that both rounded endpoints are attainable.

For all runs, the penalty-inverted coordinate intervals lie wholly inside the displayed
one-decimal coordinate intervals. Their jointly induced `p3` ranges are:

- run 1: `[0.002042123216, 0.002042258040]`;
- run 2: `[0.002041792318, 0.002041926383]`;
- run 3: `[0.002041704674, 0.002041838703]`.

All lie inside the displayed `p3` interval `[0.002035,0.002045)`. Thus coordinate and
`p3` displays are simultaneously compatible. The run-1 contradiction arises at the total:
even the smallest first-three-component penalty exceeds the largest value represented by
`2078.898`. Since `p4>=0`, the unknown term can only increase the total and cannot repair
the contradiction.

For runs 2 and 3, a common coordinate pair can satisfy the three component displays, and
the total intervals overlap the reachable totals after allowing `p4>=0`. They also overlap
the intervals implied by `F-Phi`:

- run 2 simultaneous total interval: `[2078.9225,2078.9230)`;
- run 3 simultaneous total interval: `[2078.9195,2078.9200)`.

These are existence results only, classified `CONDITIONALLY_COMPATIBLE`.

## Run-1 transcription hypothesis

The displayed central arithmetic gives

\[
16319.609-14240.621=2078.988.
\]

If `P` were hypothetically displayed as `2078.988`, its interval would be
`[2078.9875,2078.9885)`. Its simultaneous overlap with `P_known` and `F-Phi` is

`[2078.988216178383...,2078.9885)`.

The hypothesis is therefore `CONDITIONALLY_COMPATIBLE` and would explain the central
addition exactly. It is not adopted as a correction: source intent, unrounded values and
the original implementation remain `NOT_VERIFIABLE`.

## Scientific classification

- Run 1 as printed: `CONFIRMED_INCONSISTENCY` under the stated rounding model.
- Runs 2 and 3: `CONDITIONALLY_COMPATIBLE`.
- Actual internal coordinates and `p4`: `NOT_VERIFIABLE`.
- Implementation error, intent or misconduct: not inferred.

Phase A.4.1 is `READY_FOR_REVIEW`. MPRS remains `HOLD` pending independent scientific
review, and the ITP manuscript v0.2.3 remains unchanged.
