from src.models import Slot, Section, Schedule

def fake_schedule():
    """Clash-free timetable (a real solution of data/courses.json). Fri is free."""
    def sec(code, n, days, start, end):
        return Section(f"{code}-{n}", code, "Instructor X", 30,
                       tuple(Slot(d, start, end) for d in days))
    a = {
        "CSE330": sec("CSE330", 1, ("Mon", "Wed"), 630, 720),    # 10:30-12:00
        "CSE250": sec("CSE250", 2, ("Mon", "Wed"), 900, 990),    # 15:00-16:30
        "CSE300": sec("CSE300", 2, ("Mon", "Wed"), 990, 1080),   # 16:30-18:00
        "CSE340": sec("CSE340", 2, ("Tue", "Thu"), 600, 690),    # 10:00-11:30
        "STA202": sec("STA202", 2, ("Tue", "Thu"), 780, 900),    # 13:00-15:00
        "CSE518": sec("CSE518", 1, ("Tue", "Thu"), 960, 1050),   # 16:00-17:30
    }
    return Schedule(a, 0.82, {"days_off": 1.0, "early": 0.6, "gaps": 0.8, "compact": 0.9})