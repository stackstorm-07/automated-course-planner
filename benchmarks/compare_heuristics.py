"""Compare every solver variant on the same inputs.

Run from the repo root:
    python -m benchmarks.compare_heuristics
    python -m benchmarks.compare_heuristics --catalog data/courses_full.json --sizes 4 6 8 10
The first N courses of the catalog file are used for size N.
"""
import argparse
import json
import os
import statistics
import time
from math import prod

from src.loader import load_courses
from src.csp import build_csp, is_valid_schedule
from src.search import brute_force, solve

VARIANTS = [
    ("brute force", None),
    ("plain", {}),
    ("FC", {"use_fc": True}),
    ("MRV", {"use_mrv": True}),
    ("FC+MRV", {"use_fc": True, "use_mrv": True}),
    ("FC+MRV+LCV", {"use_fc": True, "use_mrv": True, "use_lcv": True}),
    ("AC3+plain", {"use_ac3": True}),
    ("AC3+FC+MRV+LCV", {"use_ac3": True, "use_fc": True, "use_mrv": True, "use_lcv": True}),
]


def key(assignment):
    return tuple(sorted((c, s.id) for c, s in assignment.items()))


def run(csp, cfg):
    if cfg is None:
        sols, stats = brute_force(csp)
        return sols, {"nodes": stats["combinations_checked"], "backtracks": None}
    return solve(csp, **cfg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default="data/stress_catalog.json")
    ap.add_argument("--sizes", type=int, nargs="+", default=[4, 6, 8, 10])
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--brute-limit", type=int, default=100_000,
                    help="skip brute force when it would check more combinations than this")
    ap.add_argument("--out", default="results/evaluation.json")
    args = ap.parse_args()

    courses = load_courses(args.catalog)
    codes = list(courses)
    rows = []

    for n in args.sizes:
        csp = build_csp(courses, codes[:n])
        combos = prod(len(d) for d in csp.domains.values())
        reference = None
        print(f"\n=== {n} courses | {combos:,} possible combinations ===")
        print(f"{'variant':<16}{'time ms':>10}{'nodes':>10}{'backtracks':>12}{'solutions':>11}  valid  matches")
        for name, cfg in VARIANTS:
            if cfg is None and combos > args.brute_limit:
                print(f"{name:<16}{'skipped (too many combinations)':>43}")
                continue
            times = []
            for _ in range(args.repeats):
                t0 = time.perf_counter()
                sols, stats = run(csp, cfg)
                times.append((time.perf_counter() - t0) * 1000)
            found = sorted(map(key, sols))
            if reference is None:                     # brute force when it runs, else plain
                reference = found
            row = {"courses": n, "combinations": combos, "variant": name,
                   "time_ms": round(statistics.median(times), 3),
                   "nodes": stats["nodes"], "backtracks": stats["backtracks"],
                   "solutions": len(sols),
                   "all_valid": all(is_valid_schedule(s) for s in sols),
                   "matches_reference": found == reference}
            rows.append(row)
            bt = "-" if row["backtracks"] is None else row["backtracks"]
            print(f"{name:<16}{row['time_ms']:>10.2f}{row['nodes']:>10}{bt!s:>12}{row['solutions']:>11}"
                  f"  {'yes' if row['all_valid'] else 'NO':<6} {'yes' if row['matches_reference'] else 'NO'}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({"catalog": args.catalog, "repeats": args.repeats, "rows": rows}, f, indent=1)
    ok = all(r["all_valid"] and r["matches_reference"] for r in rows)
    print(f"\nValidity pass rate: {sum(r['all_valid'] for r in rows)}/{len(rows)} | "
          f"all variants agree: {'yes' if ok else 'NO'} | saved to {args.out}")


if __name__ == "__main__":
    main()