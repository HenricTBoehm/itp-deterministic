from __future__ import annotations

import csv
from pathlib import Path

from itp_opt.constraints import REPORT_CONSTRAINTS, assess
from itp_opt.enumeration import generate
from itp_opt.evaluators.energyplus import EnergyPlusEvaluator
from itp_opt.evaluators.observed import ObservedDataEvaluator
from itp_opt.models import Catalog, Configuration, ConstraintResult, EvaluationResult, Status
from itp_opt.optimization import exhaustive_search, grid_search
from itp_opt.validation import load_combined_observations, validate_data_directory


def configuration(suffix: str = "a") -> Configuration:
    return Configuration(f"f{suffix}", "c", "ew", "iw", "w", "m", "s")


def test_documented_catalog_has_reproducible_5184_configurations():
    first = list(generate(Catalog.documented_shape()))
    second = list(generate(Catalog.documented_shape()))
    assert len(first) == 5184
    assert first == second
    assert len({item.key() for item in first}) == 5184


def test_documented_catalog_is_empty_after_checkable_wall_constraints():
    statuses = [assess(item, REPORT_CONSTRAINTS)[0] for item in generate(Catalog.documented_shape())]
    assert set(statuses) == {Status.INADMISSIBLE}


def test_mandatory_constraint_statuses_are_enforced():
    config = configuration()
    blocked = lambda _: ConstraintResult("test", Status.INADMISSIBLE, "blocked")
    unknown = lambda _: ConstraintResult("test", Status.NON_EVALUABLE, "unknown")
    accepted = lambda _: ConstraintResult("test", Status.ADMISSIBLE, "ok")
    assert assess(config, [accepted])[0] is Status.ADMISSIBLE
    assert assess(config, [unknown])[0] is Status.NON_EVALUABLE
    assert assess(config, [unknown, blocked])[0] is Status.INADMISSIBLE


def test_observed_evaluator_never_predicts_unknown_case():
    known = configuration("known")
    evaluator = ObservedDataEvaluator([EvaluationResult(Status.ADMISSIBLE, known, {"energy_demand": 10.0})])
    assert evaluator.evaluate(known).objectives["energy_demand"] == 10.0
    assert evaluator.evaluate(configuration("unknown")).status is Status.NON_EVALUABLE


def test_conflicting_duplicate_is_non_evaluable():
    config = configuration()
    evaluator = ObservedDataEvaluator([
        EvaluationResult(Status.ADMISSIBLE, config, {"energy_demand": 1.0}),
        EvaluationResult(Status.ADMISSIBLE, config, {"energy_demand": 2.0}),
    ])
    assert evaluator.evaluate(config).status is Status.NON_EVALUABLE


def test_missing_energyplus_prerequisites_are_reported(tmp_path: Path):
    evaluator = EnergyPlusEvaluator(None, None, executable="certainly-not-energyplus")
    result = evaluator.evaluate(configuration())
    assert result.status is Status.NON_EVALUABLE
    assert "building model" in result.reason
    assert "weather file" in result.reason
    assert "executable" in result.reason


def test_known_global_minimum_on_synthetic_grid():
    point = grid_search(((-2.0, 2.0), (-2.0, 2.0)), (0.25, 0.25),
                        lambda x: (x[0] - 0.5) ** 2 + (x[1] + 1.0) ** 2)
    assert point.x == (0.5, -1.0)
    assert point.value == 0.0


def test_tie_breaking_is_deterministic():
    a, b = configuration("a"), configuration("b")
    evaluator = ObservedDataEvaluator([
        EvaluationResult(Status.ADMISSIBLE, b, {"energy_demand": 1.0}),
        EvaluationResult(Status.ADMISSIBLE, a, {"energy_demand": 1.0}),
    ])
    best1, _ = exhaustive_search([b, a], evaluator, "energy_demand")
    best2, _ = exhaustive_search([a, b], evaluator, "energy_demand")
    assert best1 == best2
    assert best1.configuration == a


def _write_combined(path: Path, count: int = 30):
    fields = [f"x{i}" for i in range(1, 9)] + ["window_g_value", "window_u_value", "energy_demand"]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for index in range(count):
            writer.writerow({**{f"x{i}": index + i / 10 for i in range(1, 9)},
                             "window_g_value": 0.5, "window_u_value": 2.0,
                             "energy_demand": 100 - index})


def test_imports_30_combined_records_with_correct_same_row_mapping(tmp_path: Path):
    _write_combined(tmp_path / "processed_data.csv")
    observations = load_combined_observations(tmp_path)
    report = validate_data_directory(tmp_path)
    assert len(observations) == 30
    assert observations[0].objectives["energy_demand"] == 100
    assert observations[-1].objectives["energy_demand"] == 71
    assert report["input_output_mapping"]["status"] == "VERIFIED"


def test_separate_rows_without_ids_are_not_silently_mapped(tmp_path: Path):
    (tmp_path / "building_data.csv").write_text("x1,x2,x3,x4,x5,x6,x7,x8\n1,2,3,4,5,6,7,8\n")
    (tmp_path / "output_values.csv").write_text("energy_demand\n10\n")
    report = validate_data_directory(tmp_path)
    assert report["input_output_mapping"]["status"] == "NON_EVALUABLE"
    assert load_combined_observations(tmp_path) == []


def test_supplied_historical_data_imports_30_rows_and_known_minimum():
    data = Path(__file__).parents[1] / "data" / "original"
    observations = load_combined_observations(data)
    report = validate_data_directory(data)
    assert len(observations) == 30
    assert report["input_output_mapping"]["status"] == "VERIFIED_FOR_HISTORICAL_PYTHON"
    assert min(item.objectives["energy_demand"] for item in observations) == 21489.245
