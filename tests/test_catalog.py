import json

import pytest

from src.loader import load_courses
from src.csp import build_csp
from src.search import brute_force, solve

ORDER = ["CSE518", "CSE340", "CSE330", "CSE250", "STA202", "CSE300", "CSC210", "CSE212",
         "STA102", "MAT248", "MAT305", "MAT281", "CSD102", "MGT111", "FAC114"]

# size -> number of valid timetables in the full catalog
EXPECTED = {4: 1, 6: 2, 8: 10, 10: 12, 12: 1, 15: 0}


def key(a):
    return tuple(sorted((c, s.id) for c, s in a.items()))


def test_starter_catalog_is_untouched():
    start = json.load(open("data/courses.json"))
    full = json.load(open("data/courses_full.json"))
    assert len(start) == 6
    assert full[:6] == start                      # existing data copied unchanged


def test_full_catalog_loads_and_validates():
    courses = load_courses("data/courses_full.json")   # loader rejects bad data
    assert len(courses) == 15
    assert set(ORDER) == set(courses)


def test_full_catalog_has_saturday_and_full_sections():
    courses = load_courses("data/courses_full.json")
    secs = [s for c in courses.values() for s in c.sections]
    assert any(sl.day == "Sat" for s in secs for sl in s.slots)
    assert any(s.seats == 0 for s in secs)


@pytest.mark.parametrize("n", sorted(EXPECTED))
def test_every_variant_matches_brute_force_at_each_size(n):
    csp = build_csp(load_courses("data/courses_full.json"), ORDER[:n])
    bf, stats = brute_force(csp)
    print(f"\nN={n}: brute force {len(bf)} solutions, {stats['combinations_checked']} combinations")
    assert len(bf) == EXPECTED[n]
    for cfg in [dict(), dict(use_fc=True), dict(use_fc=True, use_mrv=True),
                dict(use_fc=True, use_mrv=True, use_lcv=True),
                dict(use_ac3=True, use_fc=True, use_mrv=True, use_lcv=True)]:
        sols, _ = solve(csp, **cfg)
        assert sorted(map(key, sols)) == sorted(map(key, bf)), cfg