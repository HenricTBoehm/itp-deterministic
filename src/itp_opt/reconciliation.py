from __future__ import annotations

import csv
from itertools import combinations
from pathlib import Path
from typing import Any

from .constraints import (
    EXTERIOR_WALL_LENGTH_MM,
    FLOOR_AREA_MM2,
    H_STORY_MM,
    INTERIOR_WALL_LENGTH_MM,
    REPORT_CONSTRAINTS,
    assess,
)
from .enumeration import generate
from .models import Catalog, Configuration, Status
from .validation import INPUTS, read_csv


def constraint_forensics() -> dict[str, Any]:
    candidates = list(generate(Catalog.documented_shape()))
    individual = {}
    for constraint in REPORT_CONSTRAINTS:
        counts = {status.value: 0 for status in Status}
        for candidate in candidates:
            counts[constraint(candidate).status.value] += 1
        individual[constraint.__name__] = counts

    checkable = REPORT_CONSTRAINTS[:3]
    subset_results = []
    infeasible: set[tuple[str, ...]] = set()
    for size in range(1, len(checkable) + 1):
        for subset in combinations(checkable, size):
            names = tuple(item.__name__ for item in subset)
            feasible_count = sum(assess(candidate, subset)[0] is Status.ADMISSIBLE for candidate in candidates)
            subset_results.append({"constraints": names, "feasible_configurations": feasible_count})
            if feasible_count == 0:
                infeasible.add(names)
    minimal = [
        names for names in sorted(infeasible, key=lambda value: (len(value), value))
        if all(tuple(item for item in names if item != removed) not in infeasible for removed in names)
    ]

    reference = Configuration.create(
        floor_slab="report_fixed_150", ceiling="report_fixed_11", exterior_wall="report_continuous",
        interior_wall="report_continuous", window="report_continuous", main_door="report_fixed_3.96",
        secondary_door="report_fixed_1.68",
        values={"x1": 150, "x2": 11, "x3": 291.5, "x4": 112.4, "x5": 1.2,
                "x6": 2, "x7": 3.96, "x8": 1.68},
    )
    reference_results = [constraint(reference) for constraint in REPORT_CONSTRAINTS]
    ratio = (291.5 * EXTERIOR_WALL_LENGTH_MM + 112.4 * INTERIOR_WALL_LENGTH_MM) / FLOOR_AREA_MM2
    return {
        "scope": (
            "Catalog-relative result under the transcribed formulas and units; not proof of physical impossibility."
        ),
        "catalog_size": len(candidates),
        "individual_constraint_counts": individual,
        "checkable_subset_feasibility": subset_results,
        "minimal_infeasible_constraint_subsets": minimal,
        "reference_solution": {
            "source": "Report X.2, published PSO run 1",
            "values": dict(reference.values),
            "continuous_bounds_status": {"x3": "PASS", "x4": "PASS", "x5": "PASS_AT_LOWER_BOUND"},
            "constraint_results": [
                {"name": item.name, "status": item.status.value, "reason": item.reason}
                for item in reference_results
            ],
            "wall_ratio": ratio,
            "wall_ratio_limit": 0.15,
            "wall_ratio_margin": 0.15 - ratio,
            "x3_minimum_margin_mm": 291.5 - H_STORY_MM / 16.0,
            "x4_minimum_margin_mm": 112.4 - H_STORY_MM / 32.0,
            "penalty_components_reconstructed": {
                "exterior_wall_squared": max(0.0, H_STORY_MM / (16 * 291.5) - 1) ** 2,
                "interior_wall_squared": max(0.0, H_STORY_MM / (32 * 112.4) - 1) ** 2,
                "wall_ratio_squared": max(0.0, ratio - 0.15) ** 2,
                "window_area_squared": "NON_EVALUABLE",
            },
            "conclusion": (
                "INADMISSIBLE under constraints 2 and 3 as transcribed; constraint 4 remains non-evaluable. "
                "The report itself presents a penalized, not strictly feasible, solution."
            ),
        },
        "unit_audit": {
            "constraint_1": "H_story and x3 are both mm: dimensionally consistent.",
            "constraint_2": "H_story and x4 are both mm: dimensionally consistent.",
            "constraint_3": "x*L gives mm^2 and A_floor is mm^2: dimensionless and consistent.",
            "constraint_4": (
                "Report x5 is m^2 while A_floor is stated in mm^2; conversion and the meaning/cardinality "
                "of sum(x5) are not documented."
            ),
        },
        "interpretation_risks": [
            "The report may use nominal layer thicknesses, structural thicknesses, or different reference planes.",
            "The catalog and continuous PSO define different design spaces.",
            "Formula rendering was cross-checked in PDF, but intended engineering semantics are not independently sourced.",
        ],
    }


def source_reconciliation(data_dir: Path, reference_path: Path) -> dict[str, Any]:
    _, csv_rows = read_csv(data_dir / "building_data.csv")
    _, report_rows = read_csv(reference_path)
    rows = []
    for index, (csv_row, report_row) in enumerate(zip(csv_rows, report_rows, strict=True), start=1):
        conflicts = [name for name in INPUTS if float(csv_row[name]) != float(report_row[name])]
        rows.append({
            "record_id": index,
            "status": "MATCH" if not conflicts else "DISPUTED",
            "conflicting_fields": conflicts,
            "csv_values": {name: float(csv_row[name]) for name in INPUTS},
            "report_values": {name: float(report_row[name]) for name in INPUTS},
            "reliability": (
                "CORROBORATED_BY_REPORT_AND_LATER_CODE" if not conflicts
                else "CONFLICTING_REPORT_VS_LATER_CODE"
            ),
        })
    return {
        "rows": rows,
        "counts": {
            "MATCH": sum(row["status"] == "MATCH" for row in rows),
            "DISPUTED": sum(row["status"] == "DISPUTED" for row in rows),
        },
        "provenance": {
            "report_values": (
                "Manual transcription of report VIII.2 scenario indices, cross-checked against VIII.3 numeric table."
            ),
            "csv_values": "building_data.csv; exactly reproduced by ordered arrays in input_data.py.",
            "outputs": (
                "output_values.csv sequence agrees with report VIII.3 and input_data.py, but has no record key."
            ),
            "correction_policy": "No source was modified and no disputed value was automatically selected.",
        },
    }


def write_source_csv(path: Path, reconciliation: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["record_id", "status", "reliability", "conflicting_fields"]
    fields += [f"csv_{name}" for name in INPUTS] + [f"report_{name}" for name in INPUTS]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in reconciliation["rows"]:
            writer.writerow({
                "record_id": row["record_id"], "status": row["status"],
                "reliability": row["reliability"],
                "conflicting_fields": "|".join(row["conflicting_fields"]),
                **{f"csv_{name}": row["csv_values"][name] for name in INPUTS},
                **{f"report_{name}": row["report_values"][name] for name in INPUTS},
            })
