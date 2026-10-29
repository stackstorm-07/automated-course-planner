from src.models import Slot, Section
from src.csp import slots_overlap, sections_conflict
from src.loader import load_courses

def S(day, a, b): return Slot(day, a, b)

def test_same_time():        assert slots_overlap(S("Mon",600,690), S("Mon",600,690))
def test_partial_overlap():  assert slots_overlap(S("Mon",600,690), S("Mon",660,750))
def test_back_to_back():     assert not slots_overlap(S("Mon",600,690), S("Mon",690,780))
def test_different_days():   assert not slots_overlap(S("Mon",600,690), S("Tue",600,690))

def test_multi_slot_sections():
    a = Section("a","X","i",1,(S("Mon",600,690), S("Wed",600,690)))
    b = Section("b","Y","i",1,(S("Tue",600,690), S("Wed",660,750)))
    assert sections_conflict(a, b)

def test_planted_clash():
    c = load_courses("data/courses.json")
    assert sections_conflict(c["CSE340"].sections[0], c["CSE330"].sections[0])