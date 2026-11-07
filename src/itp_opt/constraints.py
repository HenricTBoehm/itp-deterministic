from __future__ import annotations

from collections.abc import Callable, Iterable

from .models import Configuration, ConstraintResult, Status

Constraint = Callable[[Configuration], ConstraintResult]


def assess(configuration: Configuration, constraints: Iterable[Constraint]) -> tuple[Status, list[ConstraintResult]]:
    results = [constraint(configuration) for constraint in constraints]
    mandatory = [r for r in results if r.mandatory]
    if any(r.status is Status.INADMISSIBLE for r in mandatory):
        return Status.INADMISSIBLE, results
    if any(r.status is Status.NON_EVALUABLE for r in mandatory):
        return Status.NON_EVALUABLE, results
    return Status.ADMISSIBLE, results


def unresolved_report_constraints(_: Configuration) -> ConstraintResult:
    return ConstraintResult(
        "architectural_constraints",
        Status.NON_EVALUABLE,
        "Mandatory formulas from the research report have not been verified.",
    )


H_STORY_MM = 3600.0
EXTERIOR_WALL_LENGTH_MM = 66950.0
INTERIOR_WALL_LENGTH_MM = 47950.0
FLOOR_AREA_MM2 = 140.53e6


def _value(configuration: Configuration, name: str) -> float | None:
    value = dict(configuration.values).get(name)
    return float(value) if isinstance(value, (int, float)) else None


def exterior_wall_minimum(configuration: Configuration) -> ConstraintResult:
    value = _value(configuration, "x3")
    if value is None:
        return ConstraintResult("exterior_wall_minimum", Status.NON_EVALUABLE, "x3 is unavailable.")
    limit = H_STORY_MM / 16.0
    status = Status.ADMISSIBLE if value >= limit else Status.INADMISSIBLE
    return ConstraintResult("exterior_wall_minimum", status, f"Report: H_story/16 <= x3; {limit:g} <= {value:g} mm.")


def interior_wall_minimum(configuration: Configuration) -> ConstraintResult:
    value = _value(configuration, "x4")
    if value is None:
        return ConstraintResult("interior_wall_minimum", Status.NON_EVALUABLE, "x4 is unavailable.")
    limit = H_STORY_MM / 32.0
    status = Status.ADMISSIBLE if value >= limit else Status.INADMISSIBLE
    return ConstraintResult("interior_wall_minimum", status, f"Report: H_story/32 <= x4; {limit:g} <= {value:g} mm.")


def wall_area_ratio(configuration: Configuration) -> ConstraintResult:
    x3, x4 = _value(configuration, "x3"), _value(configuration, "x4")
    if x3 is None or x4 is None:
        return ConstraintResult("wall_area_ratio", Status.NON_EVALUABLE, "x3 or x4 is unavailable.")
    ratio = (x3 * EXTERIOR_WALL_LENGTH_MM + x4 * INTERIOR_WALL_LENGTH_MM) / FLOOR_AREA_MM2
    status = Status.ADMISSIBLE if ratio <= 0.15 else Status.INADMISSIBLE
    return ConstraintResult("wall_area_ratio", status,
                            f"Report: (x3*L3+x4*L4)/A_floor <= 0.15; calculated {ratio:.12g}.")


def total_window_area(configuration: Configuration) -> ConstraintResult:
    return ConstraintResult(
        "total_window_area", Status.NON_EVALUABLE,
        "Report specifies sum(x5)/A_floor <= 1/4, but the number/areas of all window instances are unavailable.",
    )


REPORT_CONSTRAINTS: tuple[Constraint, ...] = (
    exterior_wall_minimum, interior_wall_minimum, wall_area_ratio, total_window_area,
)
