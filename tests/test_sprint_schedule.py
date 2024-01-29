# -*- coding: utf-8 -*-
from jira_assistant.sprint_schedule import SprintScheduleStore

from . import SRC_ASSETS


def test_load_sprint_schedule():
    schedule_filename = SRC_ASSETS / "sprint_schedule.json"
    store = SprintScheduleStore()
    store.load_file(schedule_filename)
    assert store.total_count() > 0


def test_get_priority():
    schedule_filename = SRC_ASSETS / "sprint_schedule.json"
    store = SprintScheduleStore()
    assert store.get_priority("R138") == 0

    store.load_file(schedule_filename)
    assert store.get_priority("R140") == 2
