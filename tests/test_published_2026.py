from decimal import Decimal as D
import json

from itp_opt import pso_penalty as source_2023
from itp_opt.published_2026 import (
    A, H, L3, L4, PENALTY_WEIGHT, TAU, audit_report, candidate_audit,
    c1_c3_x4_ceiling, domain_feasibility, minimum_feasible_area,
    minimum_feasible_tau, normalized_residuals, penalty_terms,
    sensitivity_report, table14_audit, wall_ratio,
)


def test_full_constraints_are_infeasible_even_over_r2():
    # Independent boundary substitution, not a comparison to report output.
    numerator = D(99000) * D(225) + D(45920) * D("112.5")
    assert numerator == D(27441000)
    assert numerator > D("0.15") * D(139880000)
    assert domain_feasibility()["c1_c2_c3"]["R2"]["feasible"] is False


def test_c1_c3_domain_distinction_and_unrestricted_witness():
    ceiling = c1_c3_x4_ceiling()
    assert ceiling < 0
    assert D("-28.16") < ceiling < D("-28.15")
    assert wall_ratio(D(225), ceiling) == TAU
    domains = domain_feasibility()["c1_c3"]
    assert domains["R2"]["feasible"] is True
    assert domains["x4_nonnegative"]["feasible"] is False
    assert domains["documented_wall_catalog"]["feasible"] is False


def test_area_and_threshold_boundaries_and_sensitivities():
    assert minimum_feasible_area() == D(182940000)
    assert minimum_feasible_tau() > D("0.196")
    assert minimum_feasible_tau() < D("0.197")
    values = sensitivity_report()
    assert values["feasibility_margin_tauA_minus_N_mm2"] == D(-6459000)
    assert values["d_margin_d_area"] == D("0.15")
    assert values["d_margin_d_tau"] == D(139880000)


def test_printed_candidate_residuals_and_penalties_by_elementary_formula():
    residuals = normalized_residuals(D("223.7"), D("112.4"))
    assert residuals["c1"] == D("1.3") / D("223.7")
    assert residuals["c2"] == D("0.1") / D("112.4")
    expected_c3 = (D(99000) * D("223.7") + D(45920) * D("112.4")) / D(139880000) - D("0.15")
    assert residuals["c3"] == expected_c3
    terms = penalty_terms(D("223.7"), D("112.4"))
    assert terms["p1"] == (D("1.3") / D("223.7")) ** 2
    assert terms["p2"] == (D("0.1") / D("112.4")) ** 2
    assert terms["p3"] == expected_c3 ** 2
    assert terms["p4"] is None


def test_all_three_violations_are_robust_to_coordinate_rounding():
    audit = candidate_audit()
    result = audit["rounding_robustness"]
    assert result["c1_violated_throughout"]
    assert result["c2_violated_throughout"]
    assert result["c3_violated_throughout"]
    # Direct worst-case checks avoid relying only on the implementation flag.
    assert D("223.75") < D(225)
    assert D("112.45") < D("112.5")
    assert (D(99000) * D("223.65") + D(45920) * D("112.35")) > D("0.15") * D(139880000)
    for comparison in audit["reported_penalty_comparison"]:
        assert comparison["exact_printed_coordinate_matches"] == [False, False, False]
        assert comparison["exact_substitution_classification"] == "CORRECTED"
        assert comparison["coordinate_rounding_box_compatible"] == [True, True, True]
        assert comparison["rounding_box_classification"] == "CONDITIONAL"


def test_table14_objective_arithmetic_and_rounding_intervals():
    rows = table14_audit()
    assert rows[0]["phi_plus_P_from_printed"] == D("16319.519")
    assert rows[0]["F_minus_printed_sum"] == D("0.090")
    assert rows[0]["objective_rounding_compatible"] is False
    assert rows[0]["objective_classification"] == "CONFIRMED"
    for row in rows[1:]:
        assert row["F_minus_printed_sum"] == D("-0.001")
        assert row["objective_rounding_compatible"] is True
        assert row["objective_classification"] == "CONDITIONAL"


def test_component_sums_respect_displayed_precision():
    rows = table14_audit()
    assert [row["weighted_printed_component_sum"] for row in rows] == [
        D("2076.8100000"), D("2077.0700000"), D("2077.1500000")]
    assert all(row["reported_P_compatible_with_component_precision"] for row in rows)
    assert all(row["component_sum_classification"] == "CONDITIONAL" for row in rows)
    assert PENALTY_WEIGHT == D("1e6")


def test_2023_and_2026_constants_are_separate():
    assert (H, L3, L4, A) == (D(3600), D(99000), D(45920), D(139880000))
    assert (source_2023.H, source_2023.L3, source_2023.L4, source_2023.A) == (
        D(3600), D(66950), D(47950), D(140530000))
    assert L3 != source_2023.L3 and A != source_2023.A


def test_json_is_reproducible_and_window_is_non_evaluable():
    first = json.dumps(audit_report(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(audit_report(), sort_keys=True, separators=(",", ":"))
    assert first == second
    window = audit_report()["published_candidate"]["window"]
    assert window["status"] == "NON_EVALUABLE"
    assert audit_report()["audit"]["decision"] == "HOLD"
