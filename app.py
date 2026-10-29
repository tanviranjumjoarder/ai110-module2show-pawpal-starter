from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# Streamlit reruns this file on every click, so the Owner lives in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Give the pet a name.")
        elif owner.get_pet(pet_name.strip()):
            st.error(f"{pet_name} already exists.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species))
            st.success(f"Added {pet_name}.")

if not owner.pets:
    st.info("Add a pet to start scheduling tasks.")
    st.stop()

st.subheader("Schedule a task")
with st.form("add_task", clear_on_submit=False):
    target = st.selectbox("Pet", [p.name for p in owner.pets])
    description = st.text_input("Task", value="Morning walk")
    c1, c2, c3, c4 = st.columns(4)
    when = c1.time_input("Time")
    duration = c2.number_input("Minutes", min_value=1, max_value=240, value=20)
    priority = c3.selectbox("Priority", ["high", "medium", "low"], index=1)
    frequency = c4.selectbox("Repeats", ["once", "daily", "weekly"])
    if st.form_submit_button("Add task"):
        owner.get_pet(target).add_task(
            Task(description, when.strftime("%H:%M"), int(duration), priority, frequency)
        )
        st.success(f"Added '{description}' for {target} at {when.strftime('%H:%M')}.")

st.divider()
st.subheader("Today's schedule")

for warning in scheduler.detect_conflicts(date.today()):
    st.warning(warning)

f1, f2 = st.columns(2)
pet_filter = f1.selectbox("Show pet", ["All"] + [p.name for p in owner.pets])
status_filter = f2.selectbox("Show", ["Pending", "Done", "All"])
completed = {"Pending": False, "Done": True, "All": None}[status_filter]
rows = scheduler.sort_by_time(
    scheduler.filter_tasks(None if pet_filter == "All" else pet_filter, completed)
)

if rows:
    st.table([
        {"Time": t.time, "Date": str(t.due_date), "Pet": p.name, "Task": t.description,
         "Min": t.duration_minutes, "Priority": t.priority, "Repeats": t.frequency,
         "Done": "yes" if t.completed else "no"}
        for p, t in rows
    ])
else:
    st.info("No tasks match.")

pending = [(p, t) for p, t in rows if not t.completed]
if pending:
    label = lambda i: f"{pending[i][1].time}  {pending[i][0].name}: {pending[i][1].description}"
    pick = st.selectbox("Mark a task done", range(len(pending)), format_func=label)
    if st.button("Mark done"):
        pet, task = pending[pick]
        following = scheduler.mark_task_complete(pet, task)
        if following:
            st.session_state.notice = f"Done. Next {task.frequency} task created for {following.due_date}."
        else:
            st.session_state.notice = "Done."
        st.rerun()
if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))

st.divider()
st.subheader("Build a plan for the time I have")
minutes = st.number_input("Free minutes today", min_value=5, max_value=1440, value=60, step=5)
if st.button("Generate plan"):
    plan = scheduler.build_plan(int(minutes))
    if plan["scheduled"]:
        st.success("Planned, in time order (high priority tasks are picked first):")
        st.table([{"Time": t.time, "Pet": p.name, "Task": t.description,
                   "Min": t.duration_minutes, "Priority": t.priority}
                  for p, t in plan["scheduled"]])
    else:
        st.info("Nothing due today.")
    for p, t in plan["skipped"]:
        st.warning(f"Skipped (not enough time): {p.name} - {t.description} ({t.duration_minutes} min)")
