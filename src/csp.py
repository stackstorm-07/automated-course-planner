from itertools import product

def slots_overlap(a, b):
    # back-to-back (a.end == b.start) is NOT an overlap
    return a.day == b.day and a.start < b.end and b.start < a.end

def sections_conflict(s1, s2):
    return any(slots_overlap(a, b) for a, b in product(s1.slots, s2.slots))
from dataclasses import dataclass


@dataclass
class CSP:
    variables: list   # course codes, e.g. ["CSE518", "CSE340"]
    domains: dict     # course code -> list of Section objects
    credits: dict     # course code -> credits


def build_csp(courses, selected):
    missing = [c for c in selected if c not in courses]
    if missing:
        raise ValueError(f"Unknown courses: {missing}")

    # Node consistency: drop full sections (seats == 0) up front
    domains = {
        c: [s for s in courses[c].sections if s.seats > 0]
        for c in selected
    }
    return CSP(list(selected), domains, {c: courses[c].credits for c in selected})


def is_consistent(assignment, section):
    """Can `section` be added to a partial assignment without a clash?"""
    return all(not sections_conflict(section, other) for other in assignment.values())


def is_valid_schedule(assignment):
    """Independent checker: is a complete assignment free of all clashes?"""
    secs = list(assignment.values())
    return all(
        not sections_conflict(secs[i], secs[j])
        for i in range(len(secs))
        for j in range(i + 1, len(secs))
    )