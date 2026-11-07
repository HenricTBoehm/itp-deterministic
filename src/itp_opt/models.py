from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping


class Status(str, Enum):
    ADMISSIBLE = "ADMISSIBLE"
    INADMISSIBLE = "INADMISSIBLE"
    NON_EVALUABLE = "NON_EVALUABLE"


@dataclass(frozen=True, order=True)
class Configuration:
    floor_slab: str
    ceiling: str
    exterior_wall: str
    interior_wall: str
    window: str
    main_door: str
    secondary_door: str
    values: tuple[tuple[str, float | int | str], ...] = ()

    @classmethod
    def create(cls, *, values: Mapping[str, Any] | None = None, **parts: str) -> "Configuration":
        normalized = tuple(sorted((str(k), v) for k, v in (values or {}).items()))
        return cls(values=normalized, **parts)

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result.pop("values")
        result.update(dict(self.values))
        return result

    def key(self) -> str:
        fields = self.as_dict()
        return "|".join(f"{k}={fields[k]}" for k in sorted(fields))


@dataclass(frozen=True)
class ConstraintResult:
    name: str
    status: Status
    reason: str
    mandatory: bool = True


@dataclass(frozen=True)
class EvaluationResult:
    status: Status
    configuration: Configuration
    objectives: Mapping[str, float] = field(default_factory=dict)
    reason: str = ""
    provenance: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Catalog:
    floor_slabs: tuple[str, ...]
    ceilings: tuple[str, ...]
    exterior_walls: tuple[str, ...]
    interior_walls: tuple[str, ...]
    windows: tuple[str, ...]
    main_doors: tuple[str, ...]
    secondary_doors: tuple[str, ...]

    @classmethod
    def documented_shape(cls) -> "Catalog":
        """Catalog titles transcribed from report section VIII.1."""
        walls = ("Brick Wall_100", "Brick Wall_150", "Brick Wall_200", "Brick Wall_250")
        return cls(
            ("Concrete slab_130", "Concrete slab_150", "Concrete slab_200"),
            ("Panels_10", "Panels_13", "Panels_15"), walls, walls,
            ("S6_1015_2HDL", "S6_1215_2HDL", "S6_1415_2HDL",
             "D6_1015_2HDL", "D6_1215_2HDL", "D6_1415_2HDL"),
            ("1622_2HDL", "1822_2HDL", "2022_2HDL"),
            ("0621_1HDL", "0821_1HDL"),
        )
