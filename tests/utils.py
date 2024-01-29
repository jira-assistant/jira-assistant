# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List, Tuple

from jira_assistant.excel_definition import ExcelDefinition, ExcelDefinitionColumn
from jira_assistant.excel_operation import read_excel_file
from jira_assistant.priority import Priority
from jira_assistant.sprint_schedule import SprintScheduleStore
from jira_assistant.story import Story, StoryFactory

_MOCK_STORY_FACTORY = StoryFactory(
    [
        ExcelDefinitionColumn(
            index=1,
            name="name",
            type=str,
            require_sort=False,
            sort_order=False,
            inline_weights=0,
            raise_ranking=0,
            scope_raise_ranking=0,
            scope_require_sort=False,
            scope_sort_order=True,
            jira_field_mapping=None,
            query_jira_info=True,
            update_jira_info=True,
        ),
        ExcelDefinitionColumn(
            index=3,
            name="regulatory",
            type=Priority,
            require_sort=True,
            sort_order=True,
            inline_weights=5,
            raise_ranking=0,
            scope_raise_ranking=0,
            scope_require_sort=True,
            scope_sort_order=True,
            jira_field_mapping=None,
            query_jira_info=True,
            update_jira_info=True,
        ),
        ExcelDefinitionColumn(
            index=2,
            name="partnerPriority",
            type=Priority,
            require_sort=True,
            sort_order=True,
            inline_weights=4,
            raise_ranking=0,
            scope_raise_ranking=0,
            scope_require_sort=True,
            scope_sort_order=True,
            jira_field_mapping=None,
            query_jira_info=True,
            update_jira_info=True,
        ),
        ExcelDefinitionColumn(
            index=6,
            name="productValue",
            type=Priority,
            require_sort=True,
            sort_order=True,
            inline_weights=3,
            raise_ranking=0,
            scope_raise_ranking=0,
            scope_require_sort=True,
            scope_sort_order=True,
            jira_field_mapping=None,
            query_jira_info=True,
            update_jira_info=True,
        ),
        ExcelDefinitionColumn(
            index=5,
            name="marketingUrgency",
            type=Priority,
            require_sort=True,
            sort_order=True,
            inline_weights=2,
            raise_ranking=0,
            scope_raise_ranking=2,
            scope_require_sort=True,
            scope_sort_order=True,
            jira_field_mapping=None,
            query_jira_info=True,
            update_jira_info=True,
        ),
        ExcelDefinitionColumn(
            index=4,
            name="revenue",
            type=Priority,
            require_sort=True,
            sort_order=True,
            inline_weights=1,
            raise_ranking=0,
            scope_raise_ranking=1,
            scope_require_sort=True,
            scope_sort_order=True,
            jira_field_mapping=None,
            query_jira_info=True,
            update_jira_info=True,
        ),
        ExcelDefinitionColumn(
            index=7,
            name="raiseRankingTest",
            type=Priority,
            require_sort=False,
            sort_order=False,
            inline_weights=0,
            raise_ranking=1,
            scope_raise_ranking=0,
            scope_require_sort=False,
            scope_sort_order=False,
            jira_field_mapping=None,
            query_jira_info=False,
            update_jira_info=False,
        ),
    ]
)


def mock_story_data() -> Tuple[List[Story], StoryFactory]:
    # NA, Middle, Middle, NA
    s_1 = _MOCK_STORY_FACTORY.create_story()
    s_1["name"] = "s1"
    s_1["regulatory"] = Priority.NA
    s_1["partnerPriority"] = Priority.MIDDLE
    s_1["productValue"] = Priority.MIDDLE
    s_1["marketingUrgency"] = Priority.NA
    s_1["revenue"] = Priority.NA
    # NA, Low, High, NA
    s_2 = _MOCK_STORY_FACTORY.create_story()
    s_2["name"] = "s2"
    s_2["regulatory"] = Priority.NA
    s_2["partnerPriority"] = Priority.LOW
    s_2["productValue"] = Priority.HIGH
    s_2["marketingUrgency"] = Priority.NA
    s_2["revenue"] = Priority.NA
    # NA, Middle, High, NA
    s_3 = _MOCK_STORY_FACTORY.create_story()
    s_3["name"] = "s3"
    s_3["regulatory"] = Priority.NA
    s_3["partnerPriority"] = Priority.MIDDLE
    s_3["productValue"] = Priority.HIGH
    s_3["marketingUrgency"] = Priority.NA
    s_3["revenue"] = Priority.NA
    # NA, High, High, NA
    s_4 = _MOCK_STORY_FACTORY.create_story()
    s_4["name"] = "s4"
    s_4["regulatory"] = Priority.NA
    s_4["partnerPriority"] = Priority.HIGH
    s_4["productValue"] = Priority.HIGH
    s_4["marketingUrgency"] = Priority.NA
    s_4["revenue"] = Priority.NA
    # High, NA, High, NA
    s_5 = _MOCK_STORY_FACTORY.create_story()
    s_5["name"] = "s5"
    s_5["regulatory"] = Priority.HIGH
    s_5["partnerPriority"] = Priority.NA
    s_5["productValue"] = Priority.HIGH
    s_5["marketingUrgency"] = Priority.NA
    s_5["revenue"] = Priority.NA

    # Critical, N/A, Middle, N/A
    s_6 = _MOCK_STORY_FACTORY.create_story()
    s_6["name"] = "s6"
    s_6["regulatory"] = Priority.CRITICAL
    s_6["partnerPriority"] = Priority.NA
    s_6["productValue"] = Priority.MIDDLE
    s_6["marketingUrgency"] = Priority.NA
    s_6["revenue"] = Priority.NA

    # Critical, N/A, High, Low
    s_7 = _MOCK_STORY_FACTORY.create_story()
    s_7["name"] = "s7"
    s_7["regulatory"] = Priority.CRITICAL
    s_7["partnerPriority"] = Priority.NA
    s_7["productValue"] = Priority.HIGH
    s_7["marketingUrgency"] = Priority.LOW
    s_7["revenue"] = Priority.NA

    # Critical, Low, Middle, N/A
    s_8 = _MOCK_STORY_FACTORY.create_story()
    s_8["name"] = "s8"
    s_8["regulatory"] = Priority.CRITICAL
    s_8["partnerPriority"] = Priority.LOW
    s_8["productValue"] = Priority.MIDDLE
    s_8["marketingUrgency"] = Priority.NA
    s_8["revenue"] = Priority.NA

    # Critical, Middle, High, Middle
    s_9 = _MOCK_STORY_FACTORY.create_story()
    s_9["name"] = "s9"
    s_9["regulatory"] = Priority.CRITICAL
    s_9["partnerPriority"] = Priority.MIDDLE
    s_9["productValue"] = Priority.HIGH
    s_9["marketingUrgency"] = Priority.MIDDLE
    s_9["revenue"] = Priority.NA

    return ([s_1, s_2, s_3, s_4, s_5, s_6, s_7, s_8, s_9], _MOCK_STORY_FACTORY)


