# -*- coding: utf-8 -*-
import re
from datetime import datetime
from decimal import Decimal
from functools import cmp_to_key
from operator import attrgetter, itemgetter
from typing import Any, Dict, List, Optional, Set, Tuple

from dateutil import parser

from .excel_definition import ExcelDefinitionColumn, SortStrategy
from .milestone import Milestone
from .priority import Priority, convert_to_priority
from .sprint_schedule import SprintScheduleStore
from .utils import standardize_column_name, parse_index_range

__all__ = [
    "Story",
    "StoryFactory",
    "convert_to_bool",
    "convert_to_datetime",
    "convert_to_decimal",
    "sort_stories_by_property_and_order",
    "sort_stories_by_raise_ranking",
    "sort_stories_by_inline_weights",
    "compare_story_based_on_inline_weights",
]


def convert_to_bool(raw: Any) -> bool:
    if isinstance(raw, bool):
        return raw
    value = str(raw).strip().upper()
    if value in ("YES", "TRUE"):
        return True
    return False


def convert_to_decimal(raw: Any) -> Decimal:
    if isinstance(raw, Decimal):
        return raw
    raw = str(raw).strip()
    pattern = re.compile("[0-9.]{1,10}")
    result = pattern.search(raw)
    if result is not None:
        return Decimal(result.group())
    return Decimal(0)


def convert_to_datetime(raw: Any) -> Optional[datetime]:
    if isinstance(raw, datetime):
        return raw
    if raw is None:
        return None
    raw = str(raw).strip()
    return parser.parse(raw)


class Story:
    def __init__(self, factory: "StoryFactory") -> None:
        self.__need_sort = True
        self.__excel_row_index = 0
        if factory is None:
            raise ValueError("Story must be created from a specific factory!")
        self.factory = factory

    @property
    def need_sort(self) -> bool:
        return self.__need_sort

    @need_sort.setter
    def need_sort(self, value: bool):
        self.__need_sort = value

    @property
    def excel_row_index(self) -> int:
        return self.__excel_row_index

    @excel_row_index.setter
    def excel_row_index(self, value: int):
        self.__excel_row_index = value

    def __getitem__(self, property_name: str) -> Any:
        return getattr(self, standardize_column_name(property_name))

    def format_value(self, property_name: str) -> str:
        property_value = getattr(self, standardize_column_name(property_name), None)
        if property_value is None:
            return ""
        if isinstance(property_value, datetime):
            return property_value.date().isoformat()
        if isinstance(property_value, bool):
            if property_value:
                return "Yes"
            return "No"
        if isinstance(property_value, float):
            return str(property_value)
        return str(property_value)

    def set_value(self, property_type: Any, property_name: str, property_value: Any):
        property_name = standardize_column_name(property_name)
        if property_type is str:
            setattr(self, property_name, property_value)
        elif property_type is bool:
            setattr(self, property_name, convert_to_bool(property_value))
        elif property_type is Priority:
            setattr(self, property_name, convert_to_priority(property_value))
        elif property_type is datetime:
            setattr(self, property_name, convert_to_datetime(property_value))
        elif property_type is Milestone:
            milestone = Milestone(property_value)
            setattr(self, property_name, milestone)
        else:
            setattr(self, property_name, property_value)

    def __setitem__(self, property_name, property_value):
        self.set_value(type(property_value), property_name, property_value)

    def calc_sprint_schedule(self, sprint_schedule: SprintScheduleStore):
        for column in self.factory.columns:
            if column["type"] is Milestone and self[column["name"]] is not None:
                self[column["name"]].calc_priority(sprint_schedule)

    # Currently, comparing story only consider the Priority properties.
    def __lt__(self, __o: "Optional[Story]") -> bool:
        raise TypeError("unsupported operand type(s) for comparing story.")

    def __le__(self, __o: "Optional[Story]") -> bool:
        raise TypeError("unsupported operand type(s) for comparing story.")

    def __gt__(self, __o: "Optional[Story]") -> bool:
        raise TypeError("unsupported operand type(s) for comparing story.")

    def __ge__(self, __o: "Optional[Story]") -> bool:
        raise TypeError("unsupported operand type(s) for comparing story.")

    def __eq__(self, __o: "Optional[object]") -> bool:
        raise TypeError("unsupported operand type(s) for comparing story.")

    # For CSV consideration.
    def __str__(self):
        result = ""
        if self is None:
            return result

        separator = ", "
        for column in self.factory.columns:
            if column["name"] is not None and hasattr(self, column["name"]):
                result += f"{str(self[column['name']])}{separator}"
        return result


class StoryFactory:
    def __init__(self, columns: "List[ExcelDefinitionColumn]") -> None:
        if columns is None:
            raise ValueError("Columns must be provided!")
        self.__columns = columns
        self.__inline_weight_compare_rules = (
            self.__generate_inline_weights_compare_rules()
        )

    def __generate_inline_weights_compare_rules(self) -> "List[Tuple[str, int]]":
        rules = []
        for column in self.__columns:
            if column["inline_weights"] > 0:
                rules.append(
                    (
                        standardize_column_name(column["name"]),
                        column["inline_weights"],
                    )
                )
        rules.sort(key=lambda r: r[1], reverse=True)
        return rules

    @property
    def columns(self):
        return self.__columns

    @property
    def inline_weights_compare_rules(self) -> "List[Tuple[str, int]]":
        return self.__inline_weight_compare_rules

    def create_story(self) -> Story:
        return Story(self)


