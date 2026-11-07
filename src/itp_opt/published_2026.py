"""Exact, independent audit of the constraints printed in the 2026 article.

This module deliberately does not import the 2023 reconstruction.  The two
sources use different geometry constants and reported optimization results.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, getcontext, localcontext
from hashlib import sha256
from pathlib import Path
from typing import Iterable

getcontext().prec = 60
D = Decimal

DOI = "10.46223/HCMCOUJS.acs.en.16.1.84.2026"
SOURCE_FILE = "docs/A methodological approach to energy optimization for buildings by utilizing machine learning-based surrogate model and an optimization technique.pdf"
SOURCE_SHA256 = "49a72ad4f46f58ff4257714e075e54926ffa039b1878c3fecd7dacff57ec174b"
SOURCE_URL = "https://github.com/HenricTBoehm/itp-deterministic/blob/main/docs/A%20methodological%20approach%20to%20energy%20optimization%20for%20buildings%20by%20utilizing%20machine%20learning-based%20surrogate%20model%20and%20an%20optimization%20technique.pdf"

H = D("3600")
L3 = D("99000")
L4 = D("45920")
A = D("139880000")
TAU = D("0.15")
PENALTY_WEIGHT = D("1e6")
WALL_CATALOG = (D("100"), D("150"), D("200"), D("250"))
PRINTED_POINT = (D("223.7"), D("112.4"), D("1.9"))

TABLE14 = (
    {"run": 1, "F": D("16319.609"), "phi": D("14240.621"), "P": D("2078.898"),
     "components": (D("3.57e-5"), D("1.11e-6"), D("2.04e-3"), D("0.00"))},
    {"run": 2, "F": D("16319.607"), "phi": D("14240.685"), "P": D("2078.923"),
     "components": (D("3.59e-5"), D("1.17e-6"), D("2.04e-3"), D("0.00"))},
    # Table 14 labels this component row "run 1"; its position makes run 3 the
    # likely intended label, but the documentary typo is retained as evidence.
    {"run": 3, "F": D("16319.607"), "phi": D("14240.688"), "P": D("2078.920"),
     "components": (D("3.60e-5"), D("1.15e-6"), D("2.04e-3"), D("0.00"))},
)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def wall_ratio(x3: Decimal, x4: Decimal) -> Decimal:
    return (L3 * x3 + L4 * x4) / A


def normalized_residuals(x3: Decimal, x4: Decimal) -> dict[str, Decimal | None]:
    """Return residuals in the article's penalty convention (feasible <= 0)."""
    return {
        # Algebraically identical to H/(16*x3)-1 and H/(32*x4)-1,
        # but avoids avoidable cancellation in finite Decimal arithmetic.
        "c1": (H / D(16) - x3) / x3,
        "c2": (H / D(32) - x4) / x4,
        "c3": wall_ratio(x3, x4) - TAU,
        "window": None,
    }


def dimensional_margins(x3: Decimal, x4: Decimal) -> dict[str, Decimal]:
    """Positive margins satisfy c1/c2; a nonnegative c3 margin satisfies c3."""
    return {
        "c1_mm": x3 - H / D(16),
        "c2_mm": x4 - H / D(32),
        "c3_mm2": TAU * A - L3 * x3 - L4 * x4,
    }


def penalty_terms(x3: Decimal, x4: Decimal) -> dict[str, Decimal | None]:
    residuals = normalized_residuals(x3, x4)
    return {
        "p1": max(D(0), residuals["c1"]) ** 2,  # type: ignore[arg-type]
        "p2": max(D(0), residuals["c2"]) ** 2,  # type: ignore[arg-type]
        "p3": max(D(0), residuals["c3"]) ** 2,  # type: ignore[arg-type]
        "p4": None,
    }


def c1_c3_x4_ceiling(x3: Decimal = H / D(16)) -> Decimal:
    """Largest x4 satisfying c3 for a fixed x3."""
    return (TAU * A - L3 * x3) / L4


