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