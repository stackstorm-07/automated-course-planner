from collections import deque

from .csp import sections_conflict


def ac3(csp):
    """AC-3 preprocessing. Removes sections that can never be part of a solution.

    Returns (domains, removed). domains is None if some course ends up with
    no sections (the problem is impossible). removed is a list of
    (section_id, course, because_of_course) for the explanation/trace.
    """
    domains = {v: list(d) for v, d in csp.domains.items()}
    removed = []
    queue = deque((a, b) for a in csp.variables for b in csp.variables if a != b)

    while queue:
        xi, xj = queue.popleft()
        revised = False
        for s in domains[xi][:]:
            # s survives only if some section of xj is compatible with it
            if all(sections_conflict(s, t) for t in domains[xj]):
                domains[xi].remove(s)
                removed.append((s.id, xi, xj))
                revised = True
        if revised:
            if not domains[xi]:
                return None, removed
            for xk in csp.variables:
                if xk not in (xi, xj):
                    queue.append((xk, xi))

    return domains, removed