def minimum_feasible_tau() -> Decimal:
    return (L3 * H / D(16) + L4 * H / D(32)) / A


def minimum_feasible_area(tau: Decimal = TAU) -> Decimal:
    return (L3 * H / D(16) + L4 * H / D(32)) / tau


def sensitivity_report() -> dict[str, Decimal]:
    numerator = L3 * H / D(16) + L4 * H / D(32)
    return {
        "binding_numerator_mm2": numerator,
        "tau_min": numerator / A,
        "area_min_at_reported_tau_mm2": numerator / TAU,
        "d_tau_min_d_area": -numerator / (A * A),
        "d_tau_min_d_L3": H / (D(16) * A),
        "d_tau_min_d_L4": H / (D(32) * A),
        "d_tau_min_d_H": (L3 / D(16) + L4 / D(32)) / A,
        "d_area_min_d_tau": -numerator / (TAU * TAU),
        "feasibility_margin_tauA_minus_N_mm2": TAU * A - numerator,
        "d_margin_d_area": TAU,
        "d_margin_d_tau": A,
    }


def domain_feasibility() -> dict:
    x4_ceiling = c1_c3_x4_ceiling()
    catalog_pairs = [
        (x3, x4) for x3 in WALL_CATALOG for x4 in WALL_CATALOG
        if x3 >= H / D(16)
        and x4 >= H / D(32)
        and wall_ratio(x3, x4) <= TAU
    ]
    return {
        "c1_c3": {
            "R2": {"feasible": True, "witness": (H / D(16), x4_ceiling),
                    "condition_at_c1_boundary": f"x4 <= {x4_ceiling}"},
            "x4_nonnegative": {"feasible": False,
                               "proof": "c1 implies L3*x3 > tau*A even at x4=0"},
            "documented_wall_catalog": {"feasible": False},
        },
        "c1_c2_c3": {
            "R2": {"feasible": False,
                    "proof": "positive L3,L4 make the c3 left side minimal at c1/c2 lower bounds"},
            "documented_wall_catalog": {"feasible": bool(catalog_pairs), "witnesses": catalog_pairs},
        },
    }


def rounding_box(value: Decimal, quantum: Decimal = D("0.1")) -> tuple[Decimal, Decimal]:
    half = quantum / D(2)
    return value - half, value + half


def candidate_audit() -> dict:
    x3, x4, x5 = PRINTED_POINT
    residuals = normalized_residuals(x3, x4)
    terms = penalty_terms(x3, x4)
    known_sum = sum(value for value in terms.values() if value is not None)
    x3_box, x4_box = rounding_box(x3), rounding_box(x4)
    corners = [(a, b) for a in x3_box for b in x4_box]
    term_ranges = {
        "p1": (penalty_terms(x3_box[1], x4)["p1"], penalty_terms(x3_box[0], x4)["p1"]),
        "p2": (penalty_terms(x3, x4_box[1])["p2"], penalty_terms(x3, x4_box[0])["p2"]),
        "p3": (penalty_terms(x3_box[0], x4_box[0])["p3"],
               penalty_terms(x3_box[1], x4_box[1])["p3"]),
    }
    comparisons = []
    for row in TABLE14:
        component_intervals = [_component_interval(value) for value in row["components"][:3]]
        exact_matches = [low <= terms[f"p{index}"] < high
                         for index, (low, high) in enumerate(component_intervals, start=1)]
        box_compatible = [
            _intervals_overlap(term_ranges[f"p{index}"], interval)
            for index, interval in enumerate(component_intervals, start=1)
        ]
        comparisons.append({
            "run": row["run"],
            "reported_components": row["components"],
            "exact_printed_coordinate_matches": exact_matches,
            "exact_substitution_classification": "CORRECTED" if not all(exact_matches) else "CONFIRMED",
            "coordinate_rounding_box_compatible": box_compatible,
            "rounding_box_classification": "CONDITIONAL" if all(box_compatible) else "CONFIRMED",
        })
    return {
        "printed_coordinates": {"x3_mm": x3, "x4_mm": x4, "x5_m2": x5},
        "normalized_residuals_feasible_if_nonpositive": residuals,
        "dimensional_margins": dimensional_margins(x3, x4),
        "penalty_terms_exact_substitution": terms,
        "known_penalty_sum": known_sum,
        "known_weighted_penalty": PENALTY_WEIGHT * known_sum,
        "window": {
            "status": "NON_EVALUABLE",
            "reason": "Multiplicity, area aggregation, and m2-to-mm2 mapping are unresolved.",
        },
        "one_decimal_rounding_box_half_open": {"x3_mm": x3_box, "x4_mm": x4_box},
        "penalty_ranges_over_rounding_box": term_ranges,
        "reported_penalty_comparison": comparisons,
        "rounding_robustness": {
            "c1_violated_throughout": x3_box[1] < H / D(16),
            "c2_violated_throughout": x4_box[1] < H / D(32),
            "c3_violated_throughout": min(wall_ratio(a, b) for a, b in corners) > TAU,
            "minimum_wall_ratio_on_closed_box": min(wall_ratio(a, b) for a, b in corners),
        },
        "interpretation": "Exact substitution of printed coordinates; no inference of internal CPSO coordinates.",
    }


