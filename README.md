# Automated Course Planner

**AI-based university timetable generation using constraint satisfaction (CSP) and search.**

Course project for **CSE518 Artificial Intelligence**, Ahmedabad University. Instructor: Shashi Prabh.

| Team member | Role |
|---|---|
| **Ankit Kumar** | Deterministic AI: data loading, CSP formulation, constraint propagation, search and heuristics, scoring, ranking, benchmarks |
| **Milan Jayesh Shah** | Generative AI and interface: calendar display, explanation agent, human confirmation prompt, README, demo |

---

## What it does

A student picks the courses they want. Each course has several sections (different days and times). The planner:

1. models the choice of one section per course as a **Constraint Satisfaction Problem**,
2. finds **every** clash-free combination using backtracking search with heuristics,
3. **scores** each valid timetable against the student's preferences (days off, early classes, gaps, compactness),
4. shows the **top three** as a weekly calendar grid with a plain-language explanation,
5. lets the student **accept or reject** each option.

If no clash-free timetable exists, it says so.

### Two-agent design

```
 courses, sections, preferences
              |
              v
 +-------------------------------+        +--------------------------------+
 | Agent 1: Deterministic AI     |        | Agent 2: Generative AI         |
 | CSP + AC-3 + backtracking     | -----> | explains the schedule in plain |
 | (FC, MRV, LCV) + scoring      | Sched- | language; never decides        |
 | DECIDES what is valid         | ule    | validity; template fallback    |
 +-------------------------------+        +--------------------------------+
                                                      |
                                                      v
                                       calendar grid -> student accepts / rejects
                                                    (human in the loop)
```

The CSP/search code, not a language model, decides whether a timetable is valid. Every timetable is re-checked by an independent validator (`is_valid_schedule`) before it is shown. The explanation agent only describes a schedule that is already valid, and its output is verified against the schedule's facts. If it fails, a template explanation is used.

---

## How it works

### CSP formulation

| Element | In this project |
|---|---|
| **Variables** | One per selected course |
| **Domains** | The sections of that course that still have seats (full sections are removed first) |
| **Hard constraints** | No two chosen sections overlap in time; exactly one section per course; a seat is available |
| **Soft preferences** | Preferred days off, avoiding early classes, short gaps, compact days (used only for ranking) |

Two sections overlap when they are on the same day and `a.start < b.end and b.start < a.end`. Back-to-back classes (one ends exactly when the next starts) are **not** an overlap.

### Search and heuristics

| Technique | What it does |
|---|---|
| **Brute force** | Tries every combination. Used only as the baseline every other solver must match exactly. |
| **Backtracking** | Assigns one course at a time and abandons a branch at the first clash. Keeps going after the first solution to collect all of them. |
| **Forward checking (FC)** | After each assignment, removes clashing sections from the other courses' domains and cuts the branch if any domain becomes empty. |
| **MRV** | Picks the course with the fewest remaining sections next (ties broken by degree: the number of other courses it can clash with). |
| **LCV** | Tries first the section that rules out the fewest options elsewhere. |
| **AC-3** | Preprocessing: repeatedly removes sections that have no compatible section in some other course. Detects impossible requests before any search. |

### Scoring

Each term is normalised to 0..1 (1 is best). The total is the weighted average using the weights in `data/preferences.json`. Ties are broken by section ids so the output is the same on every run.

| Term | Meaning |
|---|---|
| `days_off` | Share of the preferred days off that have no classes |
| `early` | 1 minus the share of class meetings that start before `avoid_before` |
| `gaps` | Share of gaps between classes that are no longer than `max_gap_minutes` (back-to-back is not a gap) |
| `compact` | (6 minus the number of days used) divided by 5 |

---

## Quick start

Tested on Ubuntu (WSL) with Python 3.12.

```bash
git clone https://github.com/stackstorm-07/automated-course-planner.git
cd automated-course-planner

sudo apt install -y python3.12-venv      # Ubuntu only, once
python3 -m venv .venv
source .venv/bin/activate                # run this in every new terminal
pip install -r requirements.txt

python -m pytest -v                      # all tests should pass
python -m src.main                       # run the planner
```

