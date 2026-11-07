from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from ..models import Configuration, EvaluationResult, Status
from .base import EnergyEvaluator


class EnergyPlusEvaluator(EnergyEvaluator):
    def __init__(self, model: Path | None, weather: Path | None, executable: str = "energyplus",
                 output_dir: Path = Path("results/energyplus")):
        self.model = model
        self.weather = weather
        self.executable = executable
        self.output_dir = output_dir

    def prerequisites(self) -> list[str]:
        missing = []
        if not self.model or not self.model.is_file():
            missing.append("EnergyPlus building model (.idf/.epJSON)")
        if not self.weather or not self.weather.is_file():
            missing.append("EnergyPlus weather file (.epw)")
        if shutil.which(self.executable) is None:
            missing.append(f"EnergyPlus executable: {self.executable}")
        return missing

    def evaluate(self, configuration: Configuration) -> EvaluationResult:
        missing = self.prerequisites()
        if missing:
            return EvaluationResult(Status.NON_EVALUABLE, configuration,
                                    reason="Missing prerequisites: " + ", ".join(missing))
        # Safe refusal: changing arbitrary IDF construction fields requires a verified mapping.
        return EvaluationResult(
            Status.NON_EVALUABLE, configuration,
            reason="No verified mapping from configuration fields to EnergyPlus model objects is available.",
            provenance={"model": str(self.model), "weather": str(self.weather)},
        )

    def cache_key(self, configuration: Configuration) -> str:
        digest = hashlib.sha256()
        digest.update(configuration.key().encode())
        for path in (self.model, self.weather):
            if path and path.is_file():
                digest.update(hashlib.sha256(path.read_bytes()).digest())
        executable = shutil.which(self.executable)
        digest.update((executable or self.executable).encode())
        return digest.hexdigest()
