from decimal import Decimal as D
import json

from itp_opt.pso_penalty import (
    analytic_continuous_vertices,
    c1,
    c2,
    c3,
    catalog_subset_feasibility,
    clipped_continuous_vertices,
    infer_x3_from_total,
    infer_x4_from_p2,
    minimal_infeasible_subsets,
    penalty_terms,
    reconstruction_report,
    rounds_to_one_decimal,
    wall_ratio,
)


def test_exact_penalty_from_printed_coordinates():
    terms = penalty_terms(D("291.5"), D("112.4"))
    assert terms["p1"] == 0
    assert D("7.9152e-7") < terms["p2"] < D("7.9154e-7")
    assert D("7.4122e-4") < terms["p3"] < D("7.4124e-4")
    assert terms["p2"] != D("2.42e-7")


def test_conditional_inverse_of_reported_p2_and_rounding():
    inferred = infer_x4_from_p2(D("2.42e-7"))
    assert D("112.444684528") < inferred < D("112.444684530")
    assert rounds_to_one_decimal(inferred) == D("112.4")
    assert D("0.05531547") < D("112.5") - inferred < D("0.05531548")
    assert abs(penalty_terms(D("291.5"), inferred)["p2"] - D("2.42e-7")) < D("1e-48")


def test_reported_p2_rounding_interval_maps_inside_printed_coordinate_interval():
    lower_x4 = infer_x4_from_p2(D("2.425e-7"))
    upper_x4 = infer_x4_from_p2(D("2.415e-7"))
    assert D("112.35") <= lower_x4 <= upper_x4 < D("112.45")
    assert rounds_to_one_decimal(lower_x4) == rounds_to_one_decimal(upper_x4) == D("112.4")


def test_c3_violation_is_stable_for_printed_and_inferred_x4():
    inferred = infer_x4_from_p2(D("2.42e-7"))
    rounded_terms = penalty_terms(D("291.5"), D("112.4"))
    inferred_terms = penalty_terms(D("291.5"), inferred)
    assert c3(D("291.5"), D("112.4")) is False
    assert c3(D("291.5"), inferred) is False
    assert D("7.41e-4") < rounded_terms["p3"] < D("7.43e-4")
    assert D("7.41e-4") < inferred_terms["p3"] < D("7.43e-4")
    assert wall_ratio(D("291.45"), D("112.35")) > D("0.15")


def test_catalog_mus_and_all_proper_subsets():
    feasibility = catalog_subset_feasibility()
    assert minimal_infeasible_subsets() == [("c1", "c3")]
    assert feasibility[("c1", "c3")] == []
    assert (D(250), D(100)) in feasibility[("c1",)]
    assert (D(100), D(100)) in feasibility[("c3",)]
    assert feasibility[()]  # Empty proper subset is feasible.
    assert feasibility[("c1", "c2")]
    assert feasibility[("c2", "c3")]


def test_elementary_catalog_contradiction():
    # c1 leaves only x3=250; c3 is then best at catalog-minimum x4=100 and still fails.
    assert c1(D(250), D(100))
    assert D("0.15322351099409") < wall_ratio(D(250), D(100)) < D("0.15322351099410")
    assert not c3(D(250), D(100))


def test_continuous_region_vertices_by_two_independent_methods():
    analytic = analytic_continuous_vertices()
    clipped = clipped_continuous_vertices()
    assert len(analytic) == len(clipped) == 3
    for expected in analytic:
        assert any(abs(expected[0] - actual[0]) < D("1e-44")
                   and abs(expected[1] - actual[1]) < D("1e-44") for actual in clipped)
        assert c1(*expected) and c2(*expected) and c3(*expected)
    assert (D("225"), D("112.5")) in analytic


def test_joint_conditional_coordinates_reproduce_total_but_are_not_recovered_values():
    p2 = D("2.42e-7")
    x4 = infer_x4_from_p2(p2)
    x3 = infer_x3_from_total(D("742.210"), p2, x4)
    total = sum(penalty_terms(x3, x4).values()) * D("1e6")
    assert abs(total - D("742.210")) < D("1e-44")
    assert rounds_to_one_decimal(x3) == D("291.5")
    assert rounds_to_one_decimal(x4) == D("112.4")


def test_reconstruction_is_byte_reproducible_and_window_stays_non_evaluable():
    first = json.dumps(reconstruction_report(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(reconstruction_report(), sort_keys=True, separators=(",", ":"))
    assert first == second
    assert reconstruction_report()["test_f_window"]["status"] == "NON_EVALUABLE"
