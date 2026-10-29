from src.loader import load_courses, load_preferences
from src.csp import build_csp
from src.search import brute_force

def main():
    courses = load_courses("data/courses.json")
    prefs = load_preferences("data/preferences.json")
    csp = build_csp(courses, prefs["selected"])

    print("Variables and domains:")
    for v in csp.variables:
        print(" ", v, [s.id for s in csp.domains[v]])

    solutions, stats = brute_force(csp)
    print()
    print("Combinations checked:", stats["combinations_checked"])
    print("Valid schedules found:", len(solutions))
    for i, sol in enumerate(solutions, start=1):
        print(f"  Solution {i}:", {c: s.id for c, s in sol.items()})


if __name__ == "__main__":
    main()