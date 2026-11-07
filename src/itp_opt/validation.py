from __future__ import annotations

import csv
import ast
import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constraints import REPORT_CONSTRAINTS, assess
from .models import Configuration, EvaluationResult, Status

EXPECTED_FILES = ("building_data.csv", "processed_data.csv", "output_values.csv")

ALIASES = {
    "x1": {"x1", "slab_thickness", "floor_slab_thickness", "floor_thickness", "ground_floor_thickness"},
    "x2": {"x2", "ceiling_thickness", "roof_thickness"},
    "x3": {"x3", "ex_wall_thickness", "exterior_wall_thickness", "external_wall_thickness"},
    "x4": {"x4", "in_wall_thickness", "interior_wall_thickness", "internal_wall_thickness"},
    "x5": {"x5", "ex_win_area", "window_area"},
    "x6": {"x6", "ex_win_layers", "glass_layers", "number_of_glass_layers", "glazing_layers"},
    "x7": {"x7", "prim_door_area", "main_door_area", "main_entrance_door_area"},
    "x8": {"x8", "sec_door_area", "secondary_door_area", "side_door_area"},
    "window_g_value": {"window_g_value", "g_value", "solar_heat_gain_coefficient", "shgc"},
    "window_u_value": {"window_u_value", "u_value", "window_u_factor"},
    "energy_demand": {"energy_demand", "energy_requirement", "energy", "energy_consumption", "total_energy"},
    "energy_loss": {"energy_loss", "energy_losses", "heat_loss", "loss"},
    "heat_gain": {"heat_gain", "energy_gain", "gain"},
    "co2_emissions": {"co2_emissions", "co2_emission", "co2", "carbon_emissions"},
    "record_id": {"record_id", "id", "simulation_id", "case_id"},
}
INPUTS = ("x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8")
OPTIONAL_INPUTS = ("window_g_value", "window_u_value")
OBJECTIVES = ("energy_demand", "energy_loss", "heat_gain", "co2_emissions")


