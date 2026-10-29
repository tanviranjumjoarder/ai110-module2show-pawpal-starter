# PawPal+ (Module 2 Project)

**Name:** Tanvir Anjum Joarder | **Z Number:** Z23981706
**Course:** AI110 Foundations of AI Engineering, Fall 2026 (CodePath @ FAU)

PawPal+ is a Streamlit app that helps a pet owner plan care tasks (walks, feeding, meds, grooming) for one or more pets. The logic lives in `pawpal_system.py` and was checked from the terminal (`main.py`) and with `pytest` before the UI used it.

## Features

- Owner with many pets, each pet with many tasks (`Owner`, `Pet`, `Task`).
- Tasks sorted by date and time (`Scheduler.sort_by_time`).
- Filter by pet and/or done / not done (`Scheduler.filter_tasks`).
- Daily and weekly recurring tasks: marking one done creates the next one (`Task.mark_complete`, `Scheduler.mark_task_complete`).
- Conflict warnings when two pending tasks start at the same time, for the same or different pets (`Scheduler.detect_conflicts`).
- Edit (time, minutes, priority) or remove a task from the UI.
- A plan for "the time I have": high priority tasks are picked first until the minutes run out, the rest are listed as skipped (`Scheduler.build_plan`).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Sample Output

Output of `python main.py`:

```

Today's Schedule (sorted by time)
  [ ] 07:30  Mochi  Morning walk    30 min  high   daily
  [ ] 07:30  Luna   Flea medicine    5 min  high   weekly
  [ ] 08:00  Luna   Feeding         10 min  high   daily
  [ ] 13:00  Mochi  Grooming        45 min  low    once
  [ ] 18:30  Mochi  Evening walk    30 min  medium daily

Conflict warnings
  WARNING: Conflict on 2026-10-28 at 07:30: Mochi: Morning walk, Luna: Flea medicine

Only Luna's tasks
  [ ] 08:00  Luna   Feeding         10 min  high   daily
  [ ] 07:30  Luna   Flea medicine    5 min  high   weekly

Marked 'Morning walk' done; next one created for 2026-10-29

Completed tasks
  [x] 07:30  Mochi  Morning walk    30 min  high   daily

Plan for 60 free minutes (by priority)
  [ ] 07:30  Luna   Flea medicine    5 min  high   weekly
  [ ] 08:00  Luna   Feeding         10 min  high   daily
  [ ] 18:30  Mochi  Evening walk    30 min  medium daily

Skipped (not enough time)
  [ ] 13:00  Mochi  Grooming        45 min  low    once
```

## Testing PawPal+

```bash
python -m pytest
```

The 13 tests cover: marking a task complete, adding a task to a pet, chronological sorting, daily and weekly recurrence, one-time tasks not recurring, conflict detection (same time across pets, different times, completed tasks ignored), a pet with no tasks, filtering, the priority plan when time is short, and a bad time string being rejected.

```
============================= test session starts ==============================
platform darwin -- Python 3.12.15, pytest-9.2.0, pluggy-1.7.0
rootdir: pawpal-plus
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 13 items
tests/test_pawpal.py .............                                       [100%]
============================== 13 passed in 0.02s ==============================
```

**Confidence level:** ★★★★☆ (4 / 5). The core behaviours pass, including edge cases. Not covered: tasks that overlap by duration, and tasks that cross midnight.

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time` | `sorted()` with a `(due_date, "HH:MM")` key. 24-hour strings sort correctly as text. |
| Filtering | `Scheduler.filter_tasks`, `Scheduler.tasks_for_day` | By pet name, by done / not done, or today's pending tasks. |
| Conflict handling | `Scheduler.detect_conflicts` | Groups pending tasks by (date, start time). Returns warning strings, never raises. Exact start-time matches only. |
| Recurring tasks | `Task.mark_complete`, `Scheduler.mark_task_complete` | Daily adds 1 day, weekly adds 7 days (`timedelta`). The new task is added to the same pet. |
| Time-limited plan | `Scheduler.build_plan` | Highest priority first; a task that does not fit is skipped. |

## Demo Walkthrough

1. Open the app with `streamlit run app.py`. Enter the owner name.
2. Add a pet (name and species). The `Owner` object is kept in `st.session_state`, so it survives button clicks.
3. Schedule tasks for the pet: description, time, minutes, priority, and once / daily / weekly. Add two at the same time to see the yellow conflict warning above the schedule.
4. Read "Today's schedule": tasks are sorted by time; use the filters to show one pet or only pending / done tasks.
5. Pick a task and click "Mark done". A daily or weekly task creates the next occurrence.
6. Enter the free minutes you have and click "Generate plan" to see which tasks fit (with a "Why" column and minutes used) and which were skipped.
7. Open "Edit or remove a task" to change a task's time, minutes or priority, or delete it. A bad time like 25:99 shows an error instead of crashing.

Key Scheduler behaviours shown: tasks sorted by time, conflict warnings (`st.warning`), filters by pet and status, recurrence on "Mark done", and the priority plan (`st.success`, `st.table`).

Sample CLI output from `python main.py`:

```

Today's Schedule (sorted by time)
  [ ] 07:30  Mochi  Morning walk    30 min  high   daily
  [ ] 07:30  Luna   Flea medicine    5 min  high   weekly
  [ ] 08:00  Luna   Feeding         10 min  high   daily
  [ ] 13:00  Mochi  Grooming        45 min  low    once
  [ ] 18:30  Mochi  Evening walk    30 min  medium daily

Conflict warnings
  WARNING: Conflict on 2026-10-28 at 07:30: Mochi: Morning walk, Luna: Flea medicine

Only Luna's tasks
  [ ] 08:00  Luna   Feeding         10 min  high   daily
  [ ] 07:30  Luna   Flea medicine    5 min  high   weekly

Marked 'Morning walk' done; next one created for 2026-10-29

Completed tasks
  [x] 07:30  Mochi  Morning walk    30 min  high   daily

Plan for 60 free minutes (by priority)
  [ ] 07:30  Luna   Flea medicine    5 min  high   weekly
  [ ] 08:00  Luna   Feeding         10 min  high   daily
  [ ] 18:30  Mochi  Evening walk    30 min  medium daily

Skipped (not enough time)
  [ ] 13:00  Mochi  Grooming        45 min  low    once
```

## Design

UML sources: `diagrams/uml_draft.mmd` (Phase 1) and `diagrams/uml_final.mmd` (final, also saved as `diagrams/uml.mmd`). Reflection: `reflection.md`.

## AI use

I used Claude Code for design brainstorming and to draft code and tests. I checked the output against my UML and ran everything myself.
