from .models import Schedule
from .csp import is_valid_schedule
from .scoring import score_schedule


def rank_schedules(solutions, prefs, top_n=3):
    """Score every valid solution and return the best top_n Schedule objects.

    Ties are broken by section ids so the output is the same on every run."""
    ranked = []
    for assignment in solutions:
        if not is_valid_schedule(assignment):      # independent re-check
            raise ValueError("Solver returned an invalid schedule")
        total, breakdown = score_schedule(assignment, prefs)
        ranked.append(Schedule(assignment, round(total, 4), breakdown))

    def sort_key(s):
        ids = tuple(sec.id for _, sec in sorted(s.assignment.items()))
        return (-s.score, ids)

    ranked.sort(key=sort_key)
    return ranked[:top_n]