import builtins
from src.display import render_calendar, render_trace, render_no_solution, confirm_schedules
from tests.helpers import fake_schedule, Schedule


def _rows(out):
    return {l.split("|")[0].strip(): [c.strip() for c in l.split("|")[1:]] for l in out.splitlines()[4:]}


def test_calendar_contains_courses():
    out = render_calendar(fake_schedule())
    for c in ("CSE518", "CSE340", "CSE250", "CSE330", "CSE300", "STA202"):
        assert c in out


def test_cells_and_free_day():
    rows = _rows(render_calendar(fake_schedule()))
    assert rows["10:00"] == ["", "CSE340", "", "CSE340", ""]            # Tue/Thu only
    assert rows["10:30"] == ["CSE330", "CSE340", "CSE330", "CSE340", ""]
    assert rows["17:30"] == ["CSE300", "", "CSE300", "", ""]            # last row
    assert all(r[4] == "" for r in rows.values())                        # Friday empty


def test_back_to_back_and_end_exclusive():
    rows = _rows(render_calendar(fake_schedule()))
    assert rows["16:00"][0] == "CSE250" and rows["16:30"][0] == "CSE300"  # 16:30 hand-over
    assert rows["12:00"][0] == ""                                         # CSE330 ended at 12:00


def test_clash_is_visible():
    s = fake_schedule()
    bad = Schedule({**s.assignment, "CSE999": s.assignment["CSE340"]}, 0.5, {})
    assert "CLASH" in render_calendar(bad)


def test_trace_limit():
    out = render_trace([f"e{i}" for i in range(50)], limit=3)
    assert out.splitlines()[0].strip().startswith("1.") and "47 more steps hidden" in out


def test_no_solution_message():
    assert "No valid timetable" in render_no_solution(["CSE518"])


def _run(monkeypatch, answers):
    it = iter(answers)
    monkeypatch.setattr(builtins, "input", lambda *_: next(it))
    scheds = [fake_schedule(), fake_schedule()]
    return scheds, confirm_schedules(scheds, lambda s: "expl")


def test_confirm_n_then_y(monkeypatch):
    scheds, res = _run(monkeypatch, ["n", "y"])
    assert res is scheds[1]


def test_confirm_quit(monkeypatch):
    assert _run(monkeypatch, ["q"])[1] is None


def test_confirm_bad_answer_asks_again(monkeypatch):
    scheds, res = _run(monkeypatch, ["x", "", "y"])
    assert res is scheds[0]


def test_confirm_all_rejected(monkeypatch):
    assert _run(monkeypatch, ["n", "n"])[1] is None