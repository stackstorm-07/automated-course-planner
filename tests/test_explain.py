from src.explain_agent import explain, schedule_facts, template_explanation, verify_explanation
from tests.helpers import fake_schedule


def test_facts():
    f = schedule_facts(fake_schedule())
    assert f["days_off"] == ["Fri"] and f["earliest"] == "10:00" and f["latest"] == "18:00"


def test_template_mentions_all_courses_and_passes_own_check():
    s = fake_schedule()
    t = explain(s, use_llm=False)
    assert all(c in t for c in schedule_facts(s)["courses"])
    assert verify_explanation(t, schedule_facts(s))


def test_no_key_falls_back(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    s = fake_schedule()
    assert explain(s, use_llm=True) == template_explanation(s)


def test_good_llm_text_is_used():
    s = fake_schedule()
    good = "Six courses, no clashes. Friday is free and classes run 10:00 to 18:00. Score 0.82."
    assert explain(s, llm_fn=lambda p: good) == good


def _bad(text):
    return verify_explanation(text, schedule_facts(fake_schedule()))


def test_rejects_unknown_course():
    assert not _bad("Includes CSE999 on Monday.")


def test_rejects_false_day_off():
    assert not _bad("Monday is a day off.")
    assert not _bad("You have no classes on Tuesday.")


def test_rejects_wrong_time_score_and_count():
    assert not _bad("The first class starts at 08:00.")
    assert not _bad("The score is 0.95.")
    assert not _bad("It has 4 courses.")


def test_llm_failure_or_bad_text_falls_back():
    s = fake_schedule()
    def boom(p): raise RuntimeError("down")
    assert explain(s, llm_fn=boom) == template_explanation(s)
    assert explain(s, llm_fn=lambda p: "Monday is free, CSE999.") == template_explanation(s)