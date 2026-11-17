import pytest

from src.loader import load_courses, load_preferences
from src.csp import build_csp, is_valid_schedule
from src.search import brute_force, solve
from src.ranking import rank_schedules
from src.scoring import score_schedule

ORDER = ["CSE518", "CSE340", "CSE330", "CSE250", "STA202", "CSE300",
         "CSC210", "CSE212", "STA102", "MAT248", "MAT305", "MAT281"]

# size -> number of valid timetables in the stress catalog
EXPECTED = {4: 156, 6: 1280, 8: 5760, 10: 3328, 12: 256}

CONFIGS = [dict(), dict(use_fc=True), dict(use_mrv=True),
           dict(use_fc=True, use_mrv=True),
           dict(use_fc=True, use_mrv=True, use_lcv=True),
           dict(use_ac3=True), dict(use_ac3=True, use_fc=True, use_mrv=True, use_lcv=True)]


def key(a):
    return tuple(sorted((c, s.id) for c, s in a.items()))


def stress():
    return load_courses("data/stress_catalog.json")


@pytest.mark.parametrize("n", [4, 6])
def test_all_variants_match_brute_force(n):
    csp = build_csp(stress(), ORDER[:n])
    bf, _ = brute_force(csp)
    assert len(bf) == EXPECTED[n]
    for cfg in CONFIGS:
        sols, _ = solve(csp, **cfg)
        assert sorted(map(key, sols)) == sorted(map(key, bf)), cfg


@pytest.mark.parametrize("n", [8, 10, 12])
def test_all_variants_agree_on_larger_sizes(n):
    csp = build_csp(stress(), ORDER[:n])
    ref, _ = solve(csp)
    assert len(ref) == EXPECTED[n]
    assert all(is_valid_schedule(s) for s in ref)
    for cfg in CONFIGS[1:]:
        sols, _ = solve(csp, **cfg)
        assert sorted(map(key, sols)) == sorted(map(key, ref)), cfg


def test_heuristics_reduce_work_at_10_courses():
    csp = build_csp(stress(), ORDER[:10])
    _, plain = solve(csp)
    _, best = solve(csp, use_fc=True, use_mrv=True)
    print(f"\nplain {plain}  |  FC+MRV {best}")
    assert best["nodes"] < plain["nodes"] / 5
    assert best["backtracks"] == 0


def test_full_sections_are_removed():
    csp = build_csp(stress(), ORDER[:6])
    assert "CSE340-5" not in [s.id for s in csp.domains["CSE340"]]
    assert "STA202-5" not in [s.id for s in csp.domains["STA202"]]


def test_direct_conflict_has_no_solution():
    csp = build_csp(stress(), ["CLA101", "CLA102"])
    for cfg in CONFIGS:
        assert solve(csp, **cfg)[0] == []


def test_course_clashing_with_every_cse518_section_is_impossible():
    csp = build_csp(stress(), ["CSE518", "FAC114"])
    assert brute_force(csp)[0] == []
    _, plain = solve(csp)
    sols, with_ac3 = solve(csp, use_ac3=True)
    print(f"\nIMPOSSIBLE: plain {plain}  |  AC-3 {with_ac3}")
    assert sols == []
    assert plain["nodes"] > 0
    assert with_ac3["nodes"] == 0               # AC-3 detects it before any search


def test_simple_feasible_case():
    csp = build_csp(stress(), ["STA102", "MAT281"])
    sols, _ = solve(csp)
    assert len(sols) == 4 and all(is_valid_schedule(s) for s in sols)


def test_top_three_are_valid_and_sorted():
    csp = build_csp(stress(), ORDER[:6])
    sols, _ = solve(csp, use_fc=True, use_mrv=True)
    prefs = load_preferences("data/preferences.json")
    top = rank_schedules(sols, prefs, top_n=3)
    assert len(top) == 3
    assert [s.score for s in top] == sorted((s.score for s in top), reverse=True)
    assert all(is_valid_schedule(s.assignment) for s in top)


def test_preference_weights_change_the_winner():
    csp = build_csp(stress(), ORDER[:6])
    sols, _ = solve(csp, use_fc=True, use_mrv=True)
    prefs = dict(load_preferences("data/preferences.json"), avoid_before="12:00",
                 weights={"days_off": 0, "early": 1, "gaps": 0, "compact": 0})
    top = rank_schedules(sols, prefs, top_n=1)[0]
    best_possible = max(score_schedule(s, prefs)[1]["early"] for s in sols)
    assert top.breakdown["early"] == best_possible