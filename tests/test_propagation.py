import pytest

from src.loader import load_courses, load_preferences
from src.csp import build_csp
from src.propagation import ac3
from src.search import brute_force, solve


def make_csp():
    courses = load_courses("data/courses.json")
    prefs = load_preferences("data/preferences.json")
    return build_csp(courses, prefs["selected"])


def key(assignment):
    return tuple(sorted((c, s.id) for c, s in assignment.items()))


def test_ac3_prunes_expected_sections():
    domains, removed = ac3(make_csp())
    ids = {v: [s.id for s in d] for v, d in domains.items()}
    print(f"\nAC-3 removed: {removed}")
    assert len(removed) == 4
    assert ids["CSE340"] == ["CSE340-2"]
    assert ids["CSE518"] == ["CSE518-1"]
    assert ids["STA202"] == ["STA202-1", "STA202-2"]


@pytest.mark.parametrize("fc,mrv,lcv", [
    (False, False, False),
    (True, True, False),
    (True, True, True),
])
def test_ac3_never_loses_solutions(fc, mrv, lcv):
    csp = make_csp()
    bf, _ = brute_force(csp)
    sols, stats = solve(csp, use_fc=fc, use_mrv=mrv, use_lcv=lcv, use_ac3=True)
    print(f"\nAC3 + FC={fc} MRV={mrv} LCV={lcv}: {len(sols)} solutions, {stats}")
    assert sorted(map(key, sols)) == sorted(map(key, bf))


def test_ac3_reduces_nodes():
    csp = make_csp()
    _, plain = solve(csp)
    _, with_ac3 = solve(csp, use_ac3=True)
    assert with_ac3["nodes"] < plain["nodes"]


def test_ac3_detects_impossible_without_search():
    csp = make_csp()
    csp.domains["CSE340"] = [s for s in csp.domains["CSE340"] if s.id == "CSE340-1"]
    _, plain = solve(csp)
    sols, with_ac3 = solve(csp, use_ac3=True)
    print(f"\nIMPOSSIBLE case: plain {plain}  |  AC-3 {with_ac3}")
    assert sols == []
    assert with_ac3["nodes"] == 0