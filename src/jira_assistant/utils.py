# -*- coding: utf-8 -*-
from __future__ import annotations

import re

from pathlib import Path
from typing import Dict, Union, Set, Optional

_INDEX_RANGE_RULE = re.compile(
    r"(^( *\d+ *,)* *\d+ *$)|^ *\d+ *- *\d+ *$"
)


def is_absolute_path_valid(path: Union[str, Path]) -> bool:
    if path is None or not Path(path).is_absolute() or not Path(path).exists():
        return False
    return True


def standardize_column_name(name: str) -> "str":
    return strip_lower(name.replace("\n", "").replace(" ", ""))


def strip_lower(statement: str) -> "str":
    return statement.strip().lower()


def is_index_range_valid(statement: Optional[str]) -> bool:
    if (
        statement is None
        or not statement.strip()
        or _INDEX_RANGE_RULE.fullmatch(statement) is None
    ):
        return False
    return True


def parse_index_range(statement: Optional[str]) -> "Optional[Set[int]]":
    if statement is None or not is_index_range_valid(statement):
        return None
    if "-" in statement:
        begin = int(statement.split("-")[0])
        end = int(statement.split("-")[1])
        if begin < end:
            return set(i for i in range(begin, end + 1))
        return set(i for i in range(end, begin + 1))
    return set(int(i) for i in statement.split(","))


def dict_has_key(dictionary: Dict, key: str) -> bool:
    if strip_lower(key) in [strip_lower(i) for i in dictionary.keys()]:
        return True
    return False
