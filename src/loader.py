import json
from .models import Slot, Section, Course

DAYS = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat"}

def _to_min(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)

def load_courses(path):
    with open(path) as f:
        raw = json.load(f)
    courses, seen_sections = {}, set()
    for c in raw:
        code = c["code"]
        if code in courses:
            raise ValueError(f"Duplicate course code: {code}")
        if not c.get("sections"):
            raise ValueError(f"Course {code} has no sections")
        sections = []
        for s in c["sections"]:
            if s["id"] in seen_sections:
                raise ValueError(f"Duplicate section id: {s['id']}")
            seen_sections.add(s["id"])
            slots = []
            for sl in s["slots"]:
                if sl["day"] not in DAYS:
                    raise ValueError(f"Bad day '{sl['day']}' in {s['id']}")
                st, en = _to_min(sl["start"]), _to_min(sl["end"])
                if en <= st:
                    raise ValueError(f"End not after start in {s['id']}")
                slots.append(Slot(sl["day"], st, en))
            sections.append(Section(s["id"], code, s["instructor"], s["seats"],
                                    tuple(slots), s.get("synthetic", True)))
        courses[code] = Course(code, c["name"], c["credits"], tuple(sections))
    return courses

def load_preferences(path):
    with open(path) as f:
        return json.load(f)