"""Terminal display: calendar grid, search trace, human confirmation loop.
Read-only consumer of Schedule objects; never decides validity."""

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
START, END, STEP = 9 * 60, 18 * 60, 30
COL = 9


def fmt(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def render_calendar(schedule, title="Timetable"):
    """Mon-Fri grid with half-hour rows 09:00-18:00. A cell shows the course
    code running in that half hour; two courses in one cell show CLASH
    (should never happen for solver output, but makes a bug visible)."""
    lines = [f"{title} (score {schedule.score:.2f})", ""]
    header = "Time  | " + " | ".join(d.center(COL) for d in DAYS)
    lines += [header, "-" * len(header)]
    for t in range(START, END, STEP):
        cells = []
        for d in DAYS:
            codes = [code for code, sec in schedule.assignment.items()
                     for sl in sec.slots if sl.day == d and sl.start < t + STEP and t < sl.end]
            label = "" if not codes else (codes[0] if len(codes) == 1 else "CLASH")
            cells.append(label.center(COL))
        lines.append(f"{fmt(t)} | " + " | ".join(cells))
    return "\n".join(lines)


def render_trace(events, limit=40):
    """Numbered list of solver event strings (assign / reject / backtrack)."""
    shown = events[:limit]
    out = [f"{i + 1:>3}. {e}" for i, e in enumerate(shown)]
    if len(events) > limit:
        out.append(f"... {len(events) - limit} more steps hidden")
    return "\n".join(out)


def render_no_solution(selected, reason=None):
    msg = ["No valid timetable exists for: " + ", ".join(selected)]
    msg.append(reason or "Every combination of sections has at least one time clash or a closed section.")
    return "\n".join(msg)


def confirm_schedules(schedules, explain_fn, render_fn=render_calendar, input_fn=None):
    """Show each option with its explanation; ask y / n / q.
    Returns the accepted Schedule, or None."""
    ask = input_fn or input
    for i, sched in enumerate(schedules, start=1):
        print(render_fn(sched, title=f"Option {i} of {len(schedules)}"))
        print()
        print(explain_fn(sched))
        while True:
            try:
                ans = ask("\nAccept this timetable? [y]es / [n]ext option / [q]uit: ").strip().lower()
            except EOFError:
                return None
            if ans in ("y", "n", "q"):
                break
            print("Please type y, n or q.")
        if ans == "y":
            return sched
        if ans == "q":
            return None
    print("No option accepted.")
    return None