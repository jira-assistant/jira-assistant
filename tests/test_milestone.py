
# -*- coding: utf-8 -*-
from pytest import raises

from jira_assistant.milestone import Milestone
from jira_assistant.sprint_schedule import SprintScheduleStore

from . import SRC_ASSETS


def test_init():
    schedule_filename = SRC_ASSETS / "sprint_schedule.json"
    store = SprintScheduleStore()
    store.load_file(schedule_filename)

    milestone = Milestone("R139")
    milestone.calc_priority(store)
    assert milestone.priority == 1


def test_compare():
    schedule_filename = SRC_ASSETS / "sprint_schedule.json"
    store = SprintScheduleStore()
    store.load_file(schedule_filename)

    m_1 = Milestone("M123")
    m_1.calc_priority(store)
    m_2 = Milestone("M125")
    m_2.calc_priority(store)
    m_3 = Milestone("m125")
    m_3.calc_priority(store)
    m_4 = Milestone("R141")
    m_4.calc_priority(store)
    assert m_1 < m_2
    with raises(AssertionError):
        assert m_1 > m_2
    assert m_1 <= m_2
    with raises(AssertionError):
        assert m_1 >= m_2
    assert m_2 >= m_1
    assert m_2 == m_3
    assert m_3 == m_4
    assert m_4 > m_1
    with raises(AssertionError):
        assert m_1 == m_4


def test_str():
    m_1 = Milestone(None)

    assert len(str(m_1)) == 0
