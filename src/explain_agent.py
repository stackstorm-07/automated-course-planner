"""Explanation agent. The LLM only *explains*; facts are computed without AI,
the reply is verified against them, and a template is the fallback."""
import os
import re

from src.display import fmt

ALL_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
LABELS = {"days_off": "preferred days off", "early": "avoiding early classes",
          "gaps": "short gaps between classes", "compact": "a compact schedule"}


def schedule_facts(schedule):
    days_used, earliest, latest, times = set(), 24 * 60, 0, set()
    meetings = {}
    for code, sec in schedule.assignment.items():
        meetings[code] = [f"{sl.day} {fmt(sl.start)}-{fmt(sl.end)}" for sl in sec.slots]
        for sl in sec.slots:
            days_used.add(sl.day)
            earliest, latest = min(earliest, sl.start), max(latest, sl.end)
            times.update((fmt(sl.start), fmt(sl.end)))
    return {
        "courses": sorted(schedule.assignment),
        "sections": {c: s.id for c, s in schedule.assignment.items()},
        "meetings": meetings,
        "days_used": [d for d in ALL_DAYS if d in days_used],
        "days_off": [d for d in ALL_DAYS if d not in days_used],
        "earliest": fmt(earliest),
        "latest": fmt(latest),
        "times": sorted(times),
        "score": round(schedule.score, 2),
        "breakdown": schedule.breakdown,
    }


def template_explanation(schedule):
    f = schedule_facts(schedule)
    off = ", ".join(f["days_off"]) if f["days_off"] else "none"
    chosen = ", ".join(f"{c} ({f['sections'][c]})" for c in f["courses"])
    text = (f"This timetable has {len(f['courses'])} courses with no time clashes: {chosen}. "
            f"Classes run on {', '.join(f['days_used'])}; days off: {off}. "
            f"The earliest class starts at {f['earliest']} and the last ends at {f['latest']}. "
            f"Overall preference score: {f['score']:.2f} out of 1.")
    if f["breakdown"]:
        best = max(f["breakdown"], key=f["breakdown"].get)
        worst = min(f["breakdown"], key=f["breakdown"].get)
        text += (f" Strongest match: {LABELS.get(best, best)} ({f['breakdown'][best]:.2f});"
                 f" weakest: {LABELS.get(worst, worst)} ({f['breakdown'][worst]:.2f}).")
    return text


# ------------------------------------------------------------------ verification
_DAY = re.compile(r"\b(Mon|Tue|Wed|Thu|Fri)\w*", re.I)


def verify_explanation(text, facts):
    """True only if the text invents nothing checkable: course codes, clock
    times, decimal numbers, course count, and day-off claims must all match."""
    # 1. course codes
    if not set(re.findall(r"\b[A-Z]{3}\d{3}\b", text)) <= set(facts["courses"]):
        return False
    # 2. clock times must be real meeting start/end times
    if not set(re.findall(r"\b\d{1,2}:\d{2}\b", text.replace("-", " "))) <= \
            {t.lstrip("0") or t for t in facts["times"]} | set(facts["times"]):
        return False
    # 3. decimals must be the score or a breakdown value
    allowed = {round(facts["score"], 2)} | {round(v, 2) for v in facts["breakdown"].values()}
    for num in re.findall(r"(?<![\d:])\d+\.\d+", text):
        if round(float(num), 2) not in allowed:
            return False
    # 4. "N courses" must be right
    for n in re.findall(r"\b(\d+)\s+courses\b", text):
        if int(n) != len(facts["courses"]):
            return False
    # 5. days named in an "off / free / no classes" clause must really be off
    off = {d.lower() for d in facts["days_off"]}
    for clause in re.split(r"[;!?]|\.(?!\d)", text):
        if re.search(r"\b(off|free|no classes?)\b", clause, re.I):
            for m in _DAY.finditer(clause):
                if m.group(1).lower() not in off:
                    return False
    return True


# ------------------------------------------------------------------ LLM
def _load_dotenv(path=".env"):
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def call_llm(prompt):
    _load_dotenv()
    if not os.environ.get("LLM_API_KEY"):
        raise RuntimeError("no API key")
    # TODO: call the team's chosen provider here and return the reply text.
    raise NotImplementedError


def explain(schedule, use_llm=True, llm_fn=None):
    facts = schedule_facts(schedule)
    if use_llm:
        prompt = ("Explain this university timetable to a student in 3-4 plain sentences. "
                  "Use ONLY these facts, add nothing new: " + str(facts))
        try:
            text = (llm_fn or call_llm)(prompt)
            if verify_explanation(text, facts):
                return text
        except Exception:
            pass
    return template_explanation(schedule)