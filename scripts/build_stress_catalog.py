"""Build data/stress_catalog.json: a crowded catalog with deliberate clashes.

Every section sits in one of 12 weekly time blocks (Mon/Wed or Tue/Thu, six 90-minute
blocks each). Two sections clash exactly when they use the same block, so a timetable
must give every course a different block. Run from the repo root:
    python scripts/build_stress_catalog.py
"""
import json

BLOCKS = {1: ("MW", "09:00", "10:30"), 2: ("TT", "09:00", "10:30"),
          3: ("MW", "10:30", "12:00"), 4: ("TT", "10:30", "12:00"),
          5: ("MW", "12:00", "13:30"), 6: ("TT", "12:00", "13:30"),
          7: ("MW", "13:30", "15:00"), 8: ("TT", "13:30", "15:00"),
          9: ("MW", "15:00", "16:30"), 10: ("TT", "15:00", "16:30"),
          11: ("MW", "16:30", "18:00"), 12: ("TT", "16:30", "18:00")}
DAYS = {"MW": ("Mon", "Wed"), "TT": ("Tue", "Thu")}


def block_section(code, n, block, seats=30):
    pat, start, end = BLOCKS[block]
    return {"id": f"{code}-{n}", "instructor": "Instructor S", "seats": seats, "synthetic": True,
            "slots": [{"day": d, "start": start, "end": end} for d in DAYS[pat]]}


def course(code, name, blocks, full_block=None):
    secs = [block_section(code, i + 1, b) for i, b in enumerate(blocks)]
    if full_block:                                   # a closed section (0 seats)
        secs.append(block_section(code, len(secs) + 1, full_block, seats=0))
    return {"code": code, "name": name, "credits": 3, "sections": secs}


def custom(code, name, sid, slots):
    return {"code": code, "name": name, "credits": 3, "sections": [
        {"id": sid, "instructor": "Instructor S", "seats": 30, "synthetic": True,
         "slots": [{"day": d, "start": s, "end": e} for d, s, e in slots]}]}


catalog = [
    # ---- 12 benchmark courses, in the order the benchmark takes them -------------
    course("CSE518", "Artificial Intelligence", [1, 2, 3, 4]),
    course("CSE340", "Operating Systems", [1, 3, 5, 7], full_block=1),
    course("CSE330", "Computer Networks", [2, 4, 6, 8]),
    course("CSE250", "Database Management Systems", [1, 5, 9, 11]),
    course("STA202", "Mathematical Statistics", [2, 6, 10, 12], full_block=2),
    course("CSE300", "Software Engineering", [3, 7, 9, 11]),
    course("CSC210", "Data Structures and Algorithms", [4, 8, 10, 12]),
    course("CSE212", "Cyber Security", [5, 6, 7, 8]),
    course("STA102", "Probability and Random Variables", [9, 11]),     # only 2 options
    course("MAT248", "Applied Linear Algebra", [10, 12]),              # only 2 options
    course("MAT305", "Mathematical Modeling", [5, 6]),                 # only 2 options
    course("MAT281", "Multivariable Calculus", [7, 8]),                # only 2 options
    # ---- special cases used by the tests (not part of the benchmark sizes) -------
    # FAC114 clashes with EVERY CSE518 section -> CSE518 + FAC114 is impossible
    {"code": "FAC114", "name": "Financial Accounting", "credits": 3, "sections": [
        {"id": "FAC114-1", "instructor": "Instructor S", "seats": 30, "synthetic": True,
         "slots": [{"day": "Mon", "start": "09:00", "end": "12:00"},
                   {"day": "Tue", "start": "09:00", "end": "12:00"}]},
        {"id": "FAC114-2", "instructor": "Instructor S", "seats": 30, "synthetic": True,
         "slots": [{"day": "Wed", "start": "09:00", "end": "12:00"},
                   {"day": "Thu", "start": "09:00", "end": "12:00"}]}]},
    # direct conflict: two single-section courses at exactly the same time
    custom("CLA101", "Clash Course A", "CLA101-1", [("Mon", "09:00", "10:30"), ("Wed", "09:00", "10:30")]),
    custom("CLA102", "Clash Course B", "CLA102-1", [("Mon", "09:00", "10:30"), ("Wed", "09:00", "10:30")]),
]

with open("data/stress_catalog.json", "w") as f:
    json.dump(catalog, f, indent=1)
print(f"data/stress_catalog.json written with {len(catalog)} courses")