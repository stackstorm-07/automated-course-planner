from itertools import product

from .csp import is_valid_schedule, is_consistent


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

def solve(csp):
    """Plain backtracking. Collects ALL solutions (does not stop at the first)."""
    stats = {"nodes": 0, "backtracks": 0}
    solutions = []
    variables = csp.variables

    def backtrack(assignment):
        # Every course has a section: record a complete schedule
        if len(assignment) == len(variables):
            solutions.append(dict(assignment))
            return 1

        # Plain order: take the next unassigned course
        var = next(v for v in variables if v not in assignment)

        found = 0
        for section in csp.domains[var]:
            stats["nodes"] += 1                      # one section tried
            if not is_consistent(assignment, section):
                continue                             # clash: skip it
            assignment[var] = section                # assign
            found += backtrack(assignment)           # go deeper
            del assignment[var]                      # undo (backtrack)

        if found == 0:
            stats["backtracks"] += 1                 # dead end
        return found

    backtrack({})
    return solutions, stats