"""Soft-constraint scoring. Every term is normalised to 0..1 (1 = best).
Scoring never decides validity; it only ranks schedules that are already valid."""

ALL_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def to_minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _slots_by_day(assignment):
    by_day = {}
    for sec in assignment.values():
        for sl in sec.slots:
            by_day.setdefault(sl.day, []).append(sl)
    for slots in by_day.values():
        slots.sort(key=lambda s: s.start)
    return by_day


def score_days_off(assignment, prefs):
    wanted = prefs.get("preferred_days_off", [])
    if not wanted:
        return 1.0
    used = set(_slots_by_day(assignment))
    return sum(1 for d in wanted if d not in used) / len(wanted)


def score_early(assignment, prefs):
    limit = to_minutes(prefs.get("avoid_before", "00:00"))
    slots = [sl for sec in assignment.values() for sl in sec.slots]
    early = sum(1 for sl in slots if sl.start < limit)
    return 1 - early / len(slots)


def score_gaps(assignment, prefs):
    max_gap = prefs.get("max_gap_minutes", 120)
    gaps = []
    for slots in _slots_by_day(assignment).values():
        for a, b in zip(slots, slots[1:]):
            gaps.append(max(0, b.start - a.end))
    gaps = [g for g in gaps if g > 0]      # back-to-back classes are not a gap
    if not gaps:
        return 1.0
    return sum(1 for g in gaps if g <= max_gap) / len(gaps)


def score_compact(assignment, prefs):
    days_used = len(_slots_by_day(assignment))
    return (len(ALL_DAYS) - days_used) / (len(ALL_DAYS) - 1)


TERMS = {
    "days_off": score_days_off,
    "early": score_early,
    "gaps": score_gaps,
    "compact": score_compact,
}


def score_schedule(assignment, prefs):
    """Return (total, breakdown). total is the weighted average of the terms."""
    weights = prefs.get("weights", {})
    breakdown = {name: fn(assignment, prefs) for name, fn in TERMS.items()}
    total_weight = sum(weights.get(n, 0) for n in TERMS)
    if total_weight == 0:
        return 0.0, breakdown
    total = sum(weights.get(n, 0) * v for n, v in breakdown.items()) / total_weight
    return total, breakdown