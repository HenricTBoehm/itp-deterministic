"""Independent Decimal reconstruction of the penalty terms printed in the 2023 report."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, getcontext
from itertools import combinations
from typing import Callable

getcontext().prec = 50
D = Decimal

H = D("3600")
L3 = D("66950")
L4 = D("47950")
A = D("140530000")
WALL_RATIO_LIMIT = D("0.15")
PENALTY_FACTOR = D("1e6")
CATALOG = (D("100"), D("150"), D("200"), D("250"))


def c1(x3: Decimal, _x4: Decimal) -> bool:
    return x3 >= H / D(16)


def c2(_x3: Decimal, x4: Decimal) -> bool:
    return x4 >= H / D(32)


def wall_ratio(x3: Decimal, x4: Decimal) -> Decimal:
    return (L3 * x3 + L4 * x4) / A


def c3(x3: Decimal, x4: Decimal) -> bool:
    return wall_ratio(x3, x4) <= WALL_RATIO_LIMIT


CONSTRAINTS: dict[str, Callable[[Decimal, Decimal], bool]] = {"c1": c1, "c2": c2, "c3": c3}


def penalty_terms(x3: Decimal, x4: Decimal) -> dict[str, Decimal]:
    p1 = max(D(0), H / (D(16) * x3) - D(1)) ** 2
    p2 = max(D(0), H / (D(32) * x4) - D(1)) ** 2
    p3 = max(D(0), wall_ratio(x3, x4) - WALL_RATIO_LIMIT) ** 2
    return {"p1": p1, "p2": p2, "p3": p3}


def infer_x4_from_p2(p2: Decimal) -> Decimal:
    """Conditional inverse for the violated branch x4 < H/32."""
    if p2 < 0:
        raise ValueError("p2 must be non-negative")
    return (H / D(32)) / (D(1) + p2.sqrt())


def infer_x3_from_total(total: Decimal, p2: Decimal, x4: Decimal) -> Decimal:
    """Conditional inverse assuming p1=p4=0 and the stated penalty factor."""
    p3 = total / PENALTY_FACTOR - p2
    if p3 < 0:
        raise ValueError("total is too small for p2")
    ratio = WALL_RATIO_LIMIT + p3.sqrt()
    return (A * ratio - L4 * x4) / L3


def catalog_subset_feasibility() -> dict[tuple[str, ...], list[tuple[Decimal, Decimal]]]:
    result: dict[tuple[str, ...], list[tuple[Decimal, Decimal]]] = {}
    names = tuple(CONSTRAINTS)
    for size in range(len(names) + 1):
        for subset in combinations(names, size):
            result[subset] = [
                (x3, x4) for x3 in CATALOG for x4 in CATALOG
                if all(CONSTRAINTS[name](x3, x4) for name in subset)
            ]
    return result


def minimal_infeasible_subsets() -> list[tuple[str, ...]]:
    feasibility = catalog_subset_feasibility()
    infeasible = {subset for subset, witnesses in feasibility.items() if not witnesses}
    return sorted(
        [subset for subset in infeasible
         if all(tuple(item for item in subset if item != removed) not in infeasible for removed in subset)],
        key=lambda subset: (len(subset), subset),
    )


def analytic_continuous_vertices() -> list[tuple[Decimal, Decimal]]:
    limit = WALL_RATIO_LIMIT * A
    return [
        (H / D(16), H / D(32)),
        (H / D(16), (limit - L3 * (H / D(16))) / L4),
        ((limit - L4 * (H / D(32))) / L3, H / D(32)),
    ]


def clipped_continuous_vertices() -> list[tuple[Decimal, Decimal]]:
    """Independent Sutherland-Hodgman half-plane clipping of the bound rectangle."""
    polygon = [(D(100), D(100)), (D(400), D(100)), (D(400), D(300)), (D(100), D(300))]
    functions = (
        lambda point: H / D(16) - point[0],
        lambda point: H / D(32) - point[1],
        lambda point: L3 * point[0] + L4 * point[1] - WALL_RATIO_LIMIT * A,
    )
    for function in functions:
        output: list[tuple[Decimal, Decimal]] = []
        for start, end in zip(polygon, polygon[1:] + polygon[:1]):
            f_start, f_end = function(start), function(end)
            start_inside, end_inside = f_start <= 0, f_end <= 0
            if start_inside:
                output.append(start)
            if start_inside != end_inside:
                t = f_start / (f_start - f_end)
                output.append((start[0] + t * (end[0] - start[0]),
                               start[1] + t * (end[1] - start[1])))
        polygon = output
    return polygon


def rounds_to_one_decimal(value: Decimal) -> Decimal:
    return value.quantize(D("0.1"), rounding=ROUND_HALF_UP)


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


def reconstruction_report() -> dict:
    printed_x3, printed_x4, printed_x5 = D("291.5"), D("112.4"), D("1.2")
    printed_p2, printed_p3, printed_total = D("2.42e-7"), D("7.42e-4"), D("742.210")
    exact = penalty_terms(printed_x3, printed_x4)
    inferred_x4 = infer_x4_from_p2(printed_p2)
    inferred = penalty_terms(printed_x3, inferred_x4)
    inferred_x3_joint = infer_x3_from_total(printed_total, printed_p2, inferred_x4)
    joint = penalty_terms(inferred_x3_joint, inferred_x4)

    # Conditional round-to-nearest intervals inferred from printed significant digits.
    p2_interval = (D("2.415e-7"), D("2.425e-7"))
    p3_interval = (D("7.415e-4"), D("7.425e-4"))
    total_interval = (D("742.2095"), D("742.2105"))
    x4_interval = (infer_x4_from_p2(p2_interval[1]), infer_x4_from_p2(p2_interval[0]))
    coordinate_box = ((D("291.45"), D("291.55")), (D("112.35"), D("112.45")))
    box_ratios = [wall_ratio(x3, x4) for x3 in coordinate_box[0] for x4 in coordinate_box[1]]

    feasibility = catalog_subset_feasibility()
    subset_summary = {
        "+".join(subset) if subset else "empty": {
            "feasible_pairs": len(witnesses),
            "witness": witnesses[0] if witnesses else None,
        }
        for subset, witnesses in feasibility.items()
    }
    analytic = analytic_continuous_vertices()
    clipped = clipped_continuous_vertices()
    output = {
        "classification": {
            "catalog_mus": "CONFIRMED",
            "continuous_feasible_region": "CONFIRMED",
            "printed_x4_p2_match": "CORRECTED",
            "inferred_x4": "CONDITIONAL",
            "c3_violation": "CONFIRMED",
            "internal_pso_coordinates": "NOT_VERIFIABLE",
            "window_constraint": "NOT_VERIFIABLE",
        },
        "constants": {"H_mm": H, "L3_mm": L3, "L4_mm": L4, "A_mm2": A,
                      "penalty_factor": PENALTY_FACTOR},
        "printed_values": {"x3_mm": printed_x3, "x4_mm": printed_x4, "x5_m2": printed_x5,
                           "p2": printed_p2, "p3": printed_p3, "total_penalty": printed_total},
        "test_a_discrete_catalog": {
            "catalog_wall_values_mm": list(CATALOG),
            "subset_feasibility": subset_summary,
            "minimal_infeasible_subsets": minimal_infeasible_subsets(),
            "elementary_proof": {
                "step_1": "c1 forces x3=250 in the documented catalog.",
                "step_2": "At x3=250, c3 is minimized by catalog minimum x4=100.",
                "minimum_ratio_under_c1": wall_ratio(D(250), D(100)),
                "limit": WALL_RATIO_LIMIT,
                "proper_subset_witnesses": {"c1": (D(250), D(100)), "c3": (D(100), D(100))},
            },
        },
        "test_b_continuous_region": {
            "bounds_mm": {"x3": (D(100), D(400)), "x4": (D(100), D(300))},
            "analytic_vertices": analytic,
            "independent_clipping_vertices": clipped,
            "nonempty": bool(clipped),
            "scope": "Feasible only for c1-c3; full building admissibility is not established.",
        },
        "test_c_p2": {
            "from_printed_x4": exact["p2"],
            "reported": printed_p2,
            "inferred_x4_mm": inferred_x4,
            "inferred_violation_mm": H / D(32) - inferred_x4,
            "rounds_to_one_decimal_mm": rounds_to_one_decimal(inferred_x4),
            "conditional_reported_p2_interval": p2_interval,
            "conditional_x4_interval_mm": x4_interval,
            "label": "inferred, not recovered original coordinate",
        },
        "test_d_p3": {
            "from_printed_coordinates": exact["p3"],
            "with_p2_inferred_x4": inferred["p3"],
            "reported": printed_p3,
            "conditional_reported_p3_interval": p3_interval,
            "c3_violated_in_both_cases": True,
            "minimum_ratio_over_printed_coordinate_rounding_box": min(box_ratios),
            "coordinate_rounding_box": coordinate_box,
        },
        "test_e_total": {
            "from_printed_coordinates_assuming_p4_zero": (exact["p1"] + exact["p2"] + exact["p3"]) * PENALTY_FACTOR,
            "with_only_p2_inferred_x4_assuming_p4_zero": sum(inferred.values()) * PENALTY_FACTOR,
            "reported": printed_total,
            "conditional_reported_total_interval": total_interval,
            "joint_conditional_x3_mm": inferred_x3_joint,
            "joint_conditional_x4_mm": inferred_x4,
            "joint_coordinates_round_to_printed": {
                "x3": rounds_to_one_decimal(inferred_x3_joint),
                "x4": rounds_to_one_decimal(inferred_x4),
            },
            "joint_reconstructed_total_assuming_p4_zero": sum(joint.values()) * PENALTY_FACTOR,
            "warning": "Agreement is conditional and does not recover the internal PSO coordinates.",
        },
        "test_f_window": {
            "status": "NON_EVALUABLE",
            "reason": "Window count, area assignment, and m2/mm2 handling are not documented sufficiently.",
            "reported_zero_is_proof_of_feasibility": False,
        },
    }
    return _strings(output)