def _rounding_interval(value: Decimal, places: str = "0.001") -> tuple[Decimal, Decimal]:
    half = D(places) / D(2)
    return value - half, value + half


def _intervals_overlap(first: tuple[Decimal, Decimal], second: tuple[Decimal, Decimal]) -> bool:
    return max(first[0], second[0]) < min(first[1], second[1])


def _component_interval(value: Decimal) -> tuple[Decimal, Decimal]:
    if value == 0:
        # "0.00" gives no defensible scientific-notation precision for p4.
        return D(0), D("Infinity")
    # Three significant digits: e.g. 3.57e-5 has half-ULP 0.005e-5.
    half_ulp = D(5).scaleb(value.adjusted() - 3)
    return value - half_ulp, value + half_ulp


def significant_digits_interval(value: Decimal) -> tuple[Decimal, Decimal]:
    """Half-open interval represented by a three-significant-digit value."""
    if value <= 0:
        raise ValueError("a positive displayed value is required")
    return _component_interval(value)


def invert_violated_penalty(limit: Decimal, penalty: Decimal) -> Decimal:
    """Invert p=(limit/x-1)^2 on the violated branch x < limit."""
    if penalty <= 0:
        raise ValueError("penalty must be positive on the violated branch")
    return limit / (D(1) + penalty.sqrt())


def coordinate_interval_from_penalty(
        limit: Decimal, interval: tuple[Decimal, Decimal]) -> tuple[Decimal, Decimal]:
    """Coordinate bounds induced by a penalty interval; inversion is decreasing."""
    return invert_violated_penalty(limit, interval[1]), invert_violated_penalty(limit, interval[0])


def _intersection(*intervals: tuple[Decimal, Decimal]) -> tuple[Decimal, Decimal] | None:
    result = max(item[0] for item in intervals), min(item[1] for item in intervals)
    return result if result[0] < result[1] else None


def known_penalty_from_components(p1: Decimal, p2: Decimal) -> Decimal:
    x3 = invert_violated_penalty(H / D(16), p1)
    x4 = invert_violated_penalty(H / D(32), p2)
    residual = max(D(0), wall_ratio(x3, x4) - TAU)
    return PENALTY_WEIGHT * (p1 + p2 + residual * residual)


def _known_terms(p1: Decimal, p2: Decimal) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    x3 = invert_violated_penalty(H / D(16), p1)
    x4 = invert_violated_penalty(H / D(32), p2)
    residual = wall_ratio(x3, x4) - TAU
    return x3, x4, residual, residual * residual


