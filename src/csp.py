from itertools import product

def slots_overlap(a, b):
    # back-to-back (a.end == b.start) is NOT an overlap
    return a.day == b.day and a.start < b.end and b.start < a.end

def sections_conflict(s1, s2):
    return any(slots_overlap(a, b) for a, b in product(s1.slots, s2.slots))