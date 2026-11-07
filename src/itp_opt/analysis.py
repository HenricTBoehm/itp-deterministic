from __future__ import annotations

from collections.abc import Iterable
from math import sqrt
from statistics import fmean, median, pstdev

from .models import EvaluationResult


def pareto_front(results: Iterable[EvaluationResult], objectives: tuple[str, ...]) -> list[EvaluationResult]:
    candidates = [r for r in results if all(name in r.objectives for name in objectives)]
    front = []
    for candidate in candidates:
        dominated = any(
            all(other.objectives[name] <= candidate.objectives[name] for name in objectives)
            and any(other.objectives[name] < candidate.objectives[name] for name in objectives)
            for other in candidates if other is not candidate
        )
        if not dominated:
            front.append(candidate)
    return sorted(front, key=lambda result: result.configuration.key())


def summarize(results: list[EvaluationResult]) -> dict:
    names = sorted({name for result in results for name in result.objectives})
    statistics = {}
    minima = {}
    for name in names:
        values = [result.objectives[name] for result in results if name in result.objectives]
        statistics[name] = {
            "count": len(values), "min": min(values), "max": max(values),
            "mean": fmean(values), "median": median(values),
            "population_standard_deviation": pstdev(values),
        }
        available = [result for result in results if name in result.objectives]
        best = min(available, key=lambda result: (result.objectives[name], result.configuration.key()), default=None)
        if best:
            minima[name] = {"value": best.objectives[name], "configuration": best.configuration.as_dict(),
                            "tie_break": "lexicographic canonical configuration key"}
    common = tuple(name for name in names if all(name in result.objectives for result in results))
    inputs = sorted({name for result in results for name, value in result.configuration.values
                     if isinstance(value, (int, float))})
    correlations = {}
    for input_name in inputs:
        correlations[input_name] = {}
        for objective_name in names:
            pairs = [(float(dict(result.configuration.values)[input_name]), result.objectives[objective_name])
                     for result in results
                     if input_name in dict(result.configuration.values) and objective_name in result.objectives]
            correlations[input_name][objective_name] = _pearson(pairs)
    return {
        "observation_count": len(results), "descriptive_statistics": statistics,
        "observed_minima": minima,
        "pareto_objectives": common,
        "pareto_configuration_keys": [item.configuration.key() for item in pareto_front(results, common)] if common else [],
        "pearson_associations": correlations,
        "association_caveat": (
            "Descriptive correlations in 30 non-factorial, jointly varying cases; not causal sensitivities. "
            "The report/CSV configuration conflict also limits interpretation."
        ),
        "scope": "Empirical observations only; no prediction, interpolation, causal inference, or admissibility claim.",
    }


def _pearson(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    x_mean, y_mean = fmean(xs), fmean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in pairs)
    denominator = sqrt(sum((x - x_mean) ** 2 for x in xs) * sum((y - y_mean) ** 2 for y in ys))
    return numerator / denominator if denominator else None
