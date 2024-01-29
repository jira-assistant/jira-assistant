# -*- coding: utf-8 -*-
from enum import IntEnum
from typing import Any

__all__ = ["Priority", "convert_to_priority"]


class Priority(IntEnum):
    CRITICAL = 5
    HIGH = 4
    MIDDLE = 3
    LOW = 2
    NA = 1

    def __str__(self) -> str:
        if self is None or self.name == "NA":
            return "N/A"
        return self.name.capitalize()

    def __lt__(self, __o: "object") -> bool:
        left = -1
        if isinstance(self.value, int):
            left = self.value
        right = -1
        if isinstance(__o, int):
            right = __o

        if left < right:
            return True
        return False

    def __gt__(self, __o: "object") -> bool:
        left = -1
        if isinstance(self.value, int):
            left = self.value
        right = -1
        if isinstance(__o, int):
            right = __o

        if left > right:
            return True
        return False

    def __le__(self, __o: "object") -> bool:
        left = -1
        if isinstance(self.value, int):
            left = self.value
        right = -1
        if isinstance(__o, int):
            right = __o

        if left <= right:
            return True
        return False

    def __ge__(self, __o: "object") -> bool:
        left = -1
        if isinstance(self.value, int):
            left = self.value
        right = -1
        if isinstance(__o, int):
            right = __o

        if left >= right:
            return True
        return False

    def __eq__(self, __o: "object") -> bool:
        if self.value == __o:
            return True
        return False


def convert_to_priority(raw: Any) -> Priority:
    if raw is None:
        return Priority.NA
    if isinstance(raw, Priority):
        return raw
    value = str(raw).strip().upper()
    if value in ("N/A", "NA"):
        return Priority.NA
    if value == "LOW":
        return Priority.LOW
    if value in ("MEDIUM", "MIDDLE"):
        return Priority.MIDDLE
    if value == "HIGH":
        return Priority.HIGH
    if value == "CRITICAL":
        return Priority.CRITICAL
    return Priority.NA
