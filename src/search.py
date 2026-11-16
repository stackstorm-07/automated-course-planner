from itertools import product

from .csp import is_valid_schedule, is_consistent, sections_conflict


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

def solve(csp, use_fc=False):
    """Backtracking that collects ALL solutions. use_fc turns on forward checking."""
    stats = {"nodes": 0, "backtracks": 0}
    solutions = []
    variables = csp.variables

    def backtrack(assignment, domains):
        if len(assignment) == len(variables):
            solutions.append(dict(assignment))
            return 1

        var = next(v for v in variables if v not in assignment)

        found = 0
        for section in domains[var]:
            stats["nodes"] += 1
            if not is_consistent(assignment, section):
                continue

            new_domains = domains
            if use_fc:
                # copy domains, then drop sections that clash with this choice
                new_domains = dict(domains)
                dead_end = False
                for other in variables:
                    if other not in assignment and other != var:
                        new_domains[other] = [
                            s for s in domains[other]
                            if not sections_conflict(s, section)
                        ]
                        if not new_domains[other]:   # a course has no options left
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

    backtrack({}, {v: list(d) for v, d in csp.domains.items()})
    return solutions, stats