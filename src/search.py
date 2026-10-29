from itertools import product

from .csp import is_valid_schedule


def brute_force(csp):
    """Try every combination of sections; keep only the clash-free ones."""
    solutions = []
    checked = 0
    order = csp.variables

    for combo in product(*(csp.domains[v] for v in order)):
        checked += 1
        assignment = dict(zip(order, combo))
        if is_valid_schedule(assignment):
            solutions.append(assignment)

    return solutions, {"combinations_checked": checked}