def mock_story_data_for_property_sorting() -> Tuple[List[Story], StoryFactory]:
    # Name, PartnerPriority, Regulatory, Revenue, MarketingUrgency, ProductValue

    # Middle, Middle, Middle, Low, Middle
    s_1 = _MOCK_STORY_FACTORY.create_story()
    s_1["name"] = "s1"
    s_1["partnerPriority"] = Priority.MIDDLE
    s_1["regulatory"] = Priority.MIDDLE
    s_1["revenue"] = Priority.MIDDLE
    s_1["marketingUrgency"] = Priority.LOW
    s_1["productValue"] = Priority.MIDDLE
    # Middle, Middle, High, NA, High
    s_2 = _MOCK_STORY_FACTORY.create_story()
    s_2["name"] = "s2"
    s_2["partnerPriority"] = Priority.MIDDLE
    s_2["regulatory"] = Priority.MIDDLE
    s_2["revenue"] = Priority.HIGH
    s_2["marketingUrgency"] = Priority.NA
    s_2["productValue"] = Priority.HIGH

    return ([s_1, s_2], _MOCK_STORY_FACTORY)


def mock_story_data_for_property_sorting_consider_parent_index() -> (
    Tuple[List[Story], StoryFactory]
):
    # Name, PartnerPriority, Regulatory, Revenue, MarketingUrgency, ProductValue

    # Middle, Middle, High, Middle, Low
    s_1 = _MOCK_STORY_FACTORY.create_story()
    s_1["name"] = "s1"
    s_1["partnerPriority"] = Priority.MIDDLE
    s_1["regulatory"] = Priority.MIDDLE
    s_1["revenue"] = Priority.HIGH
    s_1["marketingUrgency"] = Priority.MIDDLE
    s_1["productValue"] = Priority.LOW
    # Middle, High, Low, Middle, Middle
    s_2 = _MOCK_STORY_FACTORY.create_story()
    s_2["name"] = "s2"
    s_2["partnerPriority"] = Priority.MIDDLE
    s_2["regulatory"] = Priority.HIGH
    s_2["revenue"] = Priority.LOW
    s_2["marketingUrgency"] = Priority.MIDDLE
    s_2["productValue"] = Priority.MIDDLE

    return ([s_1, s_2], _MOCK_STORY_FACTORY)


def mock_story_data_for_raise_ranking():
    # Name, PartnerPriority, Regulatory, Revenue, MarketingUrgency, ProductValue

    # Middle, Middle, High, Middle, Low
    s_1 = _MOCK_STORY_FACTORY.create_story()
    s_1["name"] = "s1"
    s_1["partnerPriority"] = Priority.MIDDLE
    s_1["regulatory"] = Priority.MIDDLE
    s_1["revenue"] = Priority.HIGH
    s_1["marketingUrgency"] = Priority.MIDDLE
    s_1["productValue"] = Priority.LOW
    s_1["raiseRankingTest"] = False
    # Middle, High, Low, Middle, Middle
    s_2 = _MOCK_STORY_FACTORY.create_story()
    s_2["name"] = "s2"
    s_2["partnerPriority"] = Priority.MIDDLE
    s_2["regulatory"] = Priority.HIGH
    s_2["revenue"] = Priority.LOW
    s_2["marketingUrgency"] = Priority.MIDDLE
    s_2["productValue"] = Priority.MIDDLE
    s_2["raiseRankingTest"] = True

    return ([s_1, s_2], _MOCK_STORY_FACTORY)


def read_stories_from_excel(
    excel_file: Path, excel_definition_file: Path, sprint_schedule_file: Path
) -> Tuple[List[str], List[Story]]:
    excel_definition = ExcelDefinition()
    excel_definition.load_file(excel_definition_file)
    sprint_schedule = SprintScheduleStore()
    sprint_schedule.load_file(sprint_schedule_file)

    columns, stories = read_excel_file(excel_file, excel_definition, sprint_schedule)

    return (columns, stories)
