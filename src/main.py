from src.loader import load_courses, load_preferences
from src.csp import build_csp


def main():
    courses = load_courses("data/courses.json")
    prefs = load_preferences("data/preferences.json")
    csp = build_csp(courses, prefs["selected"])

    print("Variables and domains:")
    for v in csp.variables:
        print(" ", v, [s.id for s in csp.domains[v]])


if __name__ == "__main__":
    main()