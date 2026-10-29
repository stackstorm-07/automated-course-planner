import pytest

from src.loader import load_courses, load_preferences
from src.csp import build_csp, is_valid_schedule
from src.search import brute_force


def make_csp():
    courses = load_courses("data/courses.json")
    prefs = load_preferences("data/preferences.json")
    return courses, build_csp(courses, prefs["selected"])


def test_full_section_removed():
    # CSE340-3 has 0 seats, so node consistency must drop it
    _, csp = make_csp()
    ids = [s.id for s in csp.domains["CSE340"]]
    assert "CSE340-3" not in ids
    assert ids == ["CSE340-1", "CSE340-2"]


def test_brute_force_only_returns_valid_schedules():
    _, csp = make_csp()
    solutions, _ = brute_force(csp)
    assert len(solutions) > 0
    assert all(is_valid_schedule(s) for s in solutions)


def test_baseline_count():
    # This is the number every optimized solver must match exactly
    _, csp = make_csp()
    solutions, stats = brute_force(csp)
    print(f"\nBASELINE: {len(solutions)} solutions, "
          f"{stats['combinations_checked']} combinations checked")
    assert stats["combinations_checked"] == 32
    assert len(solutions) == 2


def test_impossible_case_returns_empty():
    # CSE340-1 and CSE330-1 clash, and CSE330 has only one section
    _, csp = make_csp()
    csp.domains["CSE340"] = [s for s in csp.domains["CSE340"] if s.id == "CSE340-1"]
    solutions, _ = brute_force(csp)
    assert solutions == []


def test_unknown_course_raises():
    courses, _ = make_csp()
    with pytest.raises(ValueError):
        build_csp(courses, ["CSE518", "XYZ999"])