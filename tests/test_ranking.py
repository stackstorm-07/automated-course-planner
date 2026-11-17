import pytest

from src.loader import load_courses, load_preferences
from src.csp import build_csp
from src.search import solve
from src.ranking import rank_schedules
from src.explain_agent import explain


def setup():
    courses = load_courses("data/courses.json")
    prefs = load_preferences("data/preferences.json")
    csp = build_csp(courses, prefs["selected"])
    sols, _ = solve(csp, use_fc=True, use_mrv=True, use_ac3=True)
    return courses, prefs, sols


def test_best_schedule_first_and_values_checked_by_hand():
    _, prefs, sols = setup()
    top = rank_schedules(sols, prefs)
    print("\nRANKING:", [(s.assignment["STA202"].id, s.score) for s in top])
    assert [s.assignment["STA202"].id for s in top] == ["STA202-2", "STA202-1"]
    assert top[0].score == 0.75
    assert top[1].score == 0.35
    assert top[0].breakdown["days_off"] == 1.0     # Friday is free
    assert top[1].breakdown["days_off"] == 0.0     # STA202-1 meets on Friday


def test_scores_between_0_and_1():
    _, prefs, sols = setup()
    for s in rank_schedules(sols, prefs):
        assert 0 <= s.score <= 1
        assert all(0 <= v <= 1 for v in s.breakdown.values())


def test_ranking_is_deterministic():
    _, prefs, sols = setup()
    ids = lambda top: [tuple(sec.id for sec in s.assignment.values()) for s in top]
    assert ids(rank_schedules(sols, prefs)) == ids(rank_schedules(list(reversed(sols)), prefs))


def test_fewer_than_three_results_is_fine():
    _, prefs, sols = setup()
    assert len(rank_schedules(sols, prefs, top_n=3)) == 2
    assert rank_schedules([], prefs) == []


def test_weights_change_the_order():
    _, prefs, sols = setup()
    prefs = dict(prefs, weights={"days_off": 0, "early": 0, "gaps": 1, "compact": 0})
    top = rank_schedules(sols, prefs)
    assert top[0].breakdown["gaps"] >= top[1].breakdown["gaps"]


def test_invalid_schedule_is_rejected():
    courses, prefs, _ = setup()
    bad = {"CSE340": courses["CSE340"].sections[0], "CSE330": courses["CSE330"].sections[0]}
    with pytest.raises(ValueError):
        rank_schedules([bad], prefs)


def test_milans_explanation_accepts_real_schedules():
    _, prefs, sols = setup()
    top = rank_schedules(sols, prefs)
    text = explain(top[0], use_llm=False)
    assert "CSE518" in text