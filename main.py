"""CLI demo: checks the PawPal+ logic layer before the Streamlit UI uses it."""

from pawpal_system import Owner, Pet, Scheduler, Task


def show(title, pairs):
    """Print (pet, task) pairs as one aligned line each."""
    print(f"\n{title}")
    for pet, task in pairs:
        mark = "x" if task.completed else " "
        print(f"  [{mark}] {task.time}  {pet.name:<6} {task.description:<14} "
              f"{task.duration_minutes:>3} min  {task.priority:<6} {task.frequency}")


owner = Owner("Jordan")
mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
owner.add_pet(mochi)
owner.add_pet(luna)

# Added out of order on purpose
mochi.add_task(Task("Evening walk", "18:30", 30, "medium", "daily"))
mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
luna.add_task(Task("Feeding", "08:00", 10, "high", "daily"))
luna.add_task(Task("Flea medicine", "07:30", 5, "high", "weekly"))  # same time as Mochi's walk
mochi.add_task(Task("Grooming", "13:00", 45, "low"))

scheduler = Scheduler(owner)

show("Today's Schedule (sorted by time)", scheduler.tasks_for_day())

print("\nConflict warnings")
for warning in scheduler.detect_conflicts():
    print("  WARNING:", warning)

show("Only Luna's tasks", scheduler.filter_tasks(pet_name="Luna"))

walk = mochi.tasks[1]
following = scheduler.mark_task_complete(mochi, walk)
print(f"\nMarked '{walk.description}' done; next one created for {following.due_date}")
show("Completed tasks", scheduler.filter_tasks(completed=True))

plan = scheduler.build_plan(available_minutes=60)
show("Plan for 60 free minutes (by priority)", plan["scheduled"])
show("Skipped (not enough time)", plan["skipped"])
