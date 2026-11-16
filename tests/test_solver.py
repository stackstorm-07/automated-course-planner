from src.loader import load_courses, load_preferences
from src.csp import build_csp, is_valid_schedule
from src.search import brute_force, solve


def make_csp():
    courses = load_courses("data/courses.json")
    prefs = load_preferences("data/preferences.json")
    return build_csp(courses, prefs["selected"])


def key(assignment):
    return tuple(sorted((c, s.id) for c, s in assignment.items()))


def test_matches_brute_force():
    csp = make_csp()
    bf, _ = brute_force(csp)
    sols, stats = solve(csp)
    print(f"\nPLAIN BACKTRACKING: {len(sols)} solutions, {stats}")
    assert sorted(map(key, sols)) == sorted(map(key, bf))


def test_all_solutions_valid():
    sols, _ = solve(make_csp())
    assert all(is_valid_schedule(s) for s in sols)


def test_impossible_case_returns_empty():
    csp = make_csp()
    csp.domains["CSE340"] = [s for s in csp.domains["CSE340"] if s.id == "CSE340-1"]
    sols, _ = solve(csp)
    assert sols == []

def test_forward_checking_matches_and_prunes():
    csp = make_csp()
    bf, _ = brute_force(csp)
    plain, plain_stats = solve(csp)
    fc, fc_stats = solve(csp, use_fc=True)
    print(f"\nPLAIN: {plain_stats}  |  FORWARD CHECKING: {fc_stats}")
    assert sorted(map(key, fc)) == sorted(map(key, bf))
    assert fc_stats["nodes"] < plain_stats["nodes"]

import pytest

@pytest.mark.parametrize("fc,mrv,lcv", [
    (False, False, False),
    (True, False, False),
    (False, True, False),
    (True, True, False),
    (True, True, True),
])
def test_every_variant_matches_brute_force(fc, mrv, lcv):
    csp = make_csp()
    bf, _ = brute_force(csp)
    sols, stats = solve(csp, use_fc=fc, use_mrv=mrv, use_lcv=lcv)
    print(f"\nFC={fc} MRV={mrv} LCV={lcv}: {len(sols)} solutions, {stats}")
    assert sorted(map(key, sols)) == sorted(map(key, bf))


def test_mrv_reduces_nodes():
    csp = make_csp()
    _, fc_only = solve(csp, use_fc=True)
    _, with_mrv = solve(csp, use_fc=True, use_mrv=True)
    assert with_mrv["nodes"] < fc_only["nodes"]