def sort_stories_by_inline_weights(stories: "List[Story]") -> "List[Story]":
    return sorted(
        stories, key=cmp_to_key(compare_story_based_on_inline_weights), reverse=True
    )


def compare_story_based_on_inline_weights(
    story_a: Optional[Story], story_b: Optional[Story]
) -> int:
    """
    Compare two stories.

    parm a:
        First story
    parm b:
        Second story
    parm sort_rule:
        Priority information
    return
        1: means a > b
        0: means a == b
        -1: means a < b
    """
    if story_a is None or story_b is None:
        raise ValueError("The compare stories cannot be None.")

    if (
        story_a.factory != story_b.factory
        or story_a.factory is None
        or story_b.factory is None
    ):
        raise ValueError("The compare stories were built by different factory.")

    # story a and b have the same factory.
    compare_rules: List[Tuple[str, int]] = story_a.factory.inline_weights_compare_rules

    rules_count = len(compare_rules)

    if rules_count == 0:
        return 0

    skip_index_of_a = []
    skip_index_of_b = []
    count = rules_count
    while count > 0:
        # property_value, property_location
        highest_property_of_a = None
        highest_property_of_b = None
        for i, compare_rule in enumerate(compare_rules):
            if i in skip_index_of_a:
                continue

            if highest_property_of_a is None:
                # property_value, property_location
                highest_property_of_a = (story_a[compare_rule[0]], i)

            if story_a[compare_rule[0]] > highest_property_of_a[0]:
                highest_property_of_a = (story_a[compare_rule[0]], i)

        for i, compare_rule in enumerate(compare_rules):
            if i in skip_index_of_b:
                continue

            if highest_property_of_b is None:
                highest_property_of_b = (story_b[compare_rule[0]], i)

            if story_b[compare_rule[0]] > highest_property_of_b[0]:
                highest_property_of_b = (story_b[compare_rule[0]], i)

        if highest_property_of_a is None:
            highest_property_of_a = (Priority.NA, count)
        else:
            skip_index_of_a.append(highest_property_of_a[1])

        if highest_property_of_b is None:
            highest_property_of_b = (Priority.NA, count)
        else:
            skip_index_of_b.append(highest_property_of_b[1])

        # priority value
        if highest_property_of_a[0] > highest_property_of_b[0]:
            return 1
        if highest_property_of_a[0] == highest_property_of_b[0]:
            if highest_property_of_a[1] < highest_property_of_b[1]:
                return 1
            if highest_property_of_a[1] > highest_property_of_b[1]:
                return -1
        else:
            return -1

        # property location
        if highest_property_of_a[1] > highest_property_of_b[1]:
            return 1
        if highest_property_of_a[1] == highest_property_of_b[1]:
            if highest_property_of_a[0] > highest_property_of_b[0]:
                return 1
            if highest_property_of_a[0] < highest_property_of_b[0]:
                return -1
        else:
            return -1

        count -= 1
        continue
    return 0


def sort_stories_by_property_and_order(
    stories: "List[Story]",
    excel_definition_columns: "List[ExcelDefinitionColumn]",
    sort_strategy: Optional[SortStrategy],
):
    sort_rules: List[Tuple[str, bool]] = []
    excel_definition_columns.sort(key=itemgetter("index"), reverse=False)

    parent_scope_index: Optional[Set[int]] = None
    if sort_strategy is not None:
        parent_scope_config = sort_strategy.get_config("ParentScopeIndexRange")
        parent_scope_index = parse_index_range(parent_scope_config)

    if parent_scope_index is not None:
        column_definitions: Dict[int, ExcelDefinitionColumn] = {
            c["index"]: c for c in excel_definition_columns
        }

        for column in excel_definition_columns:
            if column["scope_require_sort"] is True and column["name"] is not None:
                sort_rules.append(
                    (
                        standardize_column_name(column["name"]),
                        column["scope_sort_order"],
                    )
                )

        __internal_sort_stories_by_property_and_order_considering_parent_range(
            stories, column_definitions, sort_rules, parent_scope_index
        )
    else:
        for column in excel_definition_columns:
            if column["require_sort"] is True and column["name"] is not None:
                sort_rules.append(
                    (
                        standardize_column_name(column["name"]),
                        column["sort_order"],
                    )
                )

        __internal_sort_stories_by_property_and_order(stories, sort_rules)


def __internal_sort_stories_by_property_and_order(
    stories: "List[Story]", sort_rules: "List[Tuple[str, bool]]"
):
    for column_name, sort_order in reversed(sort_rules):
        stories.sort(key=attrgetter(column_name), reverse=sort_order)