def _partial_derivatives(p1: Decimal, p2: Decimal) -> tuple[Decimal, Decimal]:
    x3, x4, residual, _p3 = _known_terms(p1, p2)
    # dx/dp = -limit / (2*sqrt(p)*(1+sqrt(p))^2)
    dx3 = -(H / D(16)) / (D(2) * p1.sqrt() * (D(1) + p1.sqrt()) ** 2)
    dx4 = -(H / D(32)) / (D(2) * p2.sqrt() * (D(1) + p2.sqrt()) ** 2)
    return (
        D(1) + D(2) * residual * (L3 / A) * dx3,
        D(1) + D(2) * residual * (L4 / A) * dx4,
    )


def _outward(value: Decimal, rounding: str) -> Decimal:
    return value.quantize(D("0.000000000001"), rounding=rounding)


def _known_penalty_endpoint_enclosure(
        p1: Decimal, p2: Decimal) -> tuple[Decimal, Decimal]:
    """Directed 80-digit interval enclosure at one exact (p1,p2) endpoint."""
    with localcontext() as ctx:
        ctx.prec = 80
        # Decimal sqrt is correctly rounded; adjacent representable values form
        # a conservative enclosure even in the exceptional exactly representable case.
        root1 = p1.sqrt()
        root2 = p2.sqrt()
        root1_bounds = ctx.next_minus(root1), ctx.next_plus(root1)
        root2_bounds = ctx.next_minus(root2), ctx.next_plus(root2)

        ctx.rounding = ROUND_FLOOR
        x3_low = (H / D(16)) / (D(1) + root1_bounds[1])
        x4_low = (H / D(32)) / (D(1) + root2_bounds[1])
        residual_low = (L3 * x3_low + L4 * x4_low) / A - TAU
        if residual_low <= 0:
            raise ArithmeticError("positive c3 residual required for this enclosure")
        p3_low = residual_low * residual_low
        total_low = PENALTY_WEIGHT * (p1 + p2 + p3_low)

        ctx.rounding = ROUND_CEILING
        x3_high = (H / D(16)) / (D(1) + root1_bounds[0])
        x4_high = (H / D(32)) / (D(1) + root2_bounds[0])
        residual_high = (L3 * x3_high + L4 * x4_high) / A - TAU
        p3_high = residual_high * residual_high
        total_high = PENALTY_WEIGHT * (p1 + p2 + p3_high)
        return total_low, total_high


