import json

from src.loader import load_courses, load_preferences
from src.csp import build_csp
from src.search import solve
from src.ranking import rank_schedules
from src.display import render_calendar
from src.explain_agent import explain, schedule_facts


def make(tmp_path, with_saturday=True):
    courses = json.load(open("data/courses.json"))
    prefs = json.load(open("data/preferences.json"))
    if with_saturday:
        courses.append({"code": "MGT111", "name": "Identity and Behaviour", "credits": 3,
                        "sections": [{"id": "MGT111-1", "instructor": "Instructor K",
                                      "seats": 30, "synthetic": True,
                                      "slots": [{"day": "Sat", "start": "10:00", "end": "12:00"}]}]})
        prefs["selected"].append("MGT111")
    cpath, ppath = tmp_path / "c.json", tmp_path / "p.json"
    cpath.write_text(json.dumps(courses))
    ppath.write_text(json.dumps(prefs))
    csp = build_csp(load_courses(str(cpath)), load_preferences(str(ppath))["selected"])
    return csp, load_preferences(str(ppath))


def test_saturday_course_is_scheduled(tmp_path):
    csp, prefs = make(tmp_path)
    sols, _ = solve(csp, use_fc=True, use_mrv=True, use_ac3=True)
    assert len(sols) == 2
    assert all("MGT111" in s for s in sols)


def test_saturday_clash_is_detected(tmp_path):
    csp, _ = make(tmp_path)
    from src.models import Slot, Section
    clash = Section("XXX999-1", "XXX999", "i", 10, (Slot("Sat", 11 * 60, 13 * 60),))
    csp.variables.append("XXX999")
    csp.domains["XXX999"] = [clash]
    sols, _ = solve(csp, use_fc=True, use_mrv=True, use_ac3=True)
    assert sols == []


def test_scores_stay_between_0_and_1_with_saturday(tmp_path):
    csp, prefs = make(tmp_path)
    sols, _ = solve(csp, use_fc=True, use_mrv=True, use_ac3=True)
    for s in rank_schedules(sols, prefs):
        assert 0 <= s.score <= 1
        assert all(0 <= v <= 1 for v in s.breakdown.values())


def test_saturday_shown_in_calendar_only_when_used(tmp_path):
    csp, prefs = make(tmp_path)
    sols, _ = solve(csp, use_fc=True, use_mrv=True, use_ac3=True)
    out = render_calendar(rank_schedules(sols, prefs)[0])
    assert "Sat" in out and "MGT111" in out
    csp2, prefs2 = make(tmp_path, with_saturday=False)
    sols2, _ = solve(csp2, use_fc=True, use_mrv=True, use_ac3=True)
    assert "Sat" not in render_calendar(rank_schedules(sols2, prefs2)[0])


def test_explanation_mentions_saturday(tmp_path):
    csp, prefs = make(tmp_path)
    sols, _ = solve(csp, use_fc=True, use_mrv=True, use_ac3=True)
    top = rank_schedules(sols, prefs)
    assert "Sat" in schedule_facts(top[0])["days_used"]
    assert "Sat" in explain(top[0], use_llm=False)