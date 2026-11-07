from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .evaluators.base import EnergyEvaluator
from .models import Configuration, EvaluationResult, Status


def deterministic_minimum(results: Iterable[EvaluationResult], objective: str) -> EvaluationResult | None:
    eligible = [r for r in results if r.status is Status.ADMISSIBLE and objective in r.objectives]
    return min(eligible, key=lambda r: (r.objectives[objective], r.configuration.key()), default=None)


def exhaustive_search(configurations: Iterable[Configuration], evaluator: EnergyEvaluator,
                      objective: str) -> tuple[EvaluationResult | None, list[EvaluationResult]]:
    results = [evaluator.evaluate(configuration) for configuration in configurations]
    return deterministic_minimum(results, objective), results


@dataclass(frozen=True)
class GridPoint:
    x: tuple[float, ...]
    value: float


def grid_search(bounds: tuple[tuple[float, float], ...], steps: tuple[float, ...],
                objective) -> GridPoint:
    """Deterministic inclusive grid search for synthetic or directly simulated objectives."""
    from itertools import product
    axes = []
    for (lower, upper), step in zip(bounds, steps, strict=True):
        if step <= 0 or lower > upper:
            raise ValueError("Invalid grid bounds or step")
        count = int((upper - lower) / step + 1e-12)
        axis = [lower + i * step for i in range(count + 1)]
        if axis[-1] < upper - 1e-12:
            axis.append(upper)
        axes.append(axis)
    points = (GridPoint(tuple(x), float(objective(tuple(x)))) for x in product(*axes))
    return min(points, key=lambda p: (p.value, p.x))
