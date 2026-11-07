from pathlib import Path

from itp_opt.reconciliation import constraint_forensics, source_reconciliation


def test_constraint_counts_and_minimal_infeasible_subset():
    result = constraint_forensics()
    assert result["individual_constraint_counts"]["exterior_wall_minimum"]["INADMISSIBLE"] == 3888
    assert result["individual_constraint_counts"]["interior_wall_minimum"]["INADMISSIBLE"] == 1296
    assert result["individual_constraint_counts"]["wall_area_ratio"]["INADMISSIBLE"] == 2268
    assert result["minimal_infeasible_constraint_subsets"] == [
        ("exterior_wall_minimum", "wall_area_ratio")
    ]


def test_report_reference_solution_is_not_strictly_feasible():
    result = constraint_forensics()["reference_solution"]
    statuses = {item["name"]: item["status"] for item in result["constraint_results"]}
    assert statuses["exterior_wall_minimum"] == "ADMISSIBLE"
    assert statuses["interior_wall_minimum"] == "INADMISSIBLE"
    assert statuses["wall_area_ratio"] == "INADMISSIBLE"
    assert statuses["total_window_area"] == "NON_EVALUABLE"


def test_source_reconciliation_has_17_disputed_rows():
    root = Path(__file__).parents[1]
    result = source_reconciliation(root / "data/original", root / "data/reference/report_scenarios.csv")
    assert result["counts"] == {"MATCH": 13, "DISPUTED": 17}
    assert [row["record_id"] for row in result["rows"] if row["status"] == "DISPUTED"] == [
        9, *range(15, 31)
    ]
