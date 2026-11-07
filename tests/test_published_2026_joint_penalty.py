from decimal import Decimal as D
import json

from itp_opt.published_2026 import (
    H, TABLE14, coordinate_interval_from_penalty, invert_violated_penalty,
    joint_penalty_audit, joint_penalty_report, known_penalty_from_components,
    significant_digits_interval,
)


def test_violated_branch_inversion_is_independent_identity():
    p1 = D("0.0000357")
    x3 = invert_violated_penalty(D(225), p1)
    assert x3 < D(225)
    assert abs((D(225) / x3 - 1) ** 2 - p1) < D("1e-48")
    p2 = D("0.00000111")
    x4 = invert_violated_penalty(D("112.5"), p2)
    assert abs((D("112.5") / x4 - 1) ** 2 - p2) < D("1e-48")


def test_three_significant_digit_intervals():
    assert significant_digits_interval(D("3.57e-5")) == (D("3.565e-5"), D("3.575e-5"))
    assert significant_digits_interval(D("1.11e-6")) == (D("1.105e-6"), D("1.115e-6"))
    assert significant_digits_interval(D("2.04e-3")) == (D("2.035e-3"), D("2.045e-3"))


def test_penalty_inversion_reverses_interval_and_fits_coordinate_printing():
    p_interval = (D("3.565e-5"), D("3.575e-5"))
    x_interval = coordinate_interval_from_penalty(H / D(16), p_interval)
    assert x_interval[0] < x_interval[1]
    assert D("223.65") <= x_interval[0] < x_interval[1] < D("223.75")


def test_certified_joint_bounds_match_independent_numerical_brackets():
    expected = (
        (D("2078.988216178383"), D("2079.013039049142")),
        (D("2078.917318430838"), D("2078.941382970343")),
        (D("2078.909674639024"), D("2078.933702985320")),
    )
    for row, bounds in zip(TABLE14, expected):
        audit = joint_penalty_audit(row)
        assert audit["known_penalty_certified_outward_bounds"] == bounds
        assert audit["monotonicity_certificate"]["strictly_decreasing_in_p1_and_p2"]
        assert audit["monotonicity_certificate"]["partial_derivative_upper_bounds"]["d_dp1"] < 0
        assert audit["monotonicity_certificate"]["partial_derivative_upper_bounds"]["d_dp2"] < 0


def test_endpoint_order_follows_strict_monotonicity_not_four_corner_search():
    row = TABLE14[0]
    p1_low, p1_high = significant_digits_interval(row["components"][0])
    p2_low, p2_high = significant_digits_interval(row["components"][1])
    lower = known_penalty_from_components(p1_high, p2_high)
    upper = known_penalty_from_components(p1_low, p2_low)
    middle_a = known_penalty_from_components(p1_low, p2_high)
    middle_b = known_penalty_from_components(p1_high, p2_low)
    assert lower < middle_a < upper
    assert lower < middle_b < upper


def test_all_runs_jointly_satisfy_coordinate_and_p3_intervals():
    for row in TABLE14:
        audit = joint_penalty_audit(row)
        assert audit["coordinate_intersections_nonempty"]
        assert audit["p3_simultaneously_compatible"]
        low, high = audit["p3_bounds"]
        assert D("0.002035") <= low <= high < D("0.002045")


def test_nonnegative_p4_makes_run1_impossible_but_runs2_and3_compatible():
    audits = [joint_penalty_audit(row) for row in TABLE14]
    assert audits[0]["classification"] == "CONFIRMED_INCONSISTENCY"
    assert audits[0]["display_intervals"]["P"][1] < audits[0]["known_penalty_raw_extrema"]["lower"]
    assert audits[0]["p4"]["known_fact"] == "p4 >= 0"
    assert [item["classification"] for item in audits[1:]] == [
        "CONDITIONALLY_COMPATIBLE", "CONDITIONALLY_COMPATIBLE"]
    assert all(item["simultaneous_total_interval"] is not None for item in audits[1:])


def test_f_phi_and_2078_988_hypothesis_are_jointly_assessed():
    report = joint_penalty_report()
    run1 = report["runs"][0]
    assert run1["display_intervals"]["P"][1] < run1["display_intervals"]["F_minus_phi"][0]
    hypothesis = report["run1_transcription_hypothesis"]
    assert hypothesis["F_minus_phi_central"] == "2078.988"
    assert hypothesis["classification"] == "CONDITIONALLY_COMPATIBLE"
    assert hypothesis["simultaneous_interval"] is not None


def test_joint_report_is_deterministic_and_does_not_reconstruct_coordinates():
    first = json.dumps(joint_penalty_report(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(joint_penalty_report(), sort_keys=True, separators=(",", ":"))
    assert first == second
    assert all(not run["historical_coordinates_reconstructed"]
               for run in joint_penalty_report()["runs"])
    assert joint_penalty_report()["audit"]["decision"] == "READY_FOR_REVIEW"