def __internal_sort_stories_by_property_and_order_considering_parent_range(
    stories: "List[Story]",
    story_columns: "Dict[int, ExcelDefinitionColumn]",
    sort_rules: "List[Tuple[str, bool]]",
    parent_level_index_range: "Set[int]",
) -> "List[Story]":
    """
    Walk through all stories from 0 to N, only sort when
    specified columns are all equaled.
    """
    begin_index = 0
    end_index = 0
    while end_index <= len(stories) - 1:
        for i in range(begin_index, len(stories) - 1):
            all_parent_column_matched = True
            for column_index in parent_level_index_range:
                if (
                    stories[i][
                        standardize_column_name(story_columns[column_index]["name"])
                    ]
                    != stories[i + 1][
                        standardize_column_name(story_columns[column_index]["name"])
                    ]
                ):
                    all_parent_column_matched = False
                    break
            if all_parent_column_matched:
                continue
            end_index = i
            break
        # Same parent level process
        for column_name, sort_order in reversed(sort_rules):
            if begin_index != end_index:
                stories[begin_index: end_index + 1] = sorted(
                    stories[begin_index: end_index + 1],
                    key=attrgetter(column_name),
                    reverse=sort_order,
                )

        begin_index = end_index + 1
        end_index = begin_index

    return stories


def sort_stories_by_raise_ranking(
    stories: "List[Story]",
    excel_definition_columns: "List[ExcelDefinitionColumn]",
    sort_strategy: Optional[SortStrategy],
) -> "List[Story]":
    if stories is None:
        return []
    sort_rules: List[Tuple[str, int]] = []
    excel_definition_columns.sort(key=itemgetter("index"), reverse=False)

    result = []

    # New raise ranking mode.
    parent_scope_index: Optional[Set[int]] = None
    if sort_strategy is not None:
        parent_scope_config = sort_strategy.get_config("ParentScopeIndexRange")
        parent_scope_index = parse_index_range(parent_scope_config)

    if parent_scope_index is not None:
        for column in excel_definition_columns:
            if column["scope_raise_ranking"] > 0 and column["name"] is not None:
                sort_rules.append(
                    (
                        standardize_column_name(column["name"]),
                        column["scope_raise_ranking"],
                    )
                )

        if len(sort_rules) == 0:
            return stories

        sort_rules.sort(key=lambda x: x[1], reverse=True)  # sort by scope_raise_ranking

        column_definitions: Dict[int, ExcelDefinitionColumn] = {
            c["index"]: c for c in excel_definition_columns
        }

        result = __internal_raise_story_ranking_by_property_considering_parent_level(
            stories, column_definitions, sort_rules, parent_scope_index
        )
    else:
        for column in excel_definition_columns:
            if column["raise_ranking"] > 0 and column["name"] is not None:
                sort_rules.append(
                    (
                        standardize_column_name(column["name"]),
                        column["raise_ranking"],
                    )
                )

        if len(sort_rules) == 0:
            return stories

        sort_rules.sort(key=lambda x: x[1], reverse=True)  # sort by raise_ranking

        for property_name, _ in sort_rules:
            result = __internal_raise_story_ranking_by_property(stories, property_name)

    return result


def __internal_raise_story_ranking_by_property(
    stories: "List[Story]", property_name: str
) -> "List[Story]":
    if stories is None or len(stories) == 0:
        return []
    # Use first story as example
    if not hasattr(stories[0], property_name):
        return stories
    return __raise_story_ranking_by_property(stories, property_name)


def __internal_raise_story_ranking_by_property_considering_parent_level(
    stories: "List[Story]",
    story_columns: "Dict[int, ExcelDefinitionColumn]",
    sort_rules: "List[Tuple[str, int]]",
    parent_level_index_range: "Set[int]",
) -> "List[Story]":
    begin_index = 0
    end_index = 0
    while end_index <= len(stories) - 1:
        for i in range(begin_index, len(stories) - 1):
            all_parent_column_matched = True
            for column_index in parent_level_index_range:
                if (
                    stories[i][
                        standardize_column_name(story_columns[column_index]["name"])
                    ]
                    != stories[i + 1][
                        standardize_column_name(story_columns[column_index]["name"])
                    ]
                ):
                    all_parent_column_matched = False
                    break
            if all_parent_column_matched:
                continue
            end_index = i
            break

        # Same parent level process
        for column_name, _ in reversed(sort_rules):
            stories[begin_index: end_index + 1] = __raise_story_ranking_by_property(
                stories[begin_index: end_index + 1], column_name
            )

        begin_index = end_index + 1
        end_index = begin_index

    return stories


# Only bool indicator for now
def __raise_story_ranking_by_property(
    stories: "List[Story]", property_name: str
) -> "List[Story]":
    if not isinstance(getattr(stories[0], property_name), bool):
        return stories
    result: List[Story] = [stories[0]] * len(stories)
    j = 0
    for story in stories:
        if getattr(story, property_name) is True:
            result[j] = story
            j += 1
    for story in stories:
        if getattr(story, property_name) is False:
            result[j] = story
            j += 1
    return result
