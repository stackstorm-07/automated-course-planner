"""Build data/courses_full.json = the existing starter catalog (copied unchanged)
+ the remaining gradesheet courses with SYNTHETIC sections.

data/courses.json is never modified. Run from the repo root:
    python scripts/build_full_catalog.py
"""
import json

MW, TT, MWF = ("Mon", "Wed"), ("Tue", "Thu"), ("Mon", "Wed", "Fri")


def sec(sid, instructor, seats, days, start, end):
    return {"id": sid, "instructor": instructor, "seats": seats, "synthetic": True,
            "slots": [{"day": d, "start": start, "end": end} for d in days]}


NEW_COURSES = [
    {"code": "CSC210", "name": "Data Structures and Algorithms", "credits": 4, "sections": [
        sec("CSC210-1", "Instructor L", 40, MWF, "09:00", "10:00"),
        sec("CSC210-2", "Instructor M", 35, TT, "11:30", "13:30"),
        sec("CSC210-3", "Instructor L", 25, MWF, "14:00", "15:00")]},
    {"code": "CSE212", "name": "Cyber Security", "credits": 3, "sections": [
        sec("CSE212-1", "Instructor N", 30, TT, "14:30", "16:00"),
        sec("CSE212-2", "Instructor O", 30, MW, "12:30", "14:00"),
        sec("CSE212-3", "Instructor N", 20, ("Sat",), "10:00", "12:30")]},
    {"code": "STA102", "name": "Probability and Random Variables", "credits": 4, "sections": [
        sec("STA102-1", "Instructor P", 40, TT, "12:00", "14:00"),
        sec("STA102-2", "Instructor Q", 35, MWF, "13:00", "14:00")]},
    {"code": "MAT248", "name": "Applied Linear Algebra", "credits": 3, "sections": [
        sec("MAT248-1", "Instructor R", 40, MW, "09:00", "10:30"),
        sec("MAT248-2", "Instructor S", 30, ("Sat",), "11:00", "12:30"),
        sec("MAT248-3", "Instructor R", 0, MW, "16:30", "18:00")]},
    {"code": "MAT305", "name": "Mathematical Modeling", "credits": 3, "sections": [
        sec("MAT305-1", "Instructor T", 30, TT, "12:00", "13:30"),
        sec("MAT305-2", "Instructor U", 30, MW, "13:00", "14:30")]},
    {"code": "MAT281", "name": "Multivariable Calculus", "credits": 4, "sections": [
        sec("MAT281-1", "Instructor V", 40, MWF, "11:00", "12:00"),
        sec("MAT281-2", "Instructor W", 35, TT, "14:00", "16:00"),
        sec("MAT281-3", "Instructor V", 30, MWF, "13:00", "14:00")]},
    {"code": "CSD102", "name": "Data Science", "credits": 3, "sections": [
        sec("CSD102-1", "Instructor X", 40, MW, "13:30", "15:00"),
        sec("CSD102-2", "Instructor Y", 35, TT, "10:00", "11:30")]},
    {"code": "MGT111", "name": "Identity and Behaviour", "credits": 3, "sections": [
        sec("MGT111-1", "Instructor Z", 40, ("Sat",), "10:00", "12:30"),
        sec("MGT111-2", "Instructor Z", 30, MW, "16:00", "17:30")]},
    {"code": "FAC114", "name": "Financial Accounting", "credits": 3, "sections": [
        sec("FAC114-1", "Instructor AA", 40, TT, "15:00", "16:30"),
        sec("FAC114-2", "Instructor AB", 30, ("Sat",), "13:00", "15:30"),
        sec("FAC114-3", "Instructor AA", 30, MW, "09:30", "11:00")]},
]

with open("data/courses.json") as f:
    existing = json.load(f)

have = {c["code"] for c in existing}
full = existing + [c for c in NEW_COURSES if c["code"] not in have]

with open("data/courses_full.json", "w") as f:
    json.dump(full, f, indent=1)
print(f"courses.json untouched ({len(existing)} courses); "
      f"courses_full.json written with {len(full)} courses")