Always run commands from the repository root.

## Usage

```bash
python -m src.main             # show the top three timetables, each with an explanation
python -m src.main --confirm   # ask y / n / q for each option
```

The program reads `data/courses.json` and `data/preferences.json`. To plan with different courses or preferences, edit `selected` and the weights in `data/preferences.json`, or replace the catalog with another file in the format described under Data.

### Preferences file

```json
{"selected": ["CSE518", "CSE340", "CSE330", "CSE250", "STA202", "CSE300"],
 "avoid_before": "09:30",
 "preferred_days_off": ["Fri"],
 "max_gap_minutes": 120,
 "weights": {"days_off": 0.3, "early": 0.2, "gaps": 0.3, "compact": 0.2}}
```

### Example output (default run, abbreviated)

```
Valid timetables found: 2   solver stats: {'nodes': 7, 'backtracks': 0, 'ac3_removed': 4}

Option 1 of 2 (score 0.78)

Time  |    Mon    |    Tue    |    Wed    |    Thu    |    Fri
-----------------------------------------------------------------
10:00 |           |   CSE340  |           |   CSE340  |
10:30 |   CSE330  |   CSE340  |   CSE330  |   CSE340  |
...
16:00 |   CSE250  |   CSE518  |   CSE250  |   CSE518  |
16:30 |   CSE300  |   CSE518  |   CSE300  |   CSE518  |

Score breakdown: {'days_off': 1.0, 'early': 1.0, 'gaps': 0.67, 'compact': 0.4}
This timetable has 6 courses with no time clashes: ... Classes run on Mon, Tue, Wed, Thu;
days off: Fri. ... Overall preference score: 0.78 out of 1.
```

A Saturday column appears in the grid only when a chosen section meets on Saturday.

---

## Data

- **Course codes, titles and credits** come from the team's gradesheet.
- **Sections and meeting times are synthetic.** The gradesheet has no timetable. The only real timing is `CSE518` (Tue/Thu 16:00-17:30). Every invented section is marked `"synthetic": true`.
- **No grades, student ids or personal records** are stored in the repository.
- To use real data, replace the JSON with verified section times from the current official timetable and record the source and date.

| File | Contents |
|---|---|
| `data/courses.json` | Starter catalog: 6 courses with deliberate clashes and one full section (the baseline: 2 valid timetables) |
| `data/courses_full.json` | All 15 gradesheet courses (the starter catalog is copied unchanged), including Saturday sections |
| `data/stress_catalog.json` | Crowded benchmark catalog, plus an impossible case and a direct conflict |
| `data/preferences.json` | Default selected courses and preference weights |

The two larger catalogs are generated by `scripts/build_full_catalog.py` and `scripts/build_stress_catalog.py`. The starter `courses.json` is never modified.

Section file format (times are `HH:MM`, days are `Mon` to `Sat`):

```json
{"code": "CSE340", "name": "Operating Systems", "credits": 3, "sections": [
  {"id": "CSE340-1", "instructor": "Instructor B", "seats": 35, "synthetic": true,
   "slots": [{"day": "Mon", "start": "10:00", "end": "11:30"},
             {"day": "Wed", "start": "10:00", "end": "11:30"}]}]}
```

The loader rejects duplicate course codes, courses with no sections, duplicate section ids, unknown day names, and end times that are not after the start.

---

## Project structure

```
automated-course-planner/
  data/          courses.json  courses_full.json  stress_catalog.json  preferences.json
  src/
    models.py        Slot, Section, Course, Schedule
    loader.py        read and validate the JSON
    csp.py           overlap check, CSP model, consistency and validity checks
    propagation.py   AC-3
    search.py        brute force, backtracking, FC, MRV, LCV
    scoring.py       soft-preference terms
    ranking.py       score, re-validate, sort, top N
    display.py       calendar grid, confirmation prompt, no-solution message
    explain_agent.py facts, template explanation, verification, optional LLM hook
    main.py          program entry point (python -m src.main)
  tests/         pytest suite
  benchmarks/    compare_heuristics.py
  scripts/       build_full_catalog.py  build_stress_catalog.py
  results/       evaluation.json (benchmark output)
  README.md  requirements.txt
```

