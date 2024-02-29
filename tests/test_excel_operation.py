# -*- coding: utf-8 -*-
import pathlib

import pytest

from jira_assistant.excel_definition import ExcelDefinition
from jira_assistant.excel_operation import output_to_excel_file, read_excel_file
from jira_assistant.sprint_schedule import SprintScheduleStore
from tests.utils import read_stories_from_excel

from . import ASSETS_FILES, SRC_ASSETS


def test_read_excel_file():
    excel_definition = ExcelDefinition()
    excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
    sprint_schedule = SprintScheduleStore()
    sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

    columns, stories = read_excel_file(
        ASSETS_FILES / "excel.xlsx", excel_definition, sprint_schedule
    )
    assert len(columns) == 29
    assert len(stories) == 8


def test_read_excel_file_duplicate_column():
    excel_definition = ExcelDefinition()
    excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
    sprint_schedule = SprintScheduleStore()
    sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

    with pytest.raises(ValueError) as e:
        _, _ = read_excel_file(
            ASSETS_FILES / "excel_duplicate_column.xlsx",
            excel_definition,
            sprint_schedule,
        )

    assert "The input excel file has duplicate column." in str(e.value)


def test_read_excel_file_empty_row():
    excel_definition = ExcelDefinition()
    excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
    sprint_schedule = SprintScheduleStore()
    sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

    columns, stories = read_excel_file(
        ASSETS_FILES / "excel_with_empty_row.xlsx",
        excel_definition,
        sprint_schedule,
    )

    assert len(columns) == 29
    assert len(stories) == 2


def test_read_excel_file_missing_columns():
    excel_definition = ExcelDefinition()
    excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
    sprint_schedule = SprintScheduleStore()
    sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

    with pytest.raises(ValueError) as e:
        _, _ = read_excel_file(
            ASSETS_FILES / "excel_missing_columns.xlsx",
            excel_definition,
            sprint_schedule,
        )
    assert "Following columns are missing:" in str(e.value)
    assert "1.criticalDefect" in str(e.value)
    assert "3.partnerPriority" in str(e.value)


def test_output_to_excel_file(tmpdir):
    columns, stories = read_stories_from_excel(
        ASSETS_FILES / "excel.xlsx",
        SRC_ASSETS / "excel_definition.json",
        SRC_ASSETS / "sprint_schedule.json",
    )

    output_to_excel_file(tmpdir / "excel_direct_output.xlsx", stories, columns)

    assert (tmpdir / "excel_direct_output.xlsx").exists()


def test_output_to_excel_file_path_is_not_absolute():
    with pytest.raises(ValueError) as e:
        output_to_excel_file("excel_direct_output.xlsx", [], [])

    assert "The output file path is invalid." in str(e.value)


def test_output_to_excel_file_path_already_exist_over_write_is_true(tmpdir):
    columns, stories = read_stories_from_excel(
        ASSETS_FILES / "excel.xlsx",
        SRC_ASSETS / "excel_definition.json",
        SRC_ASSETS / "sprint_schedule.json",
    )

    output_file = tmpdir / "excel_direct_output.xlsx"

    pathlib.Path(output_file).resolve().touch()

    output_to_excel_file(
        output_file,
        stories,
        columns,
        over_write=True,
    )

    assert output_file.exists()


def test_output_to_excel_file_path_already_exist_over_write_is_false(tmpdir):
    output_file = tmpdir / "excel_direct_output.xlsx"

    pathlib.Path(output_file).resolve().touch()

    with pytest.raises(FileExistsError) as e:
        output_to_excel_file(
            output_file,
            [],
            [],
            over_write=False,
        )

    assert "already exist." in str(e.value)
