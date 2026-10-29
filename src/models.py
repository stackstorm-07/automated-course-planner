from dataclasses import dataclass

@dataclass(frozen=True)
class Slot:
    day: str
    start: int   # minutes since midnight
    end: int

@dataclass(frozen=True)
class Section:
    id: str
    course_code: str
    instructor: str
    seats: int
    slots: tuple
    synthetic: bool = True

@dataclass(frozen=True)
class Course:
    code: str
    name: str
    credits: int
    sections: tuple

@dataclass(frozen=True)
class Schedule:
    assignment: dict   # course code -> Section
    score: float       # total weighted score, 0 to 1
    breakdown: dict    # e.g. {"days_off": 0.8, "early": 1.0, "gaps": 0.6, "compact": 0.7}