def joint_penalty_audit(row: dict) -> dict:
    """Audit whether one common hidden pair can explain a Table 14 row."""
    p1_interval = significant_digits_interval(row["components"][0])
    p2_interval = significant_digits_interval(row["components"][1])
    p3_display_interval = significant_digits_interval(row["components"][2])
    x3_from_p1 = coordinate_interval_from_penalty(H / D(16), p1_interval)
    x4_from_p2 = coordinate_interval_from_penalty(H / D(32), p2_interval)
    x3_joint = _intersection(x3_from_p1, rounding_box(PRINTED_POINT[0]))
    x4_joint = _intersection(x4_from_p2, rounding_box(PRINTED_POINT[1]))
    if x3_joint is None or x4_joint is None:
        return {"run": row["run"], "classification": "CONFIRMED_INCONSISTENCY",
                "reason": "penalty-derived and coordinate-display intervals are disjoint"}

    # Inversion maps the entire penalty intervals inside the coordinate boxes,
    # so the p-domain is unchanged by intersection for these three rows.
    p1_low, p1_high = p1_interval
    p2_low, p2_high = p2_interval
    derivative_upper = _partial_derivatives(p1_high, p2_high)
    strictly_decreasing = derivative_upper[0] < 0 and derivative_upper[1] < 0
    if not strictly_decreasing:
        raise ArithmeticError("monotonicity certificate failed")

    # P_known is strictly decreasing in each argument.  Its lower infimum is
    # approached at the excluded upper-upper endpoint, while its maximum is at
    # the included lower-lower endpoint under [low, high) display intervals.
    known_min_raw = known_penalty_from_components(p1_high, p2_high)
    known_max_raw = known_penalty_from_components(p1_low, p2_low)
    minimum_enclosure = _known_penalty_endpoint_enclosure(p1_high, p2_high)
    maximum_enclosure = _known_penalty_endpoint_enclosure(p1_low, p2_low)
    known_bounds = (
        _outward(minimum_enclosure[0], ROUND_FLOOR),
        _outward(maximum_enclosure[1], ROUND_CEILING),
    )
    p3_min = _known_terms(p1_high, p2_high)[3]
    p3_max = _known_terms(p1_low, p2_low)[3]
    p3_bounds = (_outward(p3_min, ROUND_FLOOR), _outward(p3_max, ROUND_CEILING))
    p3_compatible = (p3_display_interval[0] <= p3_min
                     and p3_max < p3_display_interval[1])

    total_interval = _rounding_interval(row["P"])
    f_interval = _rounding_interval(row["F"])
    phi_interval = _rounding_interval(row["phi"])
    f_minus_phi_interval = (f_interval[0] - phi_interval[1],
                            f_interval[1] - phi_interval[0])
    simultaneous_total = _intersection(
        total_interval,
        f_minus_phi_interval,
        (known_min_raw, D("Infinity")),  # p4 >= 0 can only increase the penalty.
    )
    compatible = p3_compatible and simultaneous_total is not None
    return {
        "run": row["run"],
        "display_intervals": {"p1": p1_interval, "p2": p2_interval,
                              "p3": p3_display_interval, "P": total_interval,
                              "F_minus_phi": f_minus_phi_interval},
        "penalty_derived_coordinate_intervals_mm": {"x3": x3_from_p1, "x4": x4_from_p2},
        "joint_coordinate_intervals_mm": {"x3": x3_joint, "x4": x4_joint},
        "coordinate_intersections_nonempty": True,
        "p3_bounds": p3_bounds,
        "p3_simultaneously_compatible": p3_compatible,
        "known_penalty_raw_extrema": {"lower": known_min_raw, "upper": known_max_raw},
        "known_penalty_endpoint_semantics": {
            "lower": "infimum; excluded because both upper penalty endpoints are excluded",
            "upper": "maximum; included because both lower penalty endpoints are included",
        },
        "directed_endpoint_enclosures": {"minimum_endpoint": minimum_enclosure,
                                         "maximum_endpoint": maximum_enclosure},
        "known_penalty_certified_outward_bounds": known_bounds,
        "monotonicity_certificate": {
            "partial_derivative_upper_bounds": {"d_dp1": derivative_upper[0],
                                                 "d_dp2": derivative_upper[1]},
            "strictly_decreasing_in_p1_and_p2": strictly_decreasing,
            "proof": ("residual and |dx_i/dp_i| decrease with either penalty; therefore each "
                      "partial derivative is maximized at the upper-upper endpoint, where both are negative"),
            "numerical_certification": ("80-digit directed interval arithmetic with adjacent-value "
                                        "sqrt enclosures; reported bounds rounded outward to 12 decimals"),
        },
        "p4": {"status": "NON_EVALUABLE", "known_fact": "p4 >= 0"},
        "simultaneous_total_interval": simultaneous_total,
        "classification": ("CONDITIONALLY_COMPATIBLE" if compatible
                           else "CONFIRMED_INCONSISTENCY"),
        "historical_coordinates_reconstructed": False,
    }


def joint_penalty_report() -> dict:
    rows = [joint_penalty_audit(row) for row in TABLE14]
    hypothesis = D("2078.988")
    hypothesis_interval = _rounding_interval(hypothesis)
    run1 = rows[0]
    hypothesis_joint = _intersection(
        hypothesis_interval,
        run1["display_intervals"]["F_minus_phi"],
        (run1["known_penalty_raw_extrema"]["lower"], D("Infinity")),
    )
    return _strings({
        "audit": {"phase": "A.4.1", "decision": "READY_FOR_REVIEW"},
        "assumptions": {
            "component_rounding": "conventional nearest rounding to three significant digits",
            "interval_convention": "positive displayed values use half-open [lower, upper) intervals",
            "coordinate_rounding": "conventional nearest rounding to one decimal place",
            "total_rounding": "conventional nearest rounding to three decimal places",
            "violated_branches": True,
            "p4": "unknown but nonnegative",
        },
        "runs": rows,
        "run1_transcription_hypothesis": {
            "hypothesized_P": hypothesis,
            "display_interval": hypothesis_interval,
            "F_minus_phi_central": TABLE14[0]["F"] - TABLE14[0]["phi"],
            "simultaneous_interval": hypothesis_joint,
            "classification": ("CONDITIONALLY_COMPATIBLE" if hypothesis_joint
                               else "CONFIRMED_INCONSISTENCY"),
            "warning": "A compatible transcription hypothesis is not a correction or historical reconstruction.",
        },
    })


def table14_audit() -> list[dict]:
    audited = []
    for row in TABLE14:
        displayed_sum = row["phi"] + row["P"]
        add_interval = (
            _rounding_interval(row["phi"])[0] + _rounding_interval(row["P"])[0],
            _rounding_interval(row["phi"])[1] + _rounding_interval(row["P"])[1],
        )
        f_interval = _rounding_interval(row["F"])
        components: Iterable[Decimal] = row["components"][:3]
        component_sum = sum(components, D(0))
        component_intervals = [_component_interval(value) for value in components]
        scaled_component_interval = (
            PENALTY_WEIGHT * sum((item[0] for item in component_intervals), D(0)),
            PENALTY_WEIGHT * sum((item[1] for item in component_intervals), D(0)),
        )
        p_compatible = scaled_component_interval[0] <= row["P"] < scaled_component_interval[1]
        objective_compatible = _intervals_overlap(add_interval, f_interval)
        audited.append({
            **row,
            "phi_plus_P_from_printed": displayed_sum,
            "F_minus_printed_sum": row["F"] - displayed_sum,
            "three_decimal_intervals": {"phi_plus_P": add_interval, "F": f_interval},
            "objective_rounding_compatible": objective_compatible,
            "objective_classification": "CONDITIONAL" if objective_compatible else "CONFIRMED",
            "objective_finding": ("compatible with unprinted digits under ordinary nearest rounding"
                                  if objective_compatible else
                                  "printed decomposition is inconsistent and cannot be explained by three-decimal rounding"),
            "printed_nonwindow_component_sum": component_sum,
            "weighted_printed_component_sum": PENALTY_WEIGHT * component_sum,
            "weighted_component_rounding_interval": scaled_component_interval,
            "reported_P_compatible_with_component_precision": p_compatible,
            "component_sum_classification": "CONDITIONAL" if p_compatible else "CONFIRMED",
        })
    return audited


def _strings(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, tuple):
        return [_strings(item) for item in value]
    if isinstance(value, list):
        return [_strings(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _strings(item) for key, item in value.items()}
    return value


def audit_report() -> dict:
    return _strings({
        "audit": {"phase": "A.4", "decision": "HOLD", "scope": "mathematical and documentary audit"},
        "source": {
            "identifier": "HCMCOUJS-Advances in Computational Structures 16(1), 30-60",
            "doi": DOI,
            "file": SOURCE_FILE,
            "repository_url": SOURCE_URL,
            "sha256": SOURCE_SHA256,
            "pages": 31,
            "journal_pages_used": ["42-45", "51", "53-54", "55", "56-57"],
            "extraction": "Poppler pdftotext -layout; equations checked against rendered PDF pages",
        },
        "constants_2026": {"H_mm": H, "L3_mm": L3, "L4_mm": L4, "A_mm2": A,
                           "tau": TAU, "penalty_weight": PENALTY_WEIGHT},
        "feasibility": domain_feasibility(),
        "sensitivities": sensitivity_report(),
        "published_candidate": candidate_audit(),
        "table14": table14_audit(),
        "joint_penalty": joint_penalty_report(),
        "boundaries": {
            "ann_training_reproduced": False,
            "cpso_reproduced": False,
            "optimality_verified": False,
            "physical_building_impossibility_claimed": False,
        },
    })
