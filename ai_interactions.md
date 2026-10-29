# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

Extra algorithm added: `Scheduler.build_plan(available_minutes)`, which picks today's tasks by priority (high, medium, low, then time) until the free minutes run out and lists the rest as skipped.

**What task did you give the agent?**

I asked Claude Code (agent mode) to build PawPal+ from my UML: the four classes in `pawpal_system.py`, the `main.py` demo, the pytest suite, and the Streamlit app, and later to check every assignment step and fill any gaps.

**What did the agent do?**

- Files edited: `pawpal_system.py`, `main.py`, `tests/test_pawpal.py`, `pytest.ini`, `app.py`, `diagrams/uml_draft.mmd`, `diagrams/uml_final.mmd`, `diagrams/uml.mmd`, `README.md`, `reflection.md`.
- Commands run: `python main.py`, `python -m pytest`, and a headless Streamlit test (`streamlit.testing.v1.AppTest`) that added pets and tasks, triggered a conflict, marked a task done, edited and removed a task, and generated a plan.
- It pasted the real CLI and test output into the README.

**What did you have to verify or fix manually?**

- The success message vanished after `st.rerun()`; it was moved into `st.session_state` so it shows after the rerun.
- In the headless test, two tasks with the exact same label confused the task picker. That was a test-tool quirk, so the test was rerun with distinct tasks.
- I checked that the final UML matches the methods in `pawpal_system.py`, and that every commit is authored by me.