def _normalized(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_").replace("[", "").replace("]", "")


def canonical_name(name: str) -> str:
    normalized = _normalized(name)
    for canonical, aliases in ALIASES.items():
        if normalized in aliases:
            return canonical
    return normalized


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _number(value: str) -> float | None:
    text = value.strip().replace(",", ".")
    if not text:
        return None
    try:
        number = float(text)
        return number if math.isfinite(number) else None
    except ValueError:
        return None


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        sample = stream.read(4096)
        stream.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(stream, dialect=dialect)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        names = [canonical_name(name) for name in reader.fieldnames]
        if len(set(names)) != len(names):
            raise ValueError(f"Columns become ambiguous after normalization: {path}")
        rows = [{canonical_name(k): (v or "").strip() for k, v in row.items()} for row in reader]
    return names, rows


def inspect_csv(path: Path) -> dict[str, Any]:
    names, rows = read_csv(path)
    columns: dict[str, Any] = {}
    for name in names:
        values = [row[name] for row in rows]
        numbers = [_number(value) for value in values if value != ""]
        numeric = bool(numbers) and len(numbers) == sum(value != "" for value in values)
        columns[name] = {
            "missing": sum(value == "" for value in values),
            "type": "number" if numeric else "string",
            "min": min(numbers) if numeric else None,
            "max": max(numbers) if numeric else None,
            "unique": len(set(values)),
        }
    signatures = [json.dumps(row, sort_keys=True) for row in rows]
    return {
        "path": str(path), "sha256": sha256(path), "rows": len(rows),
        "columns": names, "column_statistics": columns,
        "duplicate_rows": sum(count - 1 for count in Counter(signatures).values() if count > 1),
    }


def validate_data_directory(data_dir: Path) -> dict[str, Any]:
    files: dict[str, Any] = {}
    issues: list[dict[str, str]] = []
    for filename in EXPECTED_FILES:
        path = data_dir / filename
        if not path.is_file():
            files[filename] = {"status": "MISSING"}
            issues.append({"severity": "ERROR", "code": "MISSING_FILE", "message": str(path)})
            continue
        try:
            files[filename] = {"status": "PRESENT", **inspect_csv(path)}
        except (OSError, ValueError, csv.Error) as exc:
            files[filename] = {"status": "INVALID", "error": str(exc)}
            issues.append({"severity": "ERROR", "code": "INVALID_CSV", "message": str(exc)})

    present = [entry for entry in files.values() if entry.get("status") == "PRESENT"]
    if present and not any(entry["rows"] == 30 for entry in present):
        issues.append({"severity": "WARNING", "code": "EXPECTED_ROW_COUNT_NOT_FOUND",
                       "message": "No supplied CSV contains exactly 30 records."})

    mapping = _mapping_assessment(data_dir, files)
    if not mapping["status"].startswith("VERIFIED"):
        issues.append({"severity": "ERROR", "code": "ROW_MAPPING_UNVERIFIED", "message": mapping["reason"]})
    consistency = _combined_consistency(data_dir)
    issues.extend(consistency.pop("issues"))
    return {
        "schema_version": 1,
        "expected_observations": 30,
        "files": files,
        "input_output_mapping": mapping,
        "combined_data_consistency": consistency,
        "units": {
            "x1": "mm (report VIII.1)", "x2": "mm (report VIII.1)",
            "x3": "mm (report VIII.1)", "x4": "mm (report VIII.1)",
            "x5": "m^2 (report VIII.1)", "x6": "count (report VIII.1)",
            "x7": "m^2 (report VIII.1)", "x8": "m^2 (report VIII.1)",
            "window_g_value": "dimensionless (physical meaning; not documented in report table)",
            "window_u_value": "W/(m^2*K) expected physically, but source unit is UNVERIFIED",
            **{name: "UNVERIFIED in supplied report/CSV" for name in OBJECTIVES},
        },
        "source_inconsistencies": {
            "duplicate_input_files": "building_data.csv and processed_data.csv are byte-identical"
                if ((data_dir / "building_data.csv").is_file() and (data_dir / "processed_data.csv").is_file()
                    and sha256(data_dir / "building_data.csv") == sha256(data_dir / "processed_data.csv")) else None,
            "report_vs_csv": (
                "Report scenario/numeric tables differ from CSV rows 9 and 15-30; see docs/source_inventory.md. "
                "The report has only x1-x8, while CSV/code add g- and U-values."
            ),
        },
        "issues": issues,
        "valid": not any(item["severity"] == "ERROR" for item in issues),
    }


def _mapping_assessment(data_dir: Path, file_reports: dict[str, Any]) -> dict[str, str]:
    # A combined row is self-contained. Separate files require explicit shared IDs; equal order alone is not proof.
    for filename, report in file_reports.items():
        columns = set(report.get("columns", []))
        if set(INPUTS).issubset(columns) and any(name in columns for name in OBJECTIVES):
            return {"status": "VERIFIED", "method": f"combined rows in {filename}",
                    "reason": "Inputs and outputs occur in each same CSV record."}
    candidates = []
    for filename, report in file_reports.items():
        if "record_id" in report.get("columns", []):
            _, rows = read_csv(data_dir / filename)
            candidates.append((filename, {row["record_id"] for row in rows}, len(rows)))
    if (len(candidates) >= 2
            and all(len(ids) == count for _, ids, count in candidates)
            and all(ids == candidates[0][1] for _, ids, _ in candidates[1:])):
        return {"status": "VERIFIED", "method": "shared unique record_id",
                "reason": "Separate files have identical unique record identifiers."}
    code_evidence = _historical_code_evidence(data_dir)
    if code_evidence["verified"]:
        return {
            "status": "VERIFIED_FOR_HISTORICAL_PYTHON",
            "method": "exact ordered arrays in input_data.py",
            "reason": (
                "input_data.py exactly reproduces both CSV sequences. This verifies the later Python pairing, "
                "but the report's input table conflicts with CSV rows 9 and 15-30, so physical provenance is disputed."
            ),
        }
    return {"status": "NON_EVALUABLE", "method": "none",
            "reason": "No combined input/output rows or verified shared unique record IDs were found."}


def _historical_code_evidence(data_dir: Path) -> dict[str, Any]:
    source = data_dir / "input_data.py"
    input_path, output_path = data_dir / "building_data.csv", data_dir / "output_values.csv"
    if not all(path.is_file() for path in (source, input_path, output_path)):
        return {"verified": False, "reason": "required files absent"}
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"))
        arrays: dict[str, list[float]] = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                target = node.targets[0] if isinstance(node, ast.Assign) else node.target
                value = node.value
                if isinstance(target, ast.Name) and isinstance(value, ast.List):
                    try:
                        arrays[target.id] = [float(ast.literal_eval(item)) for item in value.elts]
                    except (ValueError, TypeError):
                        pass
        _, input_rows = read_csv(input_path)
        _, output_rows = read_csv(output_path)
        names = {
            "slab_thickness": "x1", "ceiling_thickness": "x2", "ex_wall_thickness": "x3",
            "in_wall_thickness": "x4", "ex_win_area": "x5", "ex_win_layers": "x6",
            "prim_door_area": "x7", "sec_door_area": "x8", "window_g_value": "window_g_value",
            "window_u_value": "window_u_value", "energy_requirement": "energy_demand",
            "energy_losses": "energy_loss", "heat_gain": "heat_gain", "cO2_emission": "co2_emissions",
        }
        for variable, canonical in names.items():
            rows = input_rows if canonical in (*INPUTS, *OPTIONAL_INPUTS) else output_rows
            expected = arrays.get(variable)
            actual = [_number(row.get(canonical, "")) for row in rows]
            if expected is None or actual != expected:
                return {"verified": False, "reason": f"source mismatch for {variable}"}
        return {"verified": len(input_rows) == len(output_rows) == 30, "reason": "exact arrays"}
    except (OSError, SyntaxError, ValueError, csv.Error) as exc:
        return {"verified": False, "reason": str(exc)}


def _combined_consistency(data_dir: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"source": None, "conflicting_duplicate_configurations": 0,
                              "window_property_dependency": "NON_EVALUABLE", "issues": []}
    for filename in ("processed_data.csv", "building_data.csv", "output_values.csv"):
        path = data_dir / filename
        if not path.is_file():
            continue
        names, rows = read_csv(path)
        if not set(INPUTS).issubset(names):
            continue
        result["source"] = filename
        by_inputs: dict[tuple[str, ...], set[tuple[str, ...]]] = {}
        if any(name in names for name in OBJECTIVES):
            for row in rows:
                key = tuple(row.get(name, "") for name in (*INPUTS, *OPTIONAL_INPUTS))
                outputs = tuple(row.get(name, "") for name in OBJECTIVES)
                by_inputs.setdefault(key, set()).add(outputs)
        conflicts = sum(1 for outputs in by_inputs.values() if len(outputs) > 1)
        result["conflicting_duplicate_configurations"] = conflicts
        if conflicts:
            result["issues"].append({"severity": "ERROR", "code": "CONFLICTING_DUPLICATES",
                                     "message": f"{conflicts} input configurations have differing outputs."})
        if all(name in names for name in ("x6", "window_g_value", "window_u_value")):
            relations: dict[str, set[tuple[str, str]]] = {}
            for row in rows:
                relations.setdefault(row["x6"], set()).add((row["window_g_value"], row["window_u_value"]))
            result["window_property_dependency"] = (
                "CONSISTENT_FUNCTION_OF_GLASS_LAYER_COUNT_IN_OBSERVED_ROWS"
                if all(len(values) == 1 for values in relations.values())
                else "NOT_A_FUNCTION_OF_GLASS_LAYER_COUNT_ALONE"
            )
            result["window_property_pairs_by_x6"] = {
                key: sorted([list(pair) for pair in values]) for key, values in sorted(relations.items())
            }
        return result
    return result


def load_combined_observations(data_dir: Path) -> list[EvaluationResult]:
    for filename in ("processed_data.csv", "building_data.csv", "output_values.csv"):
        path = data_dir / filename
        if not path.is_file():
            continue
        names, rows = read_csv(path)
        if not set(INPUTS).issubset(names) or not any(name in names for name in OBJECTIVES):
            continue
        observations = []
        for index, row in enumerate(rows, start=1):
            values = {name: _number(row[name]) for name in (*INPUTS, *OPTIONAL_INPUTS) if row.get(name, "") != ""}
            if any(values.get(name) is None for name in INPUTS):
                continue
            configuration = Configuration.create(
                floor_slab=str(values["x1"]), ceiling=str(values["x2"]),
                exterior_wall=str(values["x3"]), interior_wall=str(values["x4"]),
                window="|".join(str(values.get(name, "")) for name in ("x5", "x6", "window_g_value", "window_u_value")),
                main_door=str(values["x7"]), secondary_door=str(values["x8"]), values=values,
            )
            objectives = {name: number for name in OBJECTIVES if (number := _number(row.get(name, ""))) is not None}
            status, constraint_results = assess(configuration, REPORT_CONSTRAINTS)
            observations.append(EvaluationResult(
                status, configuration, objectives,
                reason="; ".join(item.reason for item in constraint_results if item.status is not Status.ADMISSIBLE),
                provenance={"file": filename, "row": index},
            ))
        return observations
    evidence = _historical_code_evidence(data_dir)
    input_path, output_path = data_dir / "building_data.csv", data_dir / "output_values.csv"
    if evidence["verified"] and input_path.is_file() and output_path.is_file():
        _, input_rows = read_csv(input_path)
        _, output_rows = read_csv(output_path)
        observations = []
        for index, (inputs, outputs) in enumerate(zip(input_rows, output_rows, strict=True), start=1):
            values = {name: _number(inputs[name]) for name in (*INPUTS, *OPTIONAL_INPUTS)}
            configuration = Configuration.create(
                floor_slab=str(values["x1"]), ceiling=str(values["x2"]),
                exterior_wall=str(values["x3"]), interior_wall=str(values["x4"]),
                window="|".join(str(values[name]) for name in ("x5", "x6", "window_g_value", "window_u_value")),
                main_door=str(values["x7"]), secondary_door=str(values["x8"]), values=values,
            )
            objectives = {name: number for name in OBJECTIVES
                          if (number := _number(outputs.get(name, ""))) is not None}
            status, constraint_results = assess(configuration, REPORT_CONSTRAINTS)
            constraint_reason = "; ".join(
                item.reason for item in constraint_results if item.status is not Status.ADMISSIBLE)
            observations.append(EvaluationResult(
                status, configuration, objectives,
                reason=(f"{constraint_reason} Historical Python pairing is exact, but report inputs conflict "
                        "with CSV rows 9 and 15-30."),
                provenance={"input_file": "building_data.csv", "output_file": "output_values.csv",
                            "row": index, "mapping": "historical_python_order"},
            ))
        return observations
    return []
