from itertools import product

from .csp import is_valid_schedule, is_consistent, sections_conflict
from .propagation import ac3


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

def solve(csp, use_fc=False, use_mrv=False, use_lcv=False, use_ac3=False):
    """Backtracking that collects ALL solutions, with optional heuristics."""
    stats = {"nodes": 0, "backtracks": 0}
    solutions = []
    variables = csp.variables

    # Degree: how many other courses could ever clash with this one
    degree = {
        v: sum(
            1 for w in variables if w != v and
            any(sections_conflict(a, b) for a in csp.domains[v] for b in csp.domains[w])
        )
        for v in variables
    }

    def select_var(assignment, domains):
        unassigned = [v for v in variables if v not in assignment]
        if not use_mrv:
            return unassigned[0]
        # fewest remaining sections first; ties broken by highest degree
        return min(unassigned, key=lambda v: (len(domains[v]), -degree[v]))

    def order_values(var, assignment, domains):
        values = domains[var]
        if not use_lcv:
            return values
        others = [v for v in variables if v not in assignment and v != var]

        def ruled_out(sec):
            return sum(1 for o in others for s in domains[o] if sections_conflict(sec, s))

        return sorted(values, key=ruled_out)

    def backtrack(assignment, domains):
        if len(assignment) == len(variables):
            solutions.append(dict(assignment))
            return 1

        var = select_var(assignment, domains)

        found = 0
        for section in order_values(var, assignment, domains):
            stats["nodes"] += 1
            if not is_consistent(assignment, section):
                continue

            new_domains = domains
            if use_fc:
                new_domains = dict(domains)
                dead_end = False
                for other in variables:
                    if other not in assignment and other != var:
                        new_domains[other] = [
                            s for s in domains[other]
                            if not sections_conflict(s, section)
                        ]
                        if not new_domains[other]:
                            dead_end = True
                            break
                if dead_end:
                    stats["backtracks"] += 1
                    continue

            assignment[var] = section
            found += backtrack(assignment, new_domains)
            del assignment[var]

        if found == 0:
            stats["backtracks"] += 1
        return found

    start = {v: list(d) for v, d in csp.domains.items()}
    if use_ac3:
        start, removed = ac3(csp)
        stats["ac3_removed"] = len(removed)
        if start is None:                 # a course lost all its sections
            return [], stats
    backtrack({}, start)
    return solutions, stats