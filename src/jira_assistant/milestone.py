# -*- coding: utf-8 -*-
"""
Milestone: 2 weeks                                           2022/1/10
Milestone Start Date
Release: 5 weeks (S1 2 weeks S2 2 weeks Harden 1 week)       2022/1/10
S1 Start Date 
S2 Start Date
"""


from typing import Any

from .sprint_schedule import SprintScheduleStore

__all__ = ["Milestone"]


class Milestone:
    # __init__ method cannot have class method attribute!
    # Otherwise, all instance will point to the same one.
    def __init__(self, raw: Any) -> None:
        self.__raw: str = raw
        self.__sprint = self.__raw
        self.__priority = 0

    @property
    def priority(self) -> int:
        return self.__priority

    @priority.setter
    def priority(self, value: int):
        self.__priority = value

    def calc_priority(self, sprint_schedule: SprintScheduleStore) -> None:
        if self.__sprint is None:
            self.priority = 0
        else:
            self.priority = sprint_schedule.get_priority(self.__sprint)

    def __str__(self) -> str:
        if self.__raw is None:
            return ""
        return self.__raw

    def __lt__(self, __o: "Milestone") -> bool:
        if self.priority < __o.priority:
            return True
        return False

    def __gt__(self, __o: "Milestone") -> bool:
        if self.priority > __o.priority:
            return True
        return False

    def __le__(self, __o: "Milestone") -> bool:
        if self.priority <= __o.priority:
            return True
        return False

    def __ge__(self, __o: "Milestone") -> bool:
        if self.priority >= __o.priority:
            return True
        return False

    def __eq__(self, __o: "object") -> bool:
        if isinstance(__o, Milestone):
            if self.priority == __o.priority:
                return True
        return False