---

## Testing

```bash
python -m pytest -v
```

The tests cover:

- overlap logic (same time, partial overlap, back-to-back, different days, multi-slot sections),
- data validation and seat filtering,
- the brute-force baseline (6 courses: 32 combinations, 2 valid timetables),
- **every solver variant returning exactly the same set of schedules as brute force** on the starter, full and stress catalogs,
- AC-3 pruning and early detection of impossible requests,
- scoring and ranking (hand-checked values, determinism, fewer than three results),
- Saturday classes in the solver, scoring, calendar and explanation,
- the calendar grid, the confirmation prompt and the explanation verifier.

## Evaluation

```bash
python -m benchmarks.compare_heuristics                       # stress catalog, sizes 4 6 8 10
python -m benchmarks.compare_heuristics --catalog data/courses_full.json --out results/evaluation_full.json
```

Every variant gets the same courses, the same data and the same goal (collect all solutions). The script records the median time of several runs, nodes expanded, backtracks and solutions found, and re-checks every returned schedule with the independent validator. Results are saved to `results/evaluation.json`.

Stress catalog, nodes / backtracks (identical on every machine; times depend on the machine):

| Variant | 4 courses | 6 courses | 8 courses | 10 courses |
|---|---|---|---|---|
| Brute force (combinations checked) | 256 | 4,096 | 65,536 | skipped |
| Plain backtracking | 268 / 0 | 2,908 / 0 | 20,828 / 224 | 41,308 / 6,796 |
| Forward checking | 222 / 0 | 2,006 / 0 | 10,879 / 137 | 13,183 / 1,205 |
| MRV | 260 / 0 | 2,340 / 0 | 18,036 / 0 | 20,758 / 372 |
| FC + MRV | 214 / 0 | 1,806 / 0 | 8,772 / 0 | **6,186 / 0** |
| FC + MRV + LCV | 214 / 0 | 1,806 / 0 | 8,772 / 0 | 6,186 / 0 |
| AC-3 + plain | 268 / 0 | 2,908 / 0 | 20,828 / 224 | 41,308 / 6,796 |
| Valid timetables | 156 | 1,280 | 5,760 | 3,328 |

Findings, including where the heuristics do not help:

- **FC + MRV scales best.** At 10 courses it needs about 6.7 times fewer nodes than plain backtracking and never backtracks.
- **On the smallest problem the heuristics do not pay off in time.** Each node costs more (domain copies, MRV selection): at 4 courses plain backtracking took 2.5 ms against 3.1 ms for FC + MRV in the saved run. From 6 courses on the savings in nodes show up in time too (21.7 ms against 8.1 ms). Times are from `results/evaluation.json` and depend on the machine.
- **LCV does not reduce work here,** because the solver collects all solutions and every branch must be visited anyway: the node counts with and without LCV are identical in the table, and it only adds ordering cost.
- **AC-3 has no effect on the stress catalog,** because every section has a compatible partner in every other course. It helps on tight catalogs and on impossible requests: for `CSE518` + `FAC114` (a course that clashes with every `CSE518` section), plain search needs 12 nodes and AC-3 needs 0.

---

## Known limitations

- Section data is synthetic (see Data). Results show the method works, not what a real semester looks like.
- Terminal interface only (no web dashboard).
- **The LLM call is not connected yet.** `call_llm` in `src/explain_agent.py` is a placeholder, so explanations currently come from the template. The rest of the pipeline is in place: facts are computed without AI, the prompt uses only those facts, the reply is verified against them, and the template is the fallback. A provider key would go in a git-ignored `.env` file as `LLM_API_KEY`.
- The student chooses the courses. The planner does not recommend which courses to take, and does not check prerequisites or credit limits.
- Preferred instructors are not scored.

## Team workflow

- We work on `main`. **Pull before you start and again before you push**, and only commit your own files.
- Never commit the gradesheet, the proposal, any PDF or any API key. `.gitignore` blocks `*.pdf` and `.env`.
- Run `python -m pytest -v` from the repository root before every push.