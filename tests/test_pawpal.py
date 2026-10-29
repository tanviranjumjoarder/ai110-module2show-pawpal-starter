from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def make_owner():
    owner = Owner("Jordan")
    pet = Pet("Mochi")
    owner.add_pet(pet)
    return owner, pet


def test_mark_complete_changes_status():
    task = Task("Walk", "08:00")
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi")
    pet.add_task(Task("Walk", "08:00"))
    assert len(pet.tasks) == 1


def test_sort_by_time_is_chronological():
    owner, pet = make_owner()
    for t in ("18:30", "07:30", "13:00"):
        pet.add_task(Task("x", t))
    times = [task.time for _, task in Scheduler(owner).sort_by_time()]
    assert times == ["07:30", "13:00", "18:30"]


def test_daily_task_creates_next_day_task():
    owner, pet = make_owner()
    today = date.today()
    task = Task("Feeding", "08:00", frequency="daily", due_date=today)
    pet.add_task(task)
    following = Scheduler(owner).mark_task_complete(pet, task)
    assert task.completed
    assert following.due_date == today + timedelta(days=1)
    assert not following.completed
    assert following in pet.tasks


def test_weekly_task_recurs_in_seven_days():
    task = Task("Bath", "10:00", frequency="weekly")
    assert task.mark_complete().due_date == task.due_date + timedelta(days=7)


def test_one_time_task_does_not_recur():
    owner, pet = make_owner()
    task = Task("Vet", "09:00")
    pet.add_task(task)
    assert Scheduler(owner).mark_task_complete(pet, task) is None
    assert len(pet.tasks) == 1


def test_conflict_detected_for_same_time_across_pets():
    owner, pet = make_owner()
    other = Pet("Luna")
    owner.add_pet(other)
    pet.add_task(Task("Walk", "07:30"))
    other.add_task(Task("Meds", "07:30"))
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1 and "07:30" in warnings[0]


def test_no_conflict_when_times_differ():
    owner, pet = make_owner()
    pet.add_task(Task("Walk", "07:30"))
    pet.add_task(Task("Meds", "07:31"))
    assert Scheduler(owner).detect_conflicts() == []


def test_completed_tasks_do_not_conflict():
    owner, pet = make_owner()
    done = Task("Walk", "07:30")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Meds", "07:30"))
    assert Scheduler(owner).detect_conflicts() == []


def test_pet_with_no_tasks():
    owner, _ = make_owner()
    scheduler = Scheduler(owner)
    assert scheduler.tasks_for_day() == []
    assert scheduler.detect_conflicts() == []


def test_filter_by_pet_and_status():
    owner, pet = make_owner()
    done = Task("Walk", "07:00")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Feed", "08:00"))
    scheduler = Scheduler(owner)
    assert len(scheduler.filter_tasks(pet_name="Mochi")) == 2
    assert [t.description for _, t in scheduler.filter_tasks(completed=False)] == ["Feed"]
    assert scheduler.filter_tasks(pet_name="Nobody") == []


def test_build_plan_prefers_priority_when_time_is_short():
    owner, pet = make_owner()
    pet.add_task(Task("Play", "07:00", 30, "low"))
    pet.add_task(Task("Meds", "09:00", 30, "high"))
    plan = Scheduler(owner).build_plan(available_minutes=30)
    assert [t.description for _, t in plan["scheduled"]] == ["Meds"]
    assert [t.description for _, t in plan["skipped"]] == ["Play"]


def test_invalid_time_is_rejected():
    with pytest.raises(ValueError):
        Task("Walk", "25:00")
