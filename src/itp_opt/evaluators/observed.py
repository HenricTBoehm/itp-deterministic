from __future__ import annotations

from collections.abc import Iterable

from ..models import Configuration, EvaluationResult, Status
from .base import EnergyEvaluator


class ObservedDataEvaluator(EnergyEvaluator):
    """Exact lookup only: deliberately performs no interpolation or extrapolation."""

    def __init__(self, observations: Iterable[EvaluationResult]):
        self._observations: dict[str, EvaluationResult] = {}
        self._conflicts: set[str] = set()
        for item in observations:
            key = item.configuration.key()
            prior = self._observations.get(key)
            if prior is not None and dict(prior.objectives) != dict(item.objectives):
                self._conflicts.add(key)
            else:
                self._observations[key] = item

    def evaluate(self, configuration: Configuration) -> EvaluationResult:
        key = configuration.key()
        if key in self._conflicts:
            return EvaluationResult(Status.NON_EVALUABLE, configuration,
                                    reason="Conflicting observed outputs for exact configuration.")
        result = self._observations.get(key)
        if result is None:
            return EvaluationResult(Status.NON_EVALUABLE, configuration,
                                    reason="Configuration is absent from observed simulations.")
        return result
