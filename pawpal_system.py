"""PawPal+ logic layer: Owner, Pet, Task and Scheduler."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import Dict, List, Optional

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


@dataclass
class Task:
    """One care activity for one pet on one day."""

    description: str
    time: str  # "HH:MM", 24-hour, so plain string order is time order
    duration_minutes: int = 15
    priority: str = "medium"  # low / medium / high
    frequency: str = "once"  # once / daily / weekly
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def __post_init__(self):
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if self.frequency != "once" and self.frequency not in RECURRENCE_DAYS:
            raise ValueError("frequency must be once, daily or weekly")
        hours, _, minutes = self.time.partition(":")
        if not (hours.isdigit() and minutes.isdigit() and int(hours) < 24 and int(minutes) < 60):
            raise ValueError("time must look like HH:MM")

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task done and return the next occurrence for daily/weekly tasks."""
        self.completed = True
        days = RECURRENCE_DAYS.get(self.frequency)
        if days is None:
            return None
        return replace(self, due_date=self.due_date + timedelta(days=days), completed=False)


@dataclass
class Pet:
    """A pet and the tasks that belong to it."""

    name: str
    species: str = "dog"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)


@dataclass
class Owner:
    """A person who owns one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the pet with this name, or None."""
        return next((p for p in self.pets if p.name == name), None)

    def all_tasks(self) -> List[tuple]:
        """Return (pet, task) pairs across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Reads tasks from an Owner's pets and organizes them."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_by_time(self, pairs: Optional[List[tuple]] = None) -> List[tuple]:
        """Sort (pet, task) pairs by due date, then HH:MM."""
        pairs = self.owner.all_tasks() if pairs is None else pairs
        return sorted(pairs, key=lambda pt: (pt[1].due_date, pt[1].time))

    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None) -> List[tuple]:
        """Return (pet, task) pairs, optionally limited to one pet and/or a completion state."""
        return [
            (pet, task) for pet, task in self.owner.all_tasks()
            if (pet_name is None or pet.name == pet_name)
            and (completed is None or task.completed == completed)
        ]

    def tasks_for_day(self, day: Optional[date] = None) -> List[tuple]:
        """Return the pending (pet, task) pairs due on a day, in time order."""
        day = day or date.today()
        due = [(p, t) for p, t in self.filter_tasks(completed=False) if t.due_date == day]
        return self.sort_by_time(due)

    def detect_conflicts(self, day: Optional[date] = None) -> List[str]:
        """Return a warning for every start time shared by two or more pending tasks."""
        by_slot: Dict[tuple, List[tuple]] = {}
        for pet, task in self.filter_tasks(completed=False):
            if day is None or task.due_date == day:
                by_slot.setdefault((task.due_date, task.time), []).append((pet, task))
        return [
            f"Conflict on {d} at {t}: " + ", ".join(f"{p.name}: {k.description}" for p, k in group)
            for (d, t), group in sorted(by_slot.items()) if len(group) > 1
        ]

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        """Complete a task and, if it recurs, add the next occurrence to the same pet."""
        following = task.mark_complete()
        if following is not None:
            pet.add_task(following)
        return following

    def build_plan(self, available_minutes: int, day: Optional[date] = None) -> Dict[str, list]:
        """Pick the day's tasks by priority until time runs out; the rest are skipped."""
        day = day or date.today()
        ranked = sorted(self.tasks_for_day(day),
                        key=lambda pt: (PRIORITY_RANK[pt[1].priority], pt[1].time))
        chosen, skipped, used = [], [], 0
        for pet, task in ranked:
            if used + task.duration_minutes <= available_minutes:
                chosen.append((pet, task))
                used += task.duration_minutes
            else:
                skipped.append((pet, task))
        return {"scheduled": self.sort_by_time(chosen), "skipped": skipped}
