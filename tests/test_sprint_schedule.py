# -*- coding: utf-8 -*-
from pytest import raises
from jira_assistant.sprint_schedule import SprintScheduleStore

from . import ASSETS_FILES


def test_load_sprint_schedule():
    schedule_filename = ASSETS_FILES / "sprint_schedule.json"
    store = SprintScheduleStore()
    store.load_file(schedule_filename)
    assert store.total_count() > 0


def test_get_priority():
    schedule_filename = ASSETS_FILES / "sprint_schedule.json"
    store = SprintScheduleStore()
    assert store.get_priority("R138") == 0

    store.load_file(schedule_filename)
    assert store.get_priority("R140") == 2


def test_load_file_failed():
    with raises(FileNotFoundError) as err:
        SprintScheduleStore().load_file(ASSETS_FILES / "not_exist_file.json")

    assert (
        """Please make sure the sprint schedule file \
exist and the path should be absolute."""
        in err.value.args[0]
    )


def test_load_sprint_schedule_invalid_file():
    schedule_filename = ASSETS_FILES / "sprint_schedule_invalid_key.json"
    store = SprintScheduleStore()
    store.load_file(schedule_filename)
    assert store.total_count() == 2
    assert store.get_priority("R142") == 4
    assert store.get_priority("M126") == 4


def test_load_sprint_schedule_invalid_json():
    with raises(SyntaxError) as err:
        with open(
            ASSETS_FILES / "sprint_schedule_invalid_json.txt",
            mode="r",
            encoding="utf-8",
        ) as file:
            SprintScheduleStore().load(file.read())

    assert (
        """The structure of sprint schedule file is wrong. \
Hint: Expecting property name enclosed in double quotes in line 4:9."""
        in err.value.args[0]
    )
