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