"""Exact, independent audit of the constraints printed in the 2026 article.

This module deliberately does not import the 2023 reconstruction.  The two
sources use different geometry constants and reported optimization results.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, getcontext
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
        "boundaries": {
            "ann_training_reproduced": False,
            "cpso_reproduced": False,
            "optimality_verified": False,
            "physical_building_impossibility_claimed": False,
        },
    })
