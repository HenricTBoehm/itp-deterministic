from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Configuration, EvaluationResult


class EnergyEvaluator(ABC):
    @abstractmethod
    def evaluate(self, configuration: Configuration) -> EvaluationResult:
        raise NotImplementedError
