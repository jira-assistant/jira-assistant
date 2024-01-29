# -*- coding: utf-8 -*-
from jira_assistant.priority import Priority, convert_to_priority


def test_compare_priority():
    p_1: Priority = Priority.CRITICAL
    p_2: Priority = Priority.HIGH
    p_3: Priority = Priority.HIGH
    p_4: Priority = Priority.MIDDLE
    p_5: Priority = Priority.LOW
    p_6: Priority = Priority.NA

    assert p_1 > p_2
    assert p_2 < p_1
    assert p_2 == p_3
    assert p_3 > p_4
    assert p_4 < p_3
    assert p_4 > p_5
    assert p_5 < p_4
    assert p_5 > p_6
    assert p_5 >= p_6
    assert p_6 < p_5
    assert p_6 <= p_5


def test_priority_to_str():
    p_1: Priority = Priority.CRITICAL
    p_2: Priority = Priority.NA
    assert str(p_1) == "Critical"
    assert str(p_2) == "N/A"


def test_convert_to_priority():
    assert convert_to_priority("CRITICAL") == Priority.CRITICAL
    assert convert_to_priority("LOW") == Priority.LOW
    assert convert_to_priority("MIDDLE") == Priority.MIDDLE
    assert convert_to_priority("HIGH") == Priority.HIGH
    assert convert_to_priority(None) == Priority.NA
