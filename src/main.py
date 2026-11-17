import sys

from src.loader import load_courses, load_preferences
from src.csp import build_csp
from src.search import solve
from src.ranking import rank_schedules
from src.display import render_calendar, render_no_solution, confirm_schedules
from src.explain_agent import explain


def main():
    courses = load_courses("data/courses.json")
    prefs = load_preferences("data/preferences.json")
    csp = build_csp(courses, prefs["selected"])

    solutions, stats = solve(csp, use_fc=True, use_mrv=True, use_lcv=True, use_ac3=True)
    print(f"Valid timetables found: {len(solutions)}   solver stats: {stats}")

    if not solutions:
        print(render_no_solution(prefs["selected"]))
        return

    top = rank_schedules(solutions, prefs, top_n=3)
    explain_fn = lambda s: explain(s, use_llm=False)

    if "--confirm" in sys.argv:
        chosen = confirm_schedules(top, explain_fn)
        print("Accepted:", {c: s.id for c, s in chosen.assignment.items()} if chosen else "none")
        return

    for i, sched in enumerate(top, start=1):
        print()
        print(render_calendar(sched, title=f"Option {i} of {len(top)}"))
        print()
        print("Score breakdown:", {k: round(v, 2) for k, v in sched.breakdown.items()})
        print(explain_fn(sched))


if __name__ == "__main__":
    main()