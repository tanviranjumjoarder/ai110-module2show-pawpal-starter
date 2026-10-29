# PawPal+ Project Reflection

## 1. System Design

Three core actions: add a pet, schedule a task for a pet, and see today's tasks in time order with a warning if two clash.

**a. Initial design**

Four classes. `Owner` holds the pets. `Pet` holds its tasks. `Task` is one activity (description, "HH:MM" time, duration, priority, frequency, completed). `Scheduler` reads every task through the owner and sorts, filters and checks conflicts. `Task` and `Pet` are dataclasses to keep them short.

**b. Design changes**

The first draft had no date on `Task`. Recurrence needs one: a daily task must be due tomorrow, not just "07:30" again. I added `due_date` and made `mark_complete()` return the next `Task`, and `Scheduler.mark_task_complete()` adds that task to the pet. I also added `Scheduler.build_plan()` so the app can choose tasks when the owner has limited time. The final UML is in `diagrams/uml_final.mmd`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time of day, priority (high / medium / low), duration, and the free minutes the owner has. Time order is used for display. Priority is used when time is short, because a missed medicine matters more than a missed grooming.

**b. Tradeoffs**

Conflict detection only flags tasks with the same start time. A 30-minute walk at 07:30 and a feeding at 07:45 overlap but are not flagged. This keeps the check simple and easy to test. For a home pet-care list, exact clashes are the common case.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code to suggest the class split, draft the Mermaid diagram, write the methods and tests, and run the tests. The most useful prompts named the exact file and the exact behaviour, for example "marking a daily task done must create a task for tomorrow".

**b. Judgment and verification**

I did not take every suggestion as-is. I kept plain `sorted()` with a lambda key instead of a more clever one-liner, because it is easier to read and explain. I checked each method by running `main.py` and `pytest`, and I drove the Streamlit app in a headless test to confirm the conflict warning and the mark-done flow work.

---

## 4. Testing and Verification

**a. What you tested**

Sorting, daily and weekly recurrence, conflict detection, filtering, the time-limited plan, and edge cases: a pet with no tasks, completed tasks not conflicting, and a bad time string. These are the behaviours the UI depends on.

**b. Confidence**

4 out of 5. All 13 tests pass. Next I would test overlapping durations, tasks past midnight, and monthly recurrence.

---

## 5. Reflection

**a. What went well**

Building and checking the backend first made the Streamlit step short, because the UI only calls methods that already worked.

**b. What you would improve**

Detect overlapping durations, add editing and deleting tasks in the UI, and save data between runs.

**c. Key takeaway**

AI can write code quickly, but I have to decide what the design is and prove it with tests. The UML gave me something to check the AI